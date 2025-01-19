from typing import Optional, List, Dict, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import asyncio
import aiohttp
from docgen.auth.api_key_manager import APIKeyManager
import time

class AIClient:
    def __init__(self):
        # Server pool configuration
        self.base_urls = [
            f"http://localhost:{port}" 
            for port in range(8000, 8012)  # Ports 8000-8011
        ]
        self.api_key_manager = APIKeyManager()
        
        # Configure session with connection pooling
        self.session = self._create_session()
        
        # Async session for concurrent requests
        self._async_session = None
        self._semaphore = asyncio.Semaphore(10)  # Limit concurrent connections
        
        # Rate limiting
        self._request_times = []
        self._rate_limit_lock = asyncio.Lock()
        self.RATE_LIMIT_REQUESTS = 15  # Gemini's limit
        self.RATE_LIMIT_WINDOW = 60    # Window in seconds
        
        self.MAX_BATCH_SIZE = 10  # Maximum files per batch
        self.MAX_BATCH_TOKENS = 30000  # Approximate token limit per batch
        
    def _create_session(self) -> requests.Session:
        """Create an optimized session with connection pooling."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        return session

    async def _ensure_async_session(self):
        """Ensure async session exists."""
        if self._async_session is None:
            connector = aiohttp.TCPConnector(limit=20)
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
        
        # Wait for rate limit if necessary
        await self._wait_for_rate_limit()
        
        async with self._semaphore:
            for _ in range(2):  # Retry up to 3 times
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
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("text")
                        elif response.status == 401:
                            raise ValueError("Rate limit exceeded")
                        elif response.status == 429:  # Too Many Requests
                            # Wait longer for rate limit
                            await asyncio.sleep(5)
                            continue
                except Exception as e:
                    print(f"Request failed: {str(e)}")
                    continue
        return None

    def _estimate_tokens(self, code: str) -> int:
        """Rough estimation of tokens in code."""
        return len(code.split())
        
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
            for _ in range(2):  # Retry up to 3 times
                server_url = self._get_random_server()
                try:
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
                            return data.get("texts", [])
                        elif response.status == 429:  # Too Many Requests
                            await asyncio.sleep(5)
                            continue
                except Exception as e:
                    print(f"Batch request failed: {str(e)}")
                    continue
        return [None] * len(batch)

    async def generate_text_batch(self, requests: List[Dict]) -> List[Optional[str]]:
        """Generate text for multiple requests using batching."""
        batches = self._create_batches(requests)
        results = []
        
        for batch in batches:
            batch_results = await self._make_batch_request(batch)
            results.extend(batch_results)
            
            # Wait between batches to respect rate limits
            if len(batches) > 1:
                await asyncio.sleep(1)  # Adjust based on your rate limits
                
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
        """Generate documentation updates for multiple files using batching."""
        try:
            # Prepare batch requests
            requests = [
                {
                    'code': code,
                    'changes': changes,
                    'prompt_type': 'update'
                }
                for _, _, code, changes in files_data
            ]
            
            # Process in optimized batches
            batches = self._create_batches(requests)
            all_results = []
            
            for batch in batches:
                batch_results = await self._make_batch_request(batch)
                all_results.extend(batch_results)
                
                # Wait between batches if needed
                if len(batches) > 1:
                    await asyncio.sleep(1)
            
            # Map results back to files
            results = {}
            for (path, _, _, _), result in zip(files_data, all_results):
                if result is not None:
                    results[path] = result
                else:
                    results[path] = "Error: Failed to generate documentation"
            
            return results
            
        except Exception as e:
            print(f"Batch update generation failed: {str(e)}")
            return {
                path: f"Error: {str(e)}" 
                for path, _, _, _ in files_data
            }
        finally:
            await self.close() 