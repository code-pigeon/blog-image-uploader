import boto3
from botocore.config import Config
import os
from typing import Optional

from .base import BaseUploader, UploadResult


class CloudflareUploader(BaseUploader):
    """
    Cloudflare R2 上传器
    使用 boto3 的简单上传器
    """
    
    def __init__(self, config: dict):
        """
        初始化 Cloudflare 上传器
        
        Args:
            config: 配置字典，包含 Cloudflare 相关配置
        """
        super().__init__(config)
        cloudflare_config = config.get('cloudflare', {})
        
        self.account_id = cloudflare_config.get('account_id')
        self.access_key = cloudflare_config.get('access_key')
        self.secret_key = cloudflare_config.get('secret_key')
        self.bucket_name = cloudflare_config.get('bucket_name')
        self.public_domain = cloudflare_config.get('public_domain')
        
        # 验证必要配置
        if not all([self.account_id, self.access_key, self.secret_key, self.bucket_name]):
            raise ValueError("Cloudflare 配置不完整，请检查 account_id、access_key、secret_key 和 bucket_name")
        
        # 如果没有提供公共域名，使用默认格式
        if not self.public_domain:
            self.public_domain = f'https://pub-{self.account_id}.r2.dev'
        
        # 初始化 S3 客户端
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
    
    def upload(self, file_path: str, title: str = "") -> UploadResult:
        """
        上传文件到 Cloudflare R2
        
        Args:
            file_path: 要上传的文件路径
            title: 文件标题（用于生成结果）
            
        Returns:
            UploadResult: 上传结果对象
        """
        try:
            # 使用标题作为对象名，如果没有标题则使用文件名
            if title:
                # 清理标题，移除可能的不合法字符
                safe_title = "".join(c for c in title if c.isalnum() or c in ('-', '_')).rstrip()
                file_ext = os.path.splitext(file_path)[1]
                object_name = f"{safe_title}{file_ext}"
            else:
                object_name = self.get_filename(file_path)
            
            # 上传文件
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                object_name
            )
            
            # 生成公共URL
            public_url = f'{self.public_domain}/{object_name}'
            
            print(f'  ✅ Cloudflare 上传成功: {public_url}')
            return UploadResult(
                file_path=file_path,
                title=title,
                success=True,
                image_url=public_url
            )
            
        except Exception as e:
            error_msg = f'Cloudflare 上传失败: {str(e)}'
            print(f'  ❌ {error_msg}')
            return UploadResult(
                file_path=file_path,
                title=title,
                success=False,
                error_msg=error_msg
            )

# # 🎯 使用示例 - 使用正确的公共域名
# if __name__ == "__main__":
#     # 从 Cloudflare 面板获取这个公共域名
#     correct_public_domain = "https://pub-026ecfceb63744219eb65ba54fa5359f.r2.dev"  # 替换为你的实际公共域名
    
#     uploader = CloudflareUploader(
#         account_id=,
#         access_key,
#         secret_key,
#         bucket_name,
#         public_domain=correct_public_domain  # 传入正确的公共域名
#     )
    
#     url = uploader.upload("C:/Users/10514/Downloads/Snipaste_2025-10-20_16-17-50.jpg")
#     print(f"图片链接: {url}")