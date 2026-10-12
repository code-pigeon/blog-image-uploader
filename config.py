import yaml
from pathlib import Path

def load_config(config_path="config.yaml"):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"无法加载配置文件 - {e}")

def get_uploader_config(config, service_name):
    """获取指定上传器的配置"""
    return config.get(service_name, {})