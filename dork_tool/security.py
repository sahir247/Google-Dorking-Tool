"""
Security and Credential Management module using Fernet AES encryption.
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Tuple, Optional, Any

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class CredentialManager:
    """
    Manages API credentials securely using Fernet symmetric encryption.
    Stores encrypted credentials in ~/.google_dorking_tool/creds.dat
    """

    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".google_dorking_tool")
        self.cred_file = os.path.join(self.config_dir, "creds.dat")
        self.key_file = os.path.join(self.config_dir, "master.key")
        self._ensure_config_dir()
        self._fernet = self._init_fernet()

    def _ensure_config_dir(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Could not create config dir: {e}")

    def _init_fernet(self) -> Optional[Any]:
        if not CRYPTO_AVAILABLE:
            return None
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, "rb") as f:
                    key = f.read().strip()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(key)
                try:
                    if hasattr(os, "chmod"):
                        os.chmod(self.key_file, 0o600)
                except Exception:
                    pass
            return Fernet(key)
        except Exception as e:
            print(f"[ERROR] Fernet initialization failed: {e}")
            return None

    def save(self, api_key: str, cse_id: str) -> bool:
        """Encrypts and persists credentials."""
        data = {
            "api_key": api_key.strip(),
            "cse_id": cse_id.strip(),
            "updated_at": datetime.now().isoformat()
        }
        json_str = json.dumps(data)

        try:
            if self._fernet:
                encrypted = self._fernet.encrypt(json_str.encode("utf-8"))
                with open(self.cred_file, "wb") as f:
                    f.write(encrypted)
            else:
                encoded = base64.b64encode(json_str.encode("utf-8"))
                with open(self.cred_file, "wb") as f:
                    f.write(encoded)

            if hasattr(os, "chmod"):
                try:
                    os.chmod(self.cred_file, 0o600)
                except Exception:
                    pass
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save credentials: {e}")
            return False

    def load(self) -> Tuple[str, str]:
        """Loads and decrypts credentials with fallback to environment variables."""
        # 1. Environment variables take precedence
        env_key = os.environ.get("GOOGLE_API_KEY", "").strip()
        env_cse = os.environ.get("GOOGLE_CSE_ID", "").strip()
        if env_key and env_cse:
            return env_key, env_cse

        # 2. Local encrypted storage
        if not os.path.exists(self.cred_file):
            return "", ""

        try:
            with open(self.cred_file, "rb") as f:
                content = f.read().strip()

            if not content:
                return "", ""

            if self._fernet:
                try:
                    decrypted = self._fernet.decrypt(content).decode("utf-8")
                    data = json.loads(decrypted)
                    return data.get("api_key", ""), data.get("cse_id", "")
                except Exception:
                    pass

            try:
                decrypted = base64.b64decode(content).decode("utf-8")
                data = json.loads(decrypted)
                return data.get("api_key", ""), data.get("cse_id", "")
            except Exception:
                return "", ""

        except Exception as e:
            print(f"[ERROR] Failed to load credentials: {e}")
            return "", ""

    def clear(self) -> bool:
        """Deletes encrypted credential file."""
        try:
            if os.path.exists(self.cred_file):
                os.remove(self.cred_file)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to clear credentials: {e}")
            return False

    @staticmethod
    def validate(api_key: str, cse_id: str) -> Tuple[bool, str]:
        """Tests credentials against the Google Custom Search API endpoint."""
        api_key = api_key.strip()
        cse_id = cse_id.strip()
        if not api_key or not cse_id:
            return False, "API Key and CSE ID cannot be empty."

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": "test",
            "num": 1
        }
        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                return True, "API connection verified successfully."
            elif resp.status_code == 400:
                return False, "HTTP 400: Invalid API Key or Custom Search Engine ID."
            elif resp.status_code == 403:
                return False, "HTTP 403: Forbidden - Custom Search API not enabled or quota exceeded."
            else:
                return False, f"API test returned HTTP status {resp.status_code}: {resp.text[:120]}"
        except requests.exceptions.Timeout:
            return False, "API connection test timed out."
        except requests.exceptions.RequestException as e:
            return False, f"Network error during verification: {str(e)}"
