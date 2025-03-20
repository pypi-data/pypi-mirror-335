import base64
import json
import os
import requests
import pandas as pd
import hashlib
import pickle
import datetime
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import copy
from typing import Callable, Dict, Any, Optional, Union, List

from .hooks import TelaHooks, EMPTY_HOOKS

def encoded(filepath):
    with open(filepath, "rb") as file:
        encoded_content = base64.b64encode(file.read()).decode("utf-8")
    return f"data:application/pdf;base64,{encoded_content}"


class VaultFile:
    def __init__(self, file_path: str, api_key: str, vault_url="https://api.tela.com/__hidden/services/vault", cache_dir=".vault_cache"):
        self.file_path = file_path
        self.api_key = api_key
        self.vault_url = vault_url
        self.name = self._generate_file_name()
        self.vault_identifier = f"vault://{self.name}"
        self.file_hash = self._calculate_file_hash() if not file_path.startswith("vault://") else None
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "cache.json")
        self.cache = self._load_cache()

    def upload(self):
        if self.file_path.startswith("vault://"):
            # Skip upload for vault:// URLs as they're already in the vault
            return
            
        # Check if file is already in cache with the same hash
        if self.file_hash in self.cache:
            self.name = self.cache[self.file_hash]
            self.vault_identifier = f"vault://{self.name}"
            return
            
        upload_url = self._get_upload_url()
        # Upload the file to the URL
        with open(self.file_path, 'rb') as file:
            response = requests.put(upload_url, data=file)

        # Check if the upload was successful
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {self.name}, {response.text}")
        
        # Update cache with new file hash
        self.cache[self.file_hash] = self.name
        self._save_cache()
        
    def get_download_url(self):
        # Get a download URL for the file
        response = requests.get(
            f"{self.vault_url}/v2/files/{self.name}",
            headers={
                "Authorization": f"{self.api_key}"
            }
        )
    
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to get download URL for file: {self.name}")
            
        # Return the URL from the response
        return response.json().get('url')
    
    def _calculate_file_hash(self):
        """Calculate SHA-256 hash of file contents"""
        if not os.path.exists(self.file_path):
            return None
            
        sha256_hash = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _load_cache(self):
        """Load the cache from disk"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save the cache to disk"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def _generate_file_name(self):
        if self.file_path.startswith("vault://"):
            return self.file_path.replace("vault://", "")
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"tela_law_{timestamp}_{self.file_path.split('/')[-1]}"
        return name
    
    def _get_upload_url(self):
        # Make a POST request to the API endpoint
        response = requests.post(f"{self.vault_url}/v2/files/{self.name}", headers={
            "Authorization": f"{self.api_key}"
        })
        
        if response.status_code != 200:
            raise Exception(f"Failed to get upload URL: {response.json()}")

        # Parse and return the URL from the response
        return response.json().get('url')


def is_vault_url(url):
    return url and url.startswith("vault://")


def get_file_url(filepath, api_key):
    """Get appropriate URL for a file, handling vault:// URLs"""
    if not filepath:
        return None
    
    if filepath.startswith(('http://', 'https://')):
        return filepath
    
    if is_vault_url(filepath):
        return filepath
    
    return encoded(filepath)


def file(filepath, parser_type="tela-pdf-parser", range=None, api_key=None, **options):
    file_options = options.copy()
    file_options["parserType"] = parser_type
    if range is not None:
        file_options["range"] = range
    # print(filepath)
    file_url = get_file_url(filepath, api_key)
    
    return {
        "file_url": file_url,
        "options": file_options
    }

def files(file_paths, parser_type="tela-pdf-parser", range=None, api_key=None, **options):
    """
    Create a files payload from a list of file paths with optional parameters.
    
    Args:
        file_paths (list): List of file paths or URLs to process
        parser_type (str, optional): Type of parser to use. Defaults to "tela-pdf-parser"
        range (str, optional): Page range to process. Defaults to None
        api_key (str, optional): API key for vault access
        **options: Additional options to pass to the parser
        
    Returns:
        dict: Files payload with list of processed files
    """
    file_list = []
    for f in file_paths:
        file_list.append(file(f, parser_type=parser_type, range=range, api_key=api_key, **options))
        
    return {
        "files": file_list
    }

class TelaClient:
    """
    Client for interacting with the Tela API
    
    The TelaClient provides methods for interacting with Tela's API, including
    file operations, canvas execution, and more.
    
    Args:
        api_key (str): Tela API key for authentication
        api_url (str, optional): Base URL for the Tela API. Defaults to "https://api.tela.com"
        max_attempts (int, optional): Maximum number of retry attempts. Defaults to 3
        cache_dir (str, optional): Directory to store cache files. Defaults to ".tela_cache"
        hooks (TelaHooks, optional): Dictionary of lifecycle hooks. Defaults to empty hooks
        
    Lifecycle Hooks:
        See the `hooks` module for detailed documentation on available hooks and their signatures.
    """
    def __init__(self, api_key: str, api_url: str = "https://api.tela.com", 
                 max_attempts: int = 3, cache_dir: str = ".tela_cache", 
                 hooks: Optional[TelaHooks] = None):
        self.api_key = api_key
        self.api_url = api_url
        self.max_attempts = max_attempts
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._canvas_version_cache: Dict[str, str] = {}
        self._canvas_version_cache_time: Dict[str, datetime] = {}
        self.hooks: TelaHooks = hooks or EMPTY_HOOKS

    def upload_file(self, file_path):
        """
        Upload a file to Tela API and return the download URL
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            str: Download URL for the uploaded file
        """
        # Check if file is a vault URL
        if is_vault_url(file_path):
            vault_file = VaultFile(file_path, self.api_key)
            return vault_file.get_download_url()
            
        # Check if file exists in cache
        file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
        cache_key = f"upload_{file_hash}"
        
        cached_response = self._get_cached_response(cache_key, check_age=True)
        if cached_response:
            return cached_response['download_url']
            
        # Get upload URL from Tela API
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.post(f'{self.api_url}/v2/file', headers=headers)
        upload_url = response.json()['upload_url']
        
        # Upload file to the provided URL
        with open(file_path, 'rb') as file:
            upload_response = requests.put(upload_url, data=file)
            upload_response.raise_for_status()
        
        # Cache the response
        self._cache_response(cache_key, response.json())
        
        # Return the download URL
        return response.json()['download_url']

    def upload_to_vault(self, file_path):
        """
        Upload a file to Vault and return the vault URL
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            str: Vault URL for the uploaded file
        """
        vault_file = VaultFile(file_path, self.api_key)
        vault_file.upload()
        return vault_file.vault_identifier

    def get_vault_download_url(self, vault_url):
        """
        Get a download URL for a vault file
        
        Args:
            vault_url (str): Vault URL to get download URL for
            
        Returns:
            str: Download URL for the vault file
        """
        vault_file = VaultFile(vault_url, self.api_key)
        return vault_file.get_download_url()

    def _get_cache_key(self, documents, canvas_id, override, canvas_version=None):
        # Create a string containing all input parameters including canvas version
        cache_str = f"{json.dumps(documents, sort_keys=True)}_{canvas_id}_{json.dumps(override, sort_keys=True) if override else ''}_{canvas_version}"
        # Create a hash of the input parameters
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def _get_cached_response(self, cache_key, check_age=False):
        cache_file = self.cache_dir / f"{cache_key}.pickle"
        if cache_file.exists():
            if check_age:
                cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if cache_age >= timedelta(hours=12):
                    return None
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def _cache_response(self, cache_key, response):
        cache_file = self.cache_dir / f"{cache_key}.pickle"
        with open(cache_file, 'wb') as f:
            pickle.dump(response, f)

    def get_canvas_version(self, canvas_id):
        """
        Get the promoted version of a canvas
        
        Args:
            canvas_id (str): Canvas ID to get version for
            
        Returns:
            str: Version ID of the promoted canvas version
        """
        # Check if we have a cached version and it's less than 20 seconds old
        current_time = datetime.now()
        if canvas_id in self._canvas_version_cache and canvas_id in self._canvas_version_cache_time:
            cache_age = current_time - self._canvas_version_cache_time[canvas_id]
            if cache_age < timedelta(seconds=20):
                return self._canvas_version_cache[canvas_id]
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(
            f'{self.api_url}/prompt-version',
            headers=headers,
            params={"promptId": canvas_id}
        )
        
        if response.status_code != 200:
            return None
            
        versions = response.json()
        for version in versions:
            if version.get("promoted"):
                # Cache the version and timestamp
                self._canvas_version_cache[canvas_id] = version.get("id")
                self._canvas_version_cache_time[canvas_id] = current_time
                return version.get("id")
        
        return None

    def clear_canvas_cache(self, canvas_id):
        # Iterate through all cache files
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.pickle"):
            # Read the cache file to check if it contains the canvas_id
            with open(cache_file, 'rb') as f:
                try:
                    cache_data = pickle.load(f)
                    # Check if the cache entry is related to the specified canvas_id
                    if isinstance(cache_data, dict) and cache_data.get("uses") == canvas_id:
                        # Delete the cache file
                        cache_file.unlink()
                        cleared_count += 1
                except:
                    # Skip if there's any error reading the cache file
                    continue
        return cleared_count

    def clear_all_cache(self):
        # Delete all cache files in the cache directory
        cleared_count = 0
        for cache_file in self.cache_dir.glob("*.pickle"):
            try:
                cache_file.unlink()
                cleared_count += 1
            except:
                continue
        return cleared_count

    def request(self, documents, canvas_id, override=None, use_cache=True):
        # Get the current canvas version
        canvas_version = self.get_canvas_version(canvas_id) if use_cache else None
        
        if use_cache:
            cache_key = self._get_cache_key(documents, canvas_id, override, canvas_version)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                if self._run_hook('on_cache_hit', canvas_id=canvas_id):
                    return cached_response
            else:
                self._run_hook('on_cache_miss', canvas_id=canvas_id)
        try:
            self._run_hook('on_request_start', canvas_id=canvas_id)
            url = f"{self.api_url}/v2/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "canvas_id": canvas_id,
                "variables": documents,
                "long_response": True,
            }
            # Check if any variables contain vault:// URLs and replace them with download URLs
            # Create a new data object with processed vault URLs
            import copy
            processed_data = copy.deepcopy(data)
            if "variables" in processed_data:
                for key, value in processed_data["variables"].items():
                    # Replace None values with empty string
                    if value is None:
                        processed_data["variables"][key] = ""
                    # Check if the value is a dictionary with file_url
                    elif isinstance(value, dict) and "file_url" in value and is_vault_url(value["file_url"]):
                        vault_file = VaultFile(value["file_url"], self.api_key)
                        value["file_url"] = vault_file.get_download_url()
                    # Check if the value is a list of dictionaries (like in 'files' payload)
                    elif isinstance(value, dict) and "files" in value and isinstance(value["files"], list):
                        for file_item in value["files"]:
                            if isinstance(file_item, dict) and "file_url" in file_item and is_vault_url(file_item["file_url"]):
                                vault_file = VaultFile(file_item["file_url"], self.api_key)
                                file_item["file_url"] = vault_file.get_download_url()
            
            if override:
                processed_data["override"] = override
            # print(data)
            response = requests.post(url, headers=headers, data=json.dumps(processed_data))
            # print(response.json())
            if response.status_code != 200:
                error_data = response.json()
                self._run_hook('on_request_error', status_code=response.status_code, error=error_data)
                return error_data
            response_data = response.json()
            
            if use_cache:
                self._cache_response(cache_key, response_data)
            
            self._run_hook('on_request_success', canvas_id=canvas_id, response=response_data)
            return response_data
        except json.JSONDecodeError as e:
            self._run_hook('on_request_error', error=str(e), error_type='JSONDecodeError')
            return None

    def add_hook(self, hook_func: Callable) -> None:
        """
        Add a hook function to the client.
        
        The hook function must be decorated with @tela_hook.
        
        Args:
            hook_func: A function decorated with @tela_hook
        
        Raises:
            ValueError: If the function is not decorated with @tela_hook
        
        Example:
            ```python
            @tela_hook('on_request_start')
            def log_request(canvas_id, **kwargs):
                print(f"Request started for {canvas_id}")
                
            client.add_hook(log_request)
            ```
        """
        hook_name = getattr(hook_func, '_hook_name', None)
        if not hook_name:
            raise ValueError("Hook function must be decorated with @tela_hook")
        
        # Validate hook name
        from .hooks import _validate_hook_name
        _validate_hook_name(hook_name)
        
        # Add the hook to the hooks dictionary
        self.hooks[hook_name] = hook_func
    
    def _run_hook(self, hook_name: str, **kwargs: Any) -> bool:
        """
        Run a lifecycle hook if it exists
        
        Args:
            hook_name (str): Name of the hook to run
            **kwargs: Arguments to pass to the hook
            
        Returns:
            bool: True if the hook should continue normal execution, False to interrupt
        """
        if hook_name in self.hooks and callable(self.hooks[hook_name]):
            try:
                # Only treat explicit False returns as interrupting the flow
                # None or any other value will continue normal execution
                hook_result = self.hooks[hook_name](**kwargs)
                return hook_result is not False
            except Exception as e:
                # If a hook fails, we log the error but continue execution
                return True
        return True
        
    def new_canvas(self, canvas_id: str, expected_input: Optional[List[str]] = None) -> 'Canvas':
        """
        Create a new Canvas instance for executing a specific canvas
        
        Args:
            canvas_id (str): ID of the canvas to execute
            expected_input (List[str], optional): List of expected input variable names. Defaults to None
            
        Returns:
            Canvas: A Canvas instance configured for the specified canvas_id
        """
        return Canvas(self, canvas_id, expected_input, self.max_attempts)


class Canvas:
    """
    Canvas execution wrapper for Tela
    
    The Canvas class provides methods for running a specific canvas with inputs.
    
    Args:
        tela_client (TelaClient): TelaClient instance to use for API calls
        canvas_id (str): ID of the canvas to execute
        expected_input (List[str], optional): List of expected input variable names. Defaults to None
        max_attempts (int, optional): Maximum retry attempts per execution. Defaults to 3
        
    Lifecycle Hooks (inherited from TelaClient):
        on_canvas_run_start: Called when a canvas run begins
        on_missing_input: Called when expected input is missing
        on_canvas_attempt: Called for each canvas execution attempt
        on_canvas_retry: Called when a canvas execution is retried
        on_canvas_run_success: Called when a canvas run succeeds
        on_canvas_run_failure: Called when all canvas run attempts fail
    """
    def __init__(self, tela_client: 'TelaClient', canvas_id: str, 
                 expected_input: Optional[List[str]] = None, max_attempts: int = 3):
        self.canvas_id = canvas_id
        self.tela_client = tela_client
        self.expected_input = expected_input
        self.max_attempts = max_attempts
        
    def _run_hook(self, hook_name: str, **kwargs: Any) -> bool:
        """Proxy to run hooks via the TelaClient instance"""
        return self.tela_client._run_hook(hook_name, **kwargs)

    def run(self, output_type: str = 'json', override: Optional[Dict[str, Any]] = None, 
            use_cache: bool = True, **kwargs: Any) -> Any:
        """
        Execute the canvas with the provided inputs
        
        Args:
            output_type (str, optional): Format to return results in ('json' or 'dataframe'). Defaults to 'json'
            override (Dict[str, Any], optional): Override parameters for the canvas. Defaults to None
            use_cache (bool, optional): Whether to use cached results if available. Defaults to True
            **kwargs: Input variables for the canvas
            
        Returns:
            Any: Canvas execution result in the specified format
            
        Raises:
            ValueError: If any expected input is missing
        """
        self._run_hook('on_canvas_run_start', canvas_id=self.canvas_id, kwargs=kwargs)
        
        documents: Dict[str, Any] = {}
        if self.expected_input:
            for i in self.expected_input:
                if i in kwargs:
                    documents[i] = kwargs[i]
                else:
                    self._run_hook('on_missing_input', canvas_id=self.canvas_id, missing_input=i)
                    raise ValueError(f"Missing expected input: {i}")
        else:
            documents = kwargs

        def resolve_vault_urls(documents):
            # Process any file inputs to handle vault URLs
            for key, value in documents.items():
                if isinstance(value, dict) and "file_url" in value and is_vault_url(value["file_url"]):
                    # Replace vault URL with download URL
                    vault_file = VaultFile(value["file_url"], self.tela_client.api_key)
                    value["file_url"] = vault_file.get_download_url()
            return documents
        
        attempts = 0
        response = None
        original_documents = copy.deepcopy(documents)

        while attempts < self.max_attempts:
            self._run_hook('on_canvas_attempt', canvas_id=self.canvas_id, attempt=attempts+1, max_attempts=self.max_attempts)
            documents_with_resolved_urls = resolve_vault_urls(original_documents.copy())
            response = self.tela_client.request(documents_with_resolved_urls, self.canvas_id, override, use_cache)
            if response and "choices" in response and len(response["choices"]) > 0:
                break
            attempts += 1
            if attempts < self.max_attempts:
                self._run_hook('on_canvas_retry', canvas_id=self.canvas_id, attempt=attempts, max_attempts=self.max_attempts)

        if response and "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
            self._run_hook('on_canvas_run_success', canvas_id=self.canvas_id, content_type=output_type)
            if output_type == 'dataframe':
                return self._json_to_dataframe(content)
            return content
        
        self._run_hook('on_canvas_run_failure', canvas_id=self.canvas_id, attempts=attempts)
        return None

    def run_batch(self, inputs, output_type='json', max_workers=5, use_cache=True):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        self._run_hook('on_batch_start', inputs_count=len(inputs))
        
        def process_input(index, input_data):
            self._run_hook('on_batch_item_start', index=index, input=input_data)
            result = self.run(output_type=output_type, use_cache=use_cache, **input_data)
            self._run_hook('on_batch_item_end', index=index, input=input_data, result=result)
            return {'input': input_data.get('name', f'input_{index}'), 'result': result}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_input, i, input_data) for i, input_data in enumerate(inputs)]
            results = []
            for future in as_completed(futures):
                results.append(future.result())

        self._run_hook('on_batch_end', results_count=len(results))
        return results

    def _json_to_dataframe(self, json_data):
        def flatten_json(data, prefix=''):
            items = {}
            for key, value in data.items():
                new_key = f"{prefix}{key}"
                if isinstance(value, dict):
                    items.update(flatten_json(value, f"{new_key}_"))
                elif isinstance(value, list):
                    items[new_key] = json.dumps(value)
                else:
                    items[new_key] = value
            return items

        def process_json(data):
            if isinstance(data, dict):
                return [flatten_json(data)]
            elif isinstance(data, list):
                return [flatten_json(item) if isinstance(item, dict) else item for item in data]

        processed_data = process_json(json_data)
        df = pd.DataFrame(processed_data)

        # Expand columns that contain JSON strings (lists or list of objects)
        for column in df.columns:
            try:
                df[column] = df[column].apply(json.loads)
                if df[column].apply(lambda x: isinstance(x, list)).all():
                    if isinstance(df[column].iloc[0][0], dict):
                        # Handle list of objects
                        expanded_df = pd.json_normalize(df[column].explode().tolist())
                        expanded_df.index = df.index.repeat(df[column].str.len())
                        expanded_df.columns = [f"{column}_{subcol}" for subcol in expanded_df.columns]
                        df = df.drop(columns=[column]).join(expanded_df)
                    else:
                        # Handle simple lists
                        df = df.explode(column)
            except:
                pass

        return df


# EXAMPLE USAGE
# from tela.tela import TelaClient, file

# TELA_API_KEY = "Your API KEY"
# tela_client = TelaClient(TELA_API_KEY)

# canvas_id = "2b57f4ae-c48e-4883-a0a4-130a573ffdfc"
# canvas = tela_client.new_canvas(canvas_id, expected_input=['document'])

# FILE_NAME = "./Cartao CNPJ produtor.pdf"
# canvas.run(document=file(FILE_NAME))