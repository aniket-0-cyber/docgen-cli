from rich.console import Console
import google.generativeai as genai
from pathlib import Path
from typing import Dict, List, Tuple
import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from dotenv import load_dotenv
import time
from ratelimit import limits, sleep_and_retry

load_dotenv()
console = Console()

class AIDocGenerator:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Please set GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Cache and rate limit settings
        self.cache_dir = Path.home() / '.docgen' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.CALLS_PER_MINUTE = 14
        self.PERIOD = 60
        self.last_call = 0
        self.call_count = 0
        self.MIN_WAIT_TIME = 5  # minimum wait time in seconds
        self.MAX_RETRIES = 3 
        self.BACKOFF_FACTOR = 2 
        
        # Initialize memory cache
        self._memory_cache = {}
        
        # Initialize console for status messages
        self.console = Console()

        self.BATCH_SIZE = 5  # Process files in smaller batches
        self.PARALLEL_WORKERS = min(multiprocessing.cpu_count(), 4)
        self._cache_hits = 0
        self._api_calls = 0

    def _create_prompt(self, code: str) -> str:
        """Create a language-agnostic prompt for the AI model."""
        return f"""
        Create technical documentation for this code:

        CODE:
        ```
        {code}
        ```
        
        Please provide:
        1. Brief purpose/overview (1-2 sentences max)
        2. Key functionality (bullet points)
        3. Usage example (if applicable)
        4. Important notes (only if changes are critical or important)

        Format in markdown, be short and concise and technical.
        """

    @sleep_and_retry
    @limits(calls=14, period=60)
    def _generate_doc(self, analysis: Dict, code: str) -> str:
        """Generate documentation with better error handling."""
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                prompt = self._create_prompt(code)
                response = self.model.generate_content(prompt)
                if not response.text:
                    raise ValueError("Empty response from AI model")
                return response.text
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
                # Fast cache check
                cache_key = self._fast_cache_key(code, analysis)
                doc = self._get_cached_doc(cache_key)
                
                if doc:
                    self._cache_hits += 1
                    results[path] = doc
                    continue

                if template_doc is None:
                    doc = self._generate_doc(analysis, code)
                    template_doc = doc
                    self._api_calls += 1
                else:
                    doc = self._adapt_template(template_doc, analysis, code)
                
                self._save_to_cache(cache_key, doc)
                results[path] = doc
                
            except Exception as e:
                results[path] = f"Error: {str(e)}"
        
        return results

    async def generate_documentation_batch(self, files_data: List[Tuple[Path, Dict, str]]) -> Dict[Path, str]:
        results = {}
        grouped_files = self._group_similar_files(files_data)
        
        with ThreadPoolExecutor(max_workers=self.PARALLEL_WORKERS) as executor:
            futures = []
            for group in grouped_files:
                future = executor.submit(self._process_file_group, group)
                futures.append(future)
            
            completed = 0
            total = len(files_data)
            for future in futures:
                group_results = future.result()
                results.update(group_results)
                completed += len(group_results)
                
                if completed % 5 == 0:
                    self.console.print(f"[green]Processed: {completed}/{total} files[/green]")
        return results

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

    def _fast_cache_key(self, code: str, analysis: Dict) -> str:
        """Faster cache key generation."""
        key_content = f"{code[:100]}{str(analysis.get('classes', []))}{str(analysis.get('functions', []))}"
        return hashlib.md5(key_content.encode()).hexdigest() 

    def _create_update_prompt(self, code: str, changes: str) -> str:
        """Create a prompt specifically for updating documentation based on changes."""
        return f"""As an expert developer, analyze these code changes and generate focused documentation updates.
                Focus only on what has changed and its impact. Format in markdown.

                Original Code Context:
                ```
                {code}
                Code Changes (+ for additions, - for deletions):
                ```

                Changes made:
                ```
                {changes}
                ```

                if there are no changes, then explain the code with below format:
                Please provide:
                1. Brief overview (1-2 sentences max)
                2. Key functionality (bullet points)
                3. Usage example (if applicable)
                else:
                1. Any new or modified or removed features with key functionality changes (bullet points)
                2. Simple usage example (if applicable)
                3. Important notes (only if changes are critical or important)

                Format in markdown, be short and concise and technical, focusing only on the changes.
                """ 
    
    @sleep_and_retry
    @limits(calls=14, period=60)
    async def generate_update_documentation(self, code: str, changes: str) -> str:
        """Generate documentation specifically for code updates."""
        try:
            if not changes.strip():
                return "No significant code changes detected."
            prompt = self._create_update_prompt(code, changes)
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from AI model")
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate update documentation: {str(e)}")