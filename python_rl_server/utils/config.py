"""
Configuration Utilities
TÜBİTAK İP-2 AI Bot System
"""

import os
from typing import Any, Dict, Optional
import yaml


_config_cache: Dict[str, Dict] = {}


def load_config(config_path: str, reload: bool = False) -> Dict[str, Any]:
    """
    YAML config dosyasını yükle.

    Args:
        config_path: Config dosyası yolu
        reload: True ise cache'i ignore et

    Returns:
        Config dictionary
    """
    global _config_cache

    if not reload and config_path in _config_cache:
        return _config_cache[config_path]

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    _config_cache[config_path] = config
    return config


def get_config(
    config_name: str,
    config_dir: str = "./configs",
    default: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Config dosyasını isimle yükle.

    Args:
        config_name: Config ismi (uzantısız)
        config_dir: Config dizini
        default: Dosya bulunamazsa döndürülecek default

    Returns:
        Config dictionary
    """
    config_path = os.path.join(config_dir, f"{config_name}.yaml")

    if not os.path.exists(config_path):
        # .yml uzantısını da dene
        config_path = os.path.join(config_dir, f"{config_name}.yml")

    if not os.path.exists(config_path):
        if default is not None:
            return default
        raise FileNotFoundError(f"Config not found: {config_name}")

    return load_config(config_path)


def merge_configs(*configs: Dict) -> Dict[str, Any]:
    """
    Birden fazla config'i birleştir.

    Sonraki config'ler önceki değerleri override eder.
    """
    result = {}
    for config in configs:
        _deep_merge(result, config)
    return result


def _deep_merge(base: Dict, update: Dict) -> None:
    """Recursive dict merge."""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


class ConfigManager:
    """Config yöneticisi singleton."""

    _instance: Optional['ConfigManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._configs = {}
        return cls._instance

    def load(self, name: str, path: str) -> Dict:
        """Config yükle ve cache'le."""
        self._configs[name] = load_config(path)
        return self._configs[name]

    def get(self, name: str) -> Optional[Dict]:
        """Cache'den config al."""
        return self._configs.get(name)

    def get_value(self, name: str, key: str, default: Any = None) -> Any:
        """Config'den değer al (dot notation destekli)."""
        config = self._configs.get(name, {})

        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value
