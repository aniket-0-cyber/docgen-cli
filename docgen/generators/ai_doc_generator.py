from rich.console import Console
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import hashlib
from datetime import datetime
import multiprocessing
import time
from ratelimit import limits, sleep_and_retry
from docgen.auth.api_key_manager import APIKeyManager
from docgen.utils.ai_client import AIClient

console = Console()

class AIDocGenerator:
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.ai_client = AIClient()
        
        # Cache and rate limit settings
        self.cache_dir = Path.home() / '.docgen' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.CALLS_PER_MINUTE = 14
        self.PERIOD = 60
        self.MIN_WAIT_TIME = 5
        self.MAX_RETRIES = 3 
        self.BACKOFF_FACTOR = 2 
        
        # Initialize memory cache
        self._memory_cache = {}
        self.console = Console()
        self.BATCH_SIZE = 5
        self.PARALLEL_WORKERS = min(multiprocessing.cpu_count(), 4)
        self._cache_hits = 0
        self._api_calls = 0

    @sleep_and_retry
    @limits(calls=14, period=60)
    def _generate_doc(self, analysis: Dict, code: str) -> str:
        """Generate documentation with better error handling."""
        try:
            # Ensure code content is properly formatted
            if not code or not code.strip():
                return "Error: Empty code content"
            
            # Generate documentation using AI
            response = self.ai_client.generate_text(code=code, prompt_type='doc')
            if not response:
                raise ValueError("Empty response from AI model")
            return response
            
        except Exception as e:
            retries += 1
            wait_time = self.MIN_WAIT_TIME * (self.BACKOFF_FACTOR ** retries)
            self.console.print(f"[yellow]Attempt {retries}/{self.MAX_RETRIES} failed. Waiting {wait_time}s...[/yellow]")
            time.sleep(wait_time)
            if retries == self.MAX_RETRIES:
                raise Exception(f"Failed after {self.MAX_RETRIES} attempts: {str(e)}")

    def _process_file_group(self, group: List[Tuple[Path, Dict, str]]) -> Dict[Path, str]:
        results = {}
        template_doc = None
        
        for path, analysis, code in group:
            try:
                cache_key = self._fast_cache_key(code, analysis)
                doc = self._get_cached_doc(cache_key)
                
                if doc:
                    self._cache_hits += 1
                    results[path] = doc
                    continue
                doc = self._generate_doc(analysis, code)
                self._api_calls += 1
                
                self._save_to_cache(cache_key, doc)
                results[path] = doc
                
            except Exception as e:
                results[path] = f"Error: {str(e)}"
        
        return results

    async def generate_documentation_batch(self, files_data: List[Tuple[Path, Dict, str]]) -> Dict[Path, str]:
        """Generate documentation for multiple files concurrently."""
        try:
            # Prepare batch requests
            requests = [
                {
                    'code': code,
                    'prompt_type': 'doc',
                    'file_path': str(path)
                }
                for path, _, code in files_data
            ]

            # Generate documentation concurrently
            results = await self.ai_client.generate_text_batch(requests)
            
            # Map results back to files
            return {
                path: result for (path, _, _), result in zip(files_data, results)
                if result is not None
            }
            
        finally:
            await self.ai_client.close()

    def _group_similar_files(self, files_data: List[Tuple[Path, Dict, str]]) -> List[List[Tuple[Path, Dict, str]]]:
        """Group similar files to reduce redundant processing."""
        groups = {}
        
        for file_data in files_data:
            path, analysis, code = file_data
            
            # Create a signature based on file structure
            signature = self._get_file_signature(analysis)
            
            if signature not in groups:
                groups[signature] = []
            groups[signature].append(file_data)
        
        return list(groups.values())

    def _get_file_signature(self, analysis: Dict) -> str:
        """Create a signature for file grouping."""
        signature_parts = {
            'class_count': len(analysis.get('classes', [])),
            'func_count': len(analysis.get('functions', [])),
            'import_count': len(analysis.get('imports', []))
        }
        return json.dumps(signature_parts, sort_keys=True)

    def _adapt_template(self, template: str, analysis: Dict, code: str) -> str:
        """Adapt template documentation for similar files."""
        try:
            # Extract key elements
            class_names = [c['name'] for c in analysis.get('classes', [])]
            func_names = [f['name'] for f in analysis.get('functions', [])]
            
            # Replace relevant parts
            doc = template
            for old_name in class_names + func_names:
                if old_name in doc:
                    # Find corresponding name in current file
                    new_name = next((name for name in (class_names + func_names) 
                                   if name != old_name and len(name) > 3), old_name)
                    doc = doc.replace(old_name, new_name)
            
            return doc
        except Exception as e:
            self.console.print(f"[yellow]Warning: Template adaptation failed, generating new doc[/yellow]")
            return self._generate_doc(analysis, code)

    def _create_cache_key(self, code: str, analysis: Dict) -> str:
        """Create efficient cache key."""
        content = f"{code[:1000]}|{str(analysis)[:500]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_doc(self, cache_key: str) -> str:
        """Get from memory or file cache."""
        # Check memory cache first
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
            
        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                self._memory_cache[cache_key] = data['doc']
                return data['doc']
            except Exception:
                return None
        
        return None

    def _save_to_cache(self, cache_key: str, doc: str) -> None:
        """Save to both memory and file cache."""
        try:
            # Save to memory cache
            self._memory_cache[cache_key] = doc
            
            # Save to file cache
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_file.write_text(json.dumps({'doc': doc, 'timestamp': datetime.now().isoformat()}))
        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to cache documentation: {str(e)}[/yellow]") 

    def _fast_cache_key(self, code: str, analysis: Dict, query: bool=False) -> str:
        """Faster cache key generation."""
        key_content = f"{code[:100]}{str(analysis.get('classes', []))}{str(analysis.get('functions', []))}"
        if query:
            key_content += f"update"
        return hashlib.md5(key_content.encode()).hexdigest() 
    
    @sleep_and_retry
    @limits(calls=14, period=60)
    async def generate_update_documentation(self, code: str, changes: str, file_path: Optional[str] = None) -> str:
        """Generate documentation specifically for code updates."""
        try:
            if not changes.strip():
                return "No significant code changes detected."
                
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    response = self.ai_client.generate_text(
                        code=code,
                        changes=changes,
                        prompt_type='update',
                        file_path=str(file_path)
                    )
                    if not response:
                        raise ValueError("Empty response from AI model")
                    return response
                except Exception as e:
                    retries += 1
                    wait_time = self.MIN_WAIT_TIME * (self.BACKOFF_FACTOR ** retries)
                    self.console.print(f"[yellow]Attempt {retries}/{self.MAX_RETRIES} failed. Waiting {wait_time}s...[/yellow]")
                    time.sleep(wait_time)
                    if retries == self.MAX_RETRIES:
                        raise Exception(f"Failed after {self.MAX_RETRIES} attempts: {str(e)}")
                        
        except Exception as e:
            raise Exception(f"Failed to generate update documentation: {str(e)}")

    async def generate_update_documentation_batch(self, files_data: List[Tuple[Path, Dict, str, str]]) -> Dict[Path, str]:
        """Generate documentation updates for multiple files concurrently."""
        try:
            # Filter out files with no changes
            files_to_process = [
                (path, analysis, code, changes) 
                for path, analysis, code, changes in files_data 
                if changes.strip()
            ]
            
            if not files_to_process:
                return {}
                
            # Process files in batches through AI client
            # Convert Path objects to strings before passing to AI client
            serializable_files = [
                (str(path), analysis, code, changes) for path, analysis, code, changes in files_to_process
            ]
            
            results = await self.ai_client.generate_update_documentation_batch(serializable_files)
            
            # Convert string paths back to Path objects for the result dictionary
            path_results = {}
            for str_path, doc in results.items():
                # Find the original Path object
                original_path = next(path for path, _, _, _ in files_to_process if str(path) == str_path)
                path_results[original_path] = doc
                
                # Cache successful results
                if not doc.startswith("Error:"):
                    cache_key = self._fast_cache_key(
                        next(code for p, _, code, _ in files_to_process if str(p) == str_path),
                        next(analysis for p, analysis, _, _ in files_to_process if str(p) == str_path),
                        query=True
                    )
                    self._save_to_cache(cache_key, doc)
            
            return path_results
            
        except Exception as e:
            self.console.print(f"[red]Error generating batch updates: {str(e)}[/red]")
            return {
                path: f"Error: {str(e)}" 
                for path, _, _, _ in files_data
            }

    def _process_update_group(self, group: List[Tuple[Path, Dict, str, str]]) -> Dict[Path, str]:
        """Process a group of similar files for updates."""
        results = {}
        
        for path, analysis, code, changes in group:
            try:
                cache_key = self._fast_cache_key(code + changes, analysis, query=True)
                doc = self._get_cached_doc(cache_key)
                
                if doc:
                    self._cache_hits += 1
                    results[path] = doc
                    continue

                doc = self._generate_update_doc(analysis, code, changes)
                self._api_calls += 1
                
                self._save_to_cache(cache_key, doc)
                results[path] = doc
                
            except Exception as e:
                results[path] = f"Error: {str(e)}"
        
        return results

    @sleep_and_retry
    @limits(calls=14, period=60)
    def _generate_update_doc(self, analysis: Dict, code: str, changes: str) -> str:
        """Generate documentation for updates with retries."""
        if not changes.strip():
            return "No significant code changes detected."
            
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                response = self.ai_client.generate_text(
                    code=code,
                    changes=changes,
                    prompt_type='update'
                )
                if not response:
                    raise ValueError("Empty response from AI model")
                return response
            except Exception as e:
                retries += 1
                wait_time = self.MIN_WAIT_TIME * (self.BACKOFF_FACTOR ** retries)
                self.console.print(f"[yellow]Attempt {retries}/{self.MAX_RETRIES} failed. Waiting {wait_time}s...[/yellow]")
                time.sleep(wait_time)
                if retries == self.MAX_RETRIES:
                    raise Exception(f"Failed after {self.MAX_RETRIES} attempts: {str(e)}")