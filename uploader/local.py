from .base import BaseUploader, UploadResult

class LocalUploader(BaseUploader):
    """本地路径上传器"""
    
    def upload(self, file_path, title=""):
        try:
            filename = self.get_filename(file_path)
            image_url = f"{self.config['local']}{filename}"
            return UploadResult(file_path, title, True, image_url)
        except Exception as e:
            return UploadResult(file_path, title, False, error_msg=str(e))