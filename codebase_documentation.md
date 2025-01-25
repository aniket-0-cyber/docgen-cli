
# Recent Updates

## Documentation Update (2025-01-25 12:08:12)

### Changed Files:
- docgen/cli.py
- docgen/generators/markdown_generator.py
- docgen/utils/ai_client.py

### Updates:

#### docgen/cli.py
1

* **Changed functionality:** The table of contents generation in the `_generate_async` function was modified.  The links to individual files within the table of contents are now removed.  The anchors remain in place for internal linking within the generated document.

* **Impact of changes:** The generated documentation now has a simpler table of contents, without hyperlinks to each section.  This simplifies the structure, but users will need to manually navigate to the specific file documentation.

* **Critical notes:** No critical notes.  This change is primarily stylistic and might affect user experience if they relied on the previous linked table of contents.
---

#### docgen/generators/markdown_generator.py
2

* **Changed functionality:** The docstrings for `generate_file_documentation`, `_generate_class_markdown`, and `_generate_function_markdown` have been updated for clarity.  The language-specific code fences (```python```) in `_generate_class_markdown` and `_generate_function_markdown` have been removed, making the generated markdown more generic.

* **Impact of changes:** The functions now generate more generic markdown, not specifically tailored to Python.  The docstrings are improved for better understanding.

* **Critical notes:** No critical notes.  The change in code fences allows for broader language support but may require adjustments if the target is specifically Python markdown.
---

#### docgen/utils/ai_client.py
3

* **Changed functionality:** The `base_urls` in the `AIClient` class initializer have been changed from localhost ports to a set of specific IP addresses and ports.

* **Impact of changes:** The AI client now connects to a specific set of remote servers instead of a locally running server.  This requires the remote servers to be available and correctly configured.

* **Critical notes:** This change fundamentally alters the deployment and requires access to the specified external servers.  The previous localhost setup is removed.  Error handling and connection management are critical to ensure robust operation.
---


## Documentation Update (2025-01-23 13:45:58)

### Changed Files:
- docgen/cli.py
- docgen/utils/ai_client.py

### Updates:

#### docgen/cli.py
1

* **Changed functionality:** The `AIClient` import was commented out (`# from docgen.utils.ai_client import AIClient`).

* **Impact of changes:**  This likely means the AI client interaction has been moved or refactored into a different module.  The `cli.py` file now relies on a different implementation for AI interaction, potentially for improved modularity or to address dependency issues.

* **Critical notes:** None.  The change is a refactoring and does not appear to introduce any critical issues, assuming the functionality is still provided elsewhere.
---

#### docgen/utils/ai_client.py
2

* **Changed functionality:**
    * Added caching mechanism using `hashlib`, `json`, `pathlib`, and `datetime` modules.  A cache directory is created in `~/.docgen/cache`.  Cache entries expire after one day.
    * Improved rate limiting:  Increased `RATE_LIMIT_REQUESTS` to 15 and maintained `RATE_LIMIT_WINDOW` at 60 seconds.  Adjusted retry logic and backoff factor in the session creation.
    * Increased concurrency:  Increased the semaphore value to 50 and connection pool sizes to 50.
    * Batching improved:  Increased `MAX_BATCH_SIZE` and `MAX_BATCH_TOKENS`.
    * Added error handling for cache read/write operations, including cleanup of corrupted cache files.
    * `_fast_cache_key` function now includes operation type ('generate' or 'update') to differentiate cache keys.
    * Added versioning to cached data.
    * `generate_text_batch` and `generate_update_documentation_batch` now utilize caching.
    * Retries reduced in `_make_request` for faster failure detection.
    * Timeout reduced in `_make_request`.

* **Impact of changes:** The changes significantly enhance the performance and efficiency of the AI client.  Batching, concurrency, and caching are implemented to handle larger codebases more effectively and reduce the number of requests to the AI server.  Improved error handling and rate limiting make the system more robust.

* **Critical notes:** The caching mechanism relies on the assumption that the code and analysis results remain relatively stable within a day.  Significant changes within that timeframe might lead to stale cache entries.  The cache key generation should be carefully reviewed to ensure uniqueness and avoid collisions, especially considering the use of only the first 100 characters of code.  The error handling attempts to gracefully handle cache issues, but it's still crucial to monitor for unexpected behavior.  The assumption is that the API supports batch requests (`/api/v1/gemini/generate/batch`).
---


## Documentation Update (2025-01-23 12:52:13)

### Changed Files:
- docgen/utils/ai_client.py

### Updates:

#### docgen/utils/ai_client.py
1

**1. Changed Functionality:**

*   Increased concurrency limit for asynchronous requests from 10 to 50.
*   Adjusted rate limiting parameters (`RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`) for improved throughput.
*   Increased maximum batch size (`MAX_BATCH_SIZE`) and token limit (`MAX_BATCH_TOKENS`) for fewer requests.
*   Reduced retry attempts in `_make_request` from 2 to 1 for faster failure handling.
*   Reduced retry timeout in `_make_request` from 30 to 15 seconds.
*   Reduced retry attempts in `_make_batch_request` from 3 to 2.
*   Reduced `backoff_factor` in retry strategy from 0.1 to 0.05 for faster retries.
*   Increased connection pool size in `_create_session` from 20 to 50.
*   Reduced total retry attempts in `_create_session` from 3 to 2.
*   `generate_text_batch` now processes batches concurrently using `asyncio.gather`.
*   Improved error handling in `generate_update_documentation_batch`.
*   Added `finally` block in `generate_update_documentation_batch` to ensure session closure.


**2. Impact of Changes:**

The changes aim to significantly improve the performance and efficiency of the AI client. Increased concurrency, larger batch sizes, and faster retry strategies should lead to faster processing of requests and better handling of rate limits and server errors.  The reduced retry attempts prioritize faster failure detection.

**3. Critical Notes:**

*   The code assumes the existence of `docgen.auth.api_key_manager`.  Ensure this module is correctly configured and available.
*   The token estimation (`_estimate_tokens`) is a very rough approximation.  More sophisticated tokenization might be necessary for accurate batching.
*   The rate limiting parameters might need further adjustment based on the actual server's capabilities and response times.  Careful monitoring is recommended.
*   Error handling relies heavily on catching generic `Exception` objects. More specific exception handling might be beneficial for better debugging.
---


## Documentation Update (2025-01-16 13:16:02)

### Changed Files:
- docgen/cli.py
- docgen/generators/ai_doc_generator.py

### Updates:

#### docgen/cli.py
1. **Modified Feature:**  The `docgen auth login` command invocation instruction within the usage limit exceeded message in the `_generate_async` function has been updated.


2. **Usage Example (Illustrative):** The change doesn't affect usage; the error message is updated.  Before:  `2. Run: docgen auth login --key YOUR_API_KEY` After: `2. Run: docgen auth login --key=YOUR_API_KEY`


3. **Important Notes:** The `--key` option in the `docgen auth login` command now requires an equals sign (`=`) before the API key value for correct parsing.  This is a minor update to command-line argument handling for consistency.

---

#### docgen/generators/ai_doc_generator.py
## Code Changes: AIDocGenerator Class

1. **Removed Template-Based Documentation Adaptation:** The `_process_file_group` and `_process_update_group` methods no longer use templates to adapt documentation for similar files.  Instead, they generate documentation individually for each file using  `_generate_doc` and `_generate_update_doc` respectively. This eliminates the previous behavior of reusing a template and applying adaptations based on detected class and function names.  The `_adapt_template` function is now effectively dead code.


2. **Modified Cache Key Generation:** The `_fast_cache_key` method now accepts a `query` boolean parameter.  If `query` is `True` (as used in update processing),  "update" is appended to the key content, distinguishing update documentation from the original documentation in the cache. This ensures that updates are cached separately.

3. **Simplified Update Documentation Generation:** The logic in `_process_file_group` and `_process_update_group` is simplified to generate documentation directly for each file rather than trying to reuse a template.



**Simple Usage Example (Illustrative - adapt to your specific file data):**

```python
generator = AIDocGenerator()
files_data = [
    (Path("file1.py"), {"classes": [{"name": "ClassA"}], "functions": []}, "code1"),  # Example file data
    (Path("file2.py"), {"classes": [{"name": "ClassB"}], "functions": []}, "code2"),
]

# Generate documentation for original files
results = asyncio.run(generator.generate_documentation_batch(files_data))
print(results)

update_files_data = [
    (Path("file1.py"), {"classes": [{"name": "ClassA"}], "functions": []}, "code1", "updated code"), #Example file data with changes
    (Path("file2.py"), {"classes": [{"name": "ClassB"}], "functions": []}, "code2", "updated code"),
]
update_results = asyncio.run(generator.generate_update_documentation_batch(update_files_data))
print(update_results)
```

**Important Notes:**

* The removal of template adaptation may lead to increased API calls and potentially higher costs if many files share similar structures.  The performance implications should be evaluated.
* The changes simplify the code and reduce complexity, but they sacrifice the potential optimization of using a template for similar files.  The impact on performance should be monitored, especially for large sets of files.


---


## Documentation Update (2025-01-15 13:46:01)

### Changed Files:
- docgen/cli.py
- docgen/generators/ai_doc_generator.py
- backend/run.py
- backend/src/config/settings.py
- backend/src/main.py
- backend/src/models/usage.py
- backend/src/models/user.py
- backend/src/routes/auth.py
- backend/src/routes/gemini.py
- backend/src/routes/usage.py
- backend/src/utils/prompts.py
- backend/src/utils/security.py
- backend/src/utils/supabase_client.py

### Updates:

#### docgen/cli.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### docgen/generators/ai_doc_generator.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/run.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/config/settings.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/main.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/models/usage.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/models/user.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/routes/auth.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/routes/gemini.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/routes/usage.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/utils/prompts.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/utils/security.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---

#### backend/src/utils/supabase_client.py
### Documentation Update for `docgen/cli.py`

1. **New Features and Modifications:**

* **Improved File Handling in `process_file`:**  The `process_file` function now includes robust error handling for file reading, including handling `UnicodeDecodeError` and checking for empty files.  Warnings are now issued for unreadable or empty files instead of causing crashes.  The function also adds a header to the generated documentation file including file name and timestamp.
* **Large File Handling:** Added a check in `_generate_async` and `_update_docs_async` to skip files larger than 2MB, improving performance and preventing potential crashes with excessively large files.
* **Batch Processing Enhancement:** The `generate` and `update` commands now process multiple files in batches asynchronously using `asyncio` and `AIDocGenerator.generate_documentation_batch`, significantly improving performance for larger codebases.
* **`update` Command Enhancements:** The `update` command now supports generating a separate file (`--updates-file`) containing only the changes, in addition to updating the full documentation (`--full`). The existing documentation is now updated in place rather than being completely rewritten.
* **Detailed Usage Tracking:** The `UsageTracker` now provides more detailed messages about usage limits and remaining quota.

2. **Usage Examples:**

* **Generating documentation for changed files only (incremental updates):**
 ```bash
 docgen update --updates-file updates.md
 ```
* **Generating documentation for all files (full update):**
 ```bash
 docgen update --full
 ```

3. **Important Notes:**

* The changes significantly improve the robustness and performance of the `docgen` CLI, especially when dealing with large codebases or many files.  The added error handling prevents unexpected crashes.  The batch processing dramatically reduces the time taken for documentation generation. The `update` command's flexibility allows users more control over how changes are incorporated into documentation.

---


## Documentation Update (2025-01-10 12:04:01)

### Changed Files:
- docgen/cli.py
- docgen/generators/ai_doc_generator.py

### Updates:

#### docgen/cli.py
## DocGen CLI Update:  Documentation Generation Improvements

This update focuses on enhancing the core documentation generation process and improving the handling of large codebases.

**Changes:**

* **Improved File Handling:** The `generate` command now leverages the `SUPPORTED_EXTENSIONS` constant to determine which files to process,  eliminating the hardcoded list of extensions. This allows for easier extensibility in supporting new file types.
* **Large File Handling:**  The `generate` command now skips files larger than 2MB to prevent excessive processing time and potential memory issues. A warning message is displayed for each skipped file.
* **Asynchronous Batch Processing:**  The `generate` command now uses asynchronous operations with `asyncio` to improve the speed of processing multiple files concurrently.
* **Removal of `analyze` command:** The `analyze` command has been removed.  The code analysis functionality remains integrated into the `generate` command.

**Simple Usage Example (generate command):**

To generate documentation for the current directory, including files with supported extensions:

```bash
docgen generate --current-dir
```

**Important Notes:**

* The removal of the standalone `analyze` command means that code analysis is now performed implicitly during documentation generation.
* The introduction of asynchronous processing may significantly reduce the time required to generate documentation for large codebases.  However, the actual speed improvement will depend on your system's resources and the complexity of the codebase.
* The 2MB file size limit for skipping large files can be adjusted in the source code if needed.

---

#### docgen/generators/ai_doc_generator.py
## Documentation Update: `AIDocGenerator` Class

The following changes were made to the `AIDocGenerator` class:

### 1. Improved `_create_update_prompt` Function:

* **Original Prompt:** The original prompt for generating update documentation was less specific, requesting features, functionality, examples, and notes without explicitly focusing on changes.

* **Updated Prompt:** The updated `_create_update_prompt` function now provides a more precise prompt.  It explicitly instructs the AI to focus only on changes and their impact, specifying the format and desired level of detail.  The prompt now also clearly indicates what constitutes additions and deletions using the `+` and `-` symbols respectively in the diff.  The required sections are also more concise and relevant to change analysis.


* **Impact:** This change results in more focused and relevant documentation updates, highlighting only the differences between code versions.  The AI is guided to provide more concise and technical updates focused solely on the impacted aspects.


### 2.  `generate_update_documentation` Function:

* **Change:** The method now includes error handling, ensuring that empty or null responses from the AI model are explicitly handled and raise an appropriate exception.

* **Impact:** This enhancement improves the robustness of the `generate_update_documentation` function, preventing unexpected errors and providing more informative error messages.  This leads to more reliable update generation.

### 3.  Minor Changes to Prompt Structure in `_create_update_prompt`

The prompt structure within `_create_update_prompt` has been slightly adjusted for clarity and consistency. The original prompt included redundancies and was slightly less focused.  This refinement makes the instructions provided to the AI more precise.

---


## Documentation Update (2025-01-09 14:04:52)

### Changed Files:
- docgen/analyzers/base_analyzer.py
- docgen/analyzers/code_analyzer.py
- docgen/utils/git_utils.py
- docgen/utils/extension.py

### Updates:

#### docgen/analyzers/base_analyzer.py
## Documentation Update: `docgen/analyzers/base_analyzer.py`

**Changes:** The `get_language_extensions` abstract method has been removed from the `BaseAnalyzer` class.

**Impact:**

*   Language-specific analyzers no longer need to implement a method to declare supported file extensions.  The mechanism for determining which analyzer to use for a given file will need to be updated elsewhere in the codebase (this change is not reflected in the provided diff).

**Key Functionality Removed:**

*   The ability to directly query a `BaseAnalyzer` for its supported file extensions.


**Important Notes:**

* This change necessitates a modification to the overall analyzer selection logic. The updated logic must determine file type based on other information or methods.

---

#### docgen/analyzers/code_analyzer.py
## Code Analyzer Documentation Update

The following changes were made to the `CodeAnalyzer` class:

**1. Removed Feature:**

* The `get_language_extensions()` static method has been removed. This method previously returned a list of common programming language file extensions.

**2. Impact:**

* The `CodeAnalyzer` class no longer provides a built-in list of supported file extensions.  If extension-based filtering or language detection is required, this logic must now be implemented elsewhere in the application.

**3. Key Functionality Change:**

* The core `analyze_file()` method remains unchanged.  It still analyzes a file, reading its contents and returning a dictionary with file metadata and source code.

**4. Important Notes:**

*  Any code relying on the `get_language_extensions()` method will need to be updated to provide its own mechanism for identifying file types or filtering by extensions.  

---

#### docgen/utils/git_utils.py
## Documentation Update: `git_utils.py` - `get_changed_files()` method

**1. New or Modified Features:**

* The `get_changed_files()` method has been completely rewritten for improved efficiency and error handling.
* It now uses `git diff-index` to retrieve all changes (staged and unstaged) in a single operation, rather than iterating through staged and unstaged changes separately.  This significantly improves performance, especially in large repositories.
* The method directly accesses the patch from the diff object, reducing redundant file reads and improving speed.
* Enhanced handling of UnicodeDecodeError during file reading.
* Explicit checks for file existence before attempting to read content.
* Improved error handling with more informative console messages.
* More robust handling of untracked files, including better filtering of hidden and unsupported files.
* Added support for detecting new files.

**2. Key Functionality:**

* The core functionality remains the same: to identify files changed since the last documentation update and return a dictionary containing file paths, change types ('modified' or 'new'), patch information, and full file content.  However, the implementation is significantly improved for efficiency and robustness.

**3. Simple Usage Example:**

The usage remains unchanged:

```python
analyzer = GitAnalyzer()
changed_files = analyzer.get_changed_files()
```

**4. Important Notes:**

* The previous method's approach of handling staged and unstaged changes separately has been replaced by a more efficient single-pass approach using `git diff-index`.
* The structure of the returned dictionary remains consistent, though the method of obtaining the change information is significantly different.
* The error handling is now more comprehensive, providing more detailed information in case of errors.
* The method now explicitly handles untracked files and better filters for hidden/unsupported files.


---

#### docgen/utils/extension.py
## Documentation Update: `SUPPORTED_EXTENSIONS`

**Changes:** No actual changes were made to the `SUPPORTED_EXTENSIONS` list itself. The provided diff shows the list's *content*, not modifications to it.  Therefore, no functional changes have occurred.  The diff likely represents a refactoring or a simple copy/paste of the existing list into the `docgen/utils/extension.py` file.

**Impact:** No impact on functionality. The list of supported file extensions remains unchanged.

---



## Documentation Update (2025-01-09 13:41:39)

### Changed Files:
- docgen/cli.py
- docgen/generators/ai_doc_generator.py
- docgen/utils/git_utils.py

### Updates:

#### docgen/cli.py
# DocGen CLI Update: Incremental Documentation Updates

This update introduces the ability to generate incremental documentation updates using Git version control.


## New Features:

* **`update` command:**  This command now allows for generating updates to existing documentation, either as a full re-generation or incremental updates stored in a separate file.
* **Incremental Updates:** The `update` command (and its alias `u`) can now generate documentation updates showing only changes since the last documentation generation, leveraging Git history.  These updates can be appended to an existing documentation file or saved into a separate file specified by `--updates-file`.
* **Full Update Option:**  A `--full` flag has been added to the `update` command to force a full regeneration of the documentation for all changed files.
* **`update_existing_documentation` function:** Added to handle full updates within the existing documentation file, adding a "Recent Updates" section if it doesn't exist.
* **`add_incremental_update` function:**  Handles the creation and appending of incremental updates to either an existing documentation file or a newly created one (if `--updates-file` is specified).


## Key Functionality Changes:

* The `update` command uses `GitAnalyzer` to identify changed files and their content differences.
* The `AIDocGenerator` now includes an `async generate_update_documentation` method to efficiently generate documentation for code changes.
* Large files (>2MB) are skipped during both generation and update.
* Improved error handling and informative console output during update process.


## Usage Example:

To generate incremental updates to an existing `codebase_documentation.md` file:

```bash
docgen update
```

To generate incremental updates and store them in a separate file named `updates.md`:

```bash
docgen update --updates-file updates.md 
```

To perform a full update of the documentation:

```bash
docgen update --full
```


## Important Notes:

* This update requires Git to be installed and configured within the project directory.  The `GitAnalyzer` relies on Git's functionality to detect changes.
*  The `update` command assumes the existence of a file named "codebase_documentation.md" unless the `--updates-file` option is used. If this file doesn't exist and a full update is not requested,  the command will generate a new file.
* Error messages during analysis are now presented as warnings, allowing the process to continue.
*  The `update` command now ensures the use of absolute file paths.

---

#### docgen/generators/ai_doc_generator.py
## Documentation Update: AIDocGenerator

This update introduces a new method for generating documentation updates based on code changes.


### New Method: `generate_update_documentation`

This asynchronous method takes the original code and the changes as input and returns updated documentation focusing only on the changes and their impact.

**Signature:**

```python
async def generate_update_documentation(self, code: str, changes: str) -> str:
```

**Parameters:**

* `code` (str): The original code snippet.
* `changes` (str): A diff showing the code changes (+ for additions, - for deletions).

**Returns:**

* `str`: Updated documentation in markdown format, highlighting only the changes and their impact.  Returns "No significant code changes detected." if no changes are provided.

**Functionality:**

The method constructs a specific prompt for the AI model, tailored to generating focused documentation updates. The prompt includes the original code, the changes, and instructions to focus only on the changes and their impact. The model's response is then returned.  Error handling is implemented to manage potential issues during the AI call.  Rate limiting and retry mechanisms are the same as other AI calls.


**Impact:**

This addition enhances the functionality of the `AIDocGenerator` class by enabling the generation of more targeted and efficient documentation updates, reducing the need to regenerate complete documentation for minor code modifications.  The prompt is explicitly designed to guide the AI towards concise and focused updates.

---

#### docgen/utils/git_utils.py
## Documentation Update for `git_utils.py`

**Changes:**

* **Improved `get_changed_files` function:** This function now more accurately identifies changed files by differentiating between unstaged, staged, and untracked files.  The unified diff generation is enhanced to better represent file changes.  Error handling is improved to include exception type in error messages.

* **No functional changes to `update_last_documented_state` function:** This function remains unchanged in its logic.

**Impact:**

* More comprehensive identification of file changes, including better handling of untracked files.
* Improved accuracy of the generated diffs.
* Enhanced error reporting in `get_changed_files` providing greater diagnostic information.


**No changes to key functionality or usage examples needed.**

**Important Notes:**

* The improved error handling in `get_changed_files` provides more detailed error information for debugging purposes.
* The `get_changed_files` function now provides a more comprehensive representation of changes in a Git repository, including detailed diffs for modified files and a clear representation of new files.

---

# Codebase Documentation

Generated on: 2025-01-08 05:09:07


## Table of Contents

- [docgen/__init__.py](#docgen-__init__.py)

- [docgen/analyzers/__init__.py](#docgen-analyzers-__init__.py)

- [docgen/analyzers/base_analyzer.py](#docgen-analyzers-base_analyzer.py)

- [docgen/analyzers/code_analyzer.py](#docgen-analyzers-code_analyzer.py)

- [docgen/cli.py](#docgen-cli.py)

- [docgen/config/__init__.py](#docgen-config-__init__.py)

- [docgen/config/config_handler.py](#docgen-config-config_handler.py)

- [docgen/config/language_config.py](#docgen-config-language_config.py)

- [docgen/generators/__init__.py](#docgen-generators-__init__.py)

- [docgen/generators/ai_doc_generator.py](#docgen-generators-ai_doc_generator.py)

- [docgen/generators/docstring_generator.py](#docgen-generators-docstring_generator.py)

- [docgen/generators/markdown_generator.py](#docgen-generators-markdown_generator.py)

- [docgen/utils/__init__.py](#docgen-utils-__init__.py)

- [docgen/utils/config.py](#docgen-utils-config.py)

- [docgen/utils/git_utils.py](#docgen-utils-git_utils.py)

- [setup.py](#setup.py)

- [tests/__init__.py](#tests-__init__.py)

- [tests/test_cli.py](#tests-test_cli.py)

- [tests/test_config.py](#tests-test_config.py)

- [tests/test_generator.py](#tests-test_generator.py)

- [tests/test_git_utils.py](#tests-test_git_utils.py)


<a id='docgen-__init__.py'></a>

## docgen/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-analyzers-__init__.py'></a>

## docgen/analyzers/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-analyzers-base_analyzer.py'></a>

## docgen/analyzers/base_analyzer.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-analyzers-code_analyzer.py'></a>

## docgen/analyzers/code_analyzer.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-cli.py'></a>

## docgen/cli.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-config-__init__.py'></a>

## docgen/config/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-config-config_handler.py'></a>

## docgen/config/config_handler.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-config-language_config.py'></a>

## docgen/config/language_config.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-generators-__init__.py'></a>

## docgen/generators/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-generators-ai_doc_generator.py'></a>

## docgen/generators/ai_doc_generator.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-generators-docstring_generator.py'></a>

## docgen/generators/docstring_generator.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-generators-markdown_generator.py'></a>

## docgen/generators/markdown_generator.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-utils-__init__.py'></a>

## docgen/utils/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-utils-config.py'></a>

## docgen/utils/config.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='docgen-utils-git_utils.py'></a>

## docgen/utils/git_utils.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='setup.py'></a>

## setup.py

# `docgen-cli` Technical Documentation

## 1. Purpose/Overview

`docgen-cli` is a command-line tool built using Python and the `setuptools` package. It automates the generation of software documentation, leveraging AI capabilities for enhanced efficiency.  This `setup.py` file configures the package for installation and distribution.


## 2. Key Functionality

* **Package Configuration:**  Defines metadata for the `docgen-cli` package, including name, version, author, description, and dependencies.
* **Dependency Management:** Specifies required libraries (`typer`, `rich`, `gitpython`, `google-generativeai`) for installation using `pip`.
* **Entry Point Definition:** Creates a console script (`docgen`) that launches the application's main function (`docgen.cli:app`).
* **README Integration:** Reads and includes the project's README.md file in the package metadata.
* **Classifier Specifications:**  Provides information about the package's intended audience, programming languages supported, license, and operating system compatibility.

## 3. Simple Usage Example

The usage example would involve installing the package and then running the `docgen` command.  The specifics of the command-line interface are not defined within `setup.py`.

```bash
pip install . # Install from the current directory
docgen --help # Show available command-line options 
```


## 4. Important Notes

* This file (`setup.py`) only describes the package's structure and dependencies for installation; it does not contain the core documentation generation logic. That logic resides in the `docgen` package itself.
* The `install_requires` section lists the minimum required versions of the dependencies.  Updating these versions requires modifying this file and reinstalling the package.
* The `classifiers` section helps users and package managers understand the compatibility and suitability of this package for their environments.  Accuracy here is crucial for proper indexing and discoverability.
* The `google-generativeai` dependency suggests the use of Google's AI services for documentation generation; ensure proper API keys and authentication are configured separately.



---


<a id='tests-__init__.py'></a>

## tests/__init__.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='tests-test_cli.py'></a>

## tests/test_cli.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='tests-test_config.py'></a>

## tests/test_config.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='tests-test_generator.py'></a>

## tests/test_generator.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---


<a id='tests-test_git_utils.py'></a>

## tests/test_git_utils.py

# Technical Documentation: Docstring and Markdown Generators

This document describes two Python code modules: `DocstringGenerator` and `MarkdownGenerator`, used for automated documentation generation.  These generators create docstrings and Markdown formatted documentation from provided analysis results.

## Key Functionality:

**`DocstringGenerator`:**

* Generates docstrings for functions based on provided metadata (name, arguments, return type).
* Uses a template to ensure consistent docstring formatting.  The exact template is not specified in the provided code but is implied by the assertions.
* Handles cases where the input `docstring` is `None`.

**`MarkdownGenerator`:**

* Generates Markdown formatted documentation for Python modules.
* Processes analysis results containing module, class, and function information, including docstrings.
* Organizes the output into sections for modules, classes, and functions, with appropriate headings.

## Usage Example:

```python
from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

# Docstring generation
generator = DocstringGenerator()
function_info = {"name": "my_function", "args": ["a", "b"], "returns": "int", "docstring": None}
docstring = generator.generate_function_docstring(function_info)
print(docstring)

# Markdown generation
generator = MarkdownGenerator()
analysis_result = { # ... (example analysis result as shown in the provided code) ... }
markdown = generator.generate_file_documentation(analysis_result)
print(markdown)
```

## Important Notes:

* The provided code snippets are unit tests, demonstrating the functionality of the generators.  The actual implementations of `DocstringGenerator` and `MarkdownGenerator` are not shown.
* The structure and content of the generated docstrings and Markdown depend on the internal logic of the respective generator classes (not provided here).
* The `analysis_result` dictionary needs to be populated appropriately with the relevant information to be included in the documentation.  The format shown is an example.
* Error handling (e.g., for invalid input data) is not explicitly shown in the provided code.  Robust error handling should be implemented in a production environment.



---
