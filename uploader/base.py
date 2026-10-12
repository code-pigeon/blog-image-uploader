from abc import ABC, abstractmethod
from pathlib import Path

class UploadResult:
    """上传结果类"""
    def __init__(self, file_path, title, success=True, image_url="", error_msg=""):
        self.file_path = file_path
        self.title = title
        self.success = success
        self.image_url = image_url
        self.error_msg = error_msg
        self.img_tag = self._generate_img_tag() if success else ""
    
    def _generate_img_tag(self):
        """生成图片标签"""
        return f'<img data-url="{{{{image_table.{self.title}}}}}" title="{self.title}" alt="图片加载失败：{self.title}"/>'

class UploadResults:
    """上传结果集合"""
    def __init__(self):
        self.results = []
    
    def add(self, result):
        self.results.append(result)
    
    @property
    def success_files(self):
        return [r for r in self.results if r.success]
    
    @property
    def failed_files(self):
        return [r for r in self.results if not r.success]
    
    @property
    def img_tags(self):
        return [r.img_tag for r in self.results if r.success]
    
    @property
    def data_urls(self):
        """获取成功文件的数据URL（标题和URL的对应关系）"""
        return [(r.title, r.image_url) for r in self.results if r.success]

class BaseUploader(ABC):
    """上传器基类"""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def upload(self, file_path, title=""):
        """上传文件，返回图片URL"""
        pass
    
    def get_filename(self, file_path):
        """从文件路径中提取文件名"""
        return Path(file_path).name