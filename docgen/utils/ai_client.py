from typing import Optional, List, Dict, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import asyncio
import aiohttp
from docgen.auth.api_key_manager import APIKeyManager
import time
import hashlib
from pathlib import Path
import json
from datetime import datetime, timedelta
from docgen.config.urls import URLConfig


class AIClient:
    def __init__(self):
        # Server pool configuration
        self.base_urls = URLConfig.SERVER_URLS
        self.api_key_manager = APIKeyManager()
        
        # Configure session with connection pooling
        self.session = self._create_session()
        
        # Async session for concurrent requests
        self._async_session = None
        self._semaphore = asyncio.Semaphore(50)  # Increased from 10 to 50
        
        # Rate limiting - Adjusted for better throughput
        self._request_times = []
        self._rate_limit_lock = asyncio.Lock()
        self.RATE_LIMIT_REQUESTS = 15  # Gemini's limit
        self.RATE_LIMIT_WINDOW = 60    # Window in seconds
        
        # Larger batches for fewer total requests
        self.MAX_BATCH_SIZE = 1000        # Increased significantly
        self.MAX_BATCH_TOKENS = 1000000  # Doubled token limit
        
        # Add cache initialization
        self.cache_dir = Path.home() / '.docgen' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=1)  # Cache expires after 7 days

    def _create_session(self) -> requests.Session:
        """Create an optimized session with connection pooling."""
        session = requests.Session()
        
        # Configure retry strategy with faster retries
        retry_strategy = Retry(
            total=2,  # Reduced from 3
            backoff_factor=0.05,  # Reduced from 0.1
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Increased pool size
        adapter = HTTPAdapter(
            pool_connections=50,  # Increased from 20
            pool_maxsize=50,      # Increased from 20
            max_retries=retry_strategy,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        return session

    async def _ensure_async_session(self):
        """Ensure async session exists."""
        if self._async_session is None:
            connector = aiohttp.TCPConnector(limit=50)  # Increased from 20
            self._async_session = aiohttp.ClientSession(connector=connector)

    def _get_random_server(self) -> str:
        """Get a random server URL from the pool."""
        return random.choice(self.base_urls)

    async def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits."""
        async with self._rate_limit_lock:
            current_time = time.time()
            
            # Remove requests older than the window
            self._request_times = [t for t in self._request_times 
                                 if current_time - t < self.RATE_LIMIT_WINDOW]
            
            if len(self._request_times) >= self.RATE_LIMIT_REQUESTS:
                # Calculate wait time
                oldest_request = min(self._request_times)
                wait_time = oldest_request + self.RATE_LIMIT_WINDOW - current_time
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Clear old requests after waiting
                    self._request_times = []
            
            # Add current request
            self._request_times.append(current_time)

    async def _make_request(self, code: str, changes: Optional[str] = None, prompt_type: str = 'doc') -> Optional[str]:
        """Make an async request to the AI server."""
        await self._ensure_async_session()
        api_key = self.api_key_manager.get_api_key()
        
        await self._wait_for_rate_limit()
        
        async with self._semaphore:
            for _ in range(1):  # Reduced retries from 2 to 1 for faster failure
                server_url = self._get_random_server()
                try:
                    async with self._async_session.post(
                        f"{server_url}/api/v1/gemini/generate",
                        json={
                            "code": code,
                            "changes": changes,
                            "prompt_type": prompt_type,
                            "api_key": api_key
                        },
                        timeout=aiohttp.ClientTimeout(total=15)  # Reduced from 30
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("text")
                        elif response.status == 401:
                            raise ValueError("Rate limit exceeded")
                        elif response.status == 429:
                            await asyncio.sleep(1)  # Reduced from 5
                            continue
                except Exception as e:
                    print(f"Request failed: {str(e)}")
                    continue
        return None

    def _estimate_tokens(self, code: str) -> int:
        """Rough estimation of tokens in code.
        Uses the same estimation as server: 4 characters per token."""
        return len(code) // 4
        
    def _create_batches(self, requests: List[Dict]) -> List[List[Dict]]:
        """Create optimal batches based on file sizes."""
        batches = []
        current_batch = []
        current_tokens = 0
        
        for req in requests:
            tokens = self._estimate_tokens(req['code'])
            
            # Start new batch if current would exceed limits
            if (len(current_batch) >= self.MAX_BATCH_SIZE or 
                current_tokens + tokens > self.MAX_BATCH_TOKENS):
                if current_batch:
                    batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            current_batch.append(req)
            current_tokens += tokens
            
        if current_batch:
            batches.append(current_batch)
            
        return batches

    async def _make_batch_request(self, batch: List[Dict]) -> List[Optional[str]]:
        """Make a batch request to the AI server."""
        await self._ensure_async_session()
        api_key = self.api_key_manager.get_api_key()
        
        await self._wait_for_rate_limit()
        
        async with self._semaphore:
            try:
                server_url = self._get_random_server()
                async with self._async_session.post(
                    f"{server_url}/api/v1/gemini/generate/batch",
                    json={
                        "files": batch,
                        "api_key": api_key
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("texts", [])
                        
                        # Debug logging
                        # print(f"Batch details:")
                        # print(f"Input batch size: {len(batch)}")
                        # print(f"Response size: {len(results)}")
                        
                        # Always ensure we return exactly the number of results we requested
                        if len(results) > len(batch):
                            # print(f"Trimming extra result from server")
                            results = results[:len(batch)]
                        elif len(results) < len(batch):
                            # print(f"Padding missing results")
                            results.extend([None] * (len(batch) - len(results)))
                            
                        return results
                        
            except Exception as e:
                print(f"Batch request failed: {str(e)}")
            return [None] * len(batch)

    def _fast_cache_key(self, code: str, analysis: Dict, operation: str = 'generate') -> str:
        """Generate cache key based on code content and operation type."""
        # Include first 100 chars of code, class/function names, and operation type
        key_content = (
            f"{code[:100]}"
            f"{str(analysis.get('classes', []))}"
            f"{str(analysis.get('functions', []))}"
            f"{operation}"  # Add operation type to differentiate generate vs update
        )
        return hashlib.md5(key_content.encode()).hexdigest()

    async def generate_text_batch(self, requests: List[Dict]) -> List[Optional[str]]:
        """Generate text for multiple requests using batching with caching."""
        results = []
        uncached_requests = []
        request_mapping = {}  # Map batch indices to original indices
        
        # Check cache first
        for i, req in enumerate(requests):
            cache_key = self._fast_cache_key(
                req['code'], 
                req.get('analysis', {}),
                'generate'
            )
            cached_doc = self._get_cached_doc(cache_key)
            if cached_doc:
                results.append(cached_doc)
            else:
                uncached_requests.append(req)
                request_mapping[len(uncached_requests) - 1] = i
        
        if uncached_requests:
            # Process uncached requests in batches
            batches = self._create_batches(uncached_requests)
            
            async def process_batch(batch):
                return await self._make_batch_request(batch)
            
            # Create tasks for all batches
            tasks = [process_batch(batch) for batch in batches]
            batch_results = await asyncio.gather(*tasks)
            
            # Process and cache results
            flat_results = []
            for batch_result in batch_results:
                flat_results.extend(batch_result)
            
            # Cache new results and insert them in correct positions
            final_results = results.copy()
            for i, result in enumerate(flat_results):
                if result:
                    orig_idx = request_mapping[i]
                    cache_key = self._fast_cache_key(
                        uncached_requests[i]['code'],
                        uncached_requests[i].get('analysis', {}),
                        'generate'
                    )
                    self._save_to_cache(cache_key, result)
                    while len(final_results) <= orig_idx:
                        final_results.append(None)
                    final_results[orig_idx] = result
            
            return final_results
        
        return results

    async def generate_text(self, code: str, changes: Optional[str] = None, prompt_type: str = 'doc') -> Optional[str]:
        """Generate text using AI through the proxy server."""
        try:
            return await self._make_request(code, changes, prompt_type)
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return None

    async def close(self):
        """Close the async session."""
        if self._async_session:
            await self._async_session.close() 

    async def generate_update_documentation_batch(self, files_data: List[Tuple[str, Dict, str, str]]) -> Dict[str, str]:
        """Generate documentation updates with caching."""
        try:
            results = {}
            uncached_files = []
            
            # Check cache first
            for path, analysis, code, changes in files_data:
                if not changes.strip():
                    continue
                    
                cache_key = self._fast_cache_key(
                    changes+code,  # Include changes in cache key for updates
                    analysis,
                    'update'
                )
                cached_doc = self._get_cached_doc(cache_key)
                
                if cached_doc:
                    results[path] = cached_doc
                else:
                    uncached_files.append((path, analysis, code, changes))
            
            if uncached_files:
                # Process uncached files
                requests = [
                    {
                        'code': code,
                        'changes': changes,
                        'prompt_type': 'update',
                        'file_path': path
                    }
                    for path, _, code, changes in uncached_files
                ]
                
                batches = self._create_batches(requests)
                
                async def process_batch(batch):
                    return await self._make_batch_request(batch)
                
                tasks = [process_batch(batch) for batch in batches]
                batch_results = await asyncio.gather(*tasks)
                
                # Process and cache new results
                all_results = []
                for batch_result in batch_results:
                    all_results.extend(batch_result)
                
                for (path, analysis, code, changes), result in zip(uncached_files, all_results):
                    if result:
                        cache_key = self._fast_cache_key(
                            changes+code,
                            analysis,
                            'update'
                        )
                        self._save_to_cache(cache_key, result)
                        results[path] = result
                    else:
                        results[path] = "Error: Failed to generate documentation"
            
            return results
            
        except Exception as e:
            print(f"Batch update generation failed: {str(e)}")
            return {path: f"Error: {str(e)}" for path, _, _, _ in files_data}
        finally:
            await self.close() 

    def _get_cached_doc(self, cache_key: str) -> Optional[str]:
        """Retrieve cached documentation if it exists and is valid."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if not cache_file.exists():
                return None
                
            cache_data = json.loads(cache_file.read_text())
            # Check if cache data has the expected structure
            if not isinstance(cache_data, dict) or 'content' not in cache_data or 'timestamp' not in cache_data:
                # Invalid cache data, remove it
                cache_file.unlink()
                return None
                
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            
            # Check if cache is still valid
            if datetime.now() - cached_time <= self.cache_duration:
                return cache_data.get('content')
            
            # Remove expired cache
            cache_file.unlink()
            return None
            
        except Exception as e:
            # If there's an error, clean up the corrupted cache file
            try:
                if cache_file.exists():
                    cache_file.unlink()
            except:
                pass
            print(f"Cache read error for key {cache_key}: {str(e)}")
            return None

    def _save_to_cache(self, cache_key: str, content: str) -> None:
        """Save documentation to cache."""
        try:
            if not content or not isinstance(content, str):
                return  # Don't cache invalid content
                
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_data = {
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'  # Adding version for future compatibility
            }
            
            # Write to temporary file first
            temp_file = cache_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2))
            
            # Then rename to final filename (atomic operation)
            temp_file.replace(cache_file)
            
        except Exception as e:
            print(f"Cache write error for key {cache_key}: {str(e)}")
            # Clean up temporary file if it exists
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass

    def _clear_cache(self) -> None:
        """Clear all cached documentation."""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
        except Exception as e:
            print(f"Cache clear error: {str(e)}") 

    async def _track_usage(self, request_type: str = 'generate') -> None:
        """Track API usage."""
        try:
            headers = {
                'x-machine-id': self.api_key_manager.machine_id,
                'x-api-key': self.api_key_manager.get_api_key()
            }
            
            async with self._async_session.post(
                f"{URLConfig.USAGE_BASE_URL}/track",
                headers=headers,
                json={'request_type': request_type},  # Send as JSON body
                timeout=10
            ) as response:
                if response.status != 200:
                    print(f"Warning: Failed to track usage (status: {response.status})")
        except Exception as e:
            print(f"Warning: Could not track usage: {str(e)}") 