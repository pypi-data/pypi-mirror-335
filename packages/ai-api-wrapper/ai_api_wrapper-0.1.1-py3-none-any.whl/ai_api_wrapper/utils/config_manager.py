import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv, find_dotenv
from ai_api_wrapper.utils.logger import logger
from ai_api_wrapper.utils.constants import PROJECT_ROOT


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()



class ConfigManager:
    """配置管理器"""
    _instance = None
    _config: Dict[str, Any] = {}
    _initialized = False
    _config_dir = None
    
    def __new__(cls, config_dir: str = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._config_dir = config_dir
            cls._config = {}  # 重置配置
            cls._initialized = False
        return cls._instance
    
    def __init__(self, config_dir: str = None):
        if not self._initialized:
            self._config_dir = config_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            self._config = {}  # 重置配置
            self._load_config()
            self._load_env_config()
            self._initialized = True
    
    def _log_warning(self, message: str):
        """记录警告日志"""
        logger.warning(message)
    
    def _log_error(self, message: str):
        """记录错误日志"""
        logger.error(message)
    
    def _log_info(self, message: str):
        """记录信息日志"""
        logger.info(message)
    
    def _get_config_paths(self) -> List[str]:
        """获取配置文件路径列表，按优先级排序"""
        return [
            os.path.join(self._config_dir, 'config.json')  # 主配置文件
        ]
    
    def _load_env_config(self):
        """从 .env 文件加载配置"""
        # 加载 .env 文件
        load_dotenv(find_dotenv())
        
        # 获取所有环境变量
        env_config = {}
        
        # 处理 AI 服务配置
        for provider in ['grok', 'openai', 'anthropic', 'azure', 'google', 'deepseek', 'openrouter']:
            provider_config = {}
            api_key = os.getenv(f'{provider.upper()}_API_KEY')
            if api_key:
                if provider not in self._config:
                    self._config[provider] = {}
                self._config[provider]['api_key'] = api_key
                
            base_url = os.getenv(f'{provider.upper()}_BASE_URL')
            if base_url:
                if provider not in self._config:
                    self._config[provider] = {}
                self._config[provider]['base_url'] = base_url
    
    def is_loaded(self) -> bool:
        """检查配置是否已加载"""
        return bool(self._config)
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 加载配置文件
            config_loaded = False
            for config_path in self._get_config_paths():
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if not config_loaded:
                            self._config = json.load(f)
                            config_loaded = True
                        else:
                            # 合并配置
                            self._merge_config(json.load(f))
            
            if not config_loaded:
                self._log_warning("No configuration files found, using default settings")
                self._create_default_config()
            
        except Exception as e:
            self._log_error(f"Failed to load configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        try:
            # 创建一个最小配置
            self._config = {
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "timeout": 30.0,
                    "max_retries": 3,
                    "models": {
                        "deepseek-chat": {
                            "max_tokens": 4000,
                            "temperature": 0.7
                        }
                    }
                },
                "logging": {
                    "level": "INFO",
                    "file": "app.log"
                }
            }
            self._save_default_config()
            
        except Exception as e:
            self._log_error(f"Failed to create default configuration: {str(e)}")
    
    def _save_default_config(self):
        """保存默认配置"""
        try:
            # 创建配置目录
            os.makedirs(self._config_dir, exist_ok=True)
            
            # 保存配置
            config_path = os.path.join(self._config_dir, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            self._log_info("Configuration saved")
                
        except Exception as e:
            self._log_error(f"Failed to save configuration: {str(e)}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """递归合并配置"""
        for key, value in new_config.items():
            if key in self._config:
                if isinstance(self._config[key], dict) and isinstance(value, dict):
                    self._merge_config_recursive(self._config[key], value)
                else:
                    self._config[key] = value
            else:
                self._config[key] = value
    
    def _merge_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]):
        """递归合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config_recursive(target[key], value)
            else:
                target[key] = value
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取指定提供商的配置"""
        if provider not in self._config:
            raise KeyError(f"Provider '{provider}' not found")
        return self._config[provider]
    
    def get_model_config(self, provider: str, model_name: str) -> Dict[str, Any]:
        """获取指定模型的配置
        
        Args:
            provider: 提供商名称
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 模型配置
        """
        if provider not in self._config:
            raise KeyError(f"Provider '{provider}' not found")
            
        # 默认的模型配置
        default_model_config = {
            "max_tokens": 4000,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": None
        }
        
        # 如果找不到特定模型的配置，返回默认配置
        provider_config = self._config[provider]
        if not isinstance(provider_config, dict) or "models" not in provider_config or model_name not in provider_config["models"]:
            logger.debug(f"No specific config found for model '{model_name}' in provider '{provider}', using default config")
            return default_model_config
            
        # 合并默认配置和特定模型的配置
        model_config = default_model_config.copy()
        model_config.update(provider_config["models"][model_name])
        return model_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
        self._save_default_config()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def update(self, config: Dict[str, Any]):
        """更新配置"""
        self._merge_config(config)
        self._save_default_config()
    
    def get_enabled_providers(self) -> List[str]:
        """获取已启用的提供商列表"""
        providers = []
        for name, config in self._config.items():
            if isinstance(config, dict) and config.get('enabled', False):
                providers.append(name)
        return providers 