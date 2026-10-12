import requests
from typing import Optional

from .base import BaseUploader, UploadResult


class JpgDogUploader(BaseUploader):
    """
    JpgDog 图床上传器
    用于上传图片到 jpg.dog API
    """
    
    def __init__(self, config: dict):
        """
        初始化 JpgDog 上传器
        
        Args:
            config: 配置字典，包含 JpgDog 相关配置
        """
        super().__init__(config)
        jpg_dog_config = config.get('jpg_dog', {})
        
        self.api_key = jpg_dog_config.get('api_key')
        self.base_url = "https://jpg.dog/api/1/upload"  # 使用正确的 API 版本
        self.default_album_id = jpg_dog_config.get('album_id')
        
        if not self.api_key:
            raise ValueError("JpgDog 配置中缺少 api_key")
        
        self.headers = {
            "X-API-Key": self.api_key
        }
    
    def upload(
        self, 
        file_path: str, 
        title: str = "",
        album_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        category_id: Optional[str] = None,
        width: Optional[int] = None,
        expiration: Optional[str] = None,
        nsfw: Optional[int] = 0,
        format: str = "json"
    ) -> UploadResult:
        """
        上传本地文件到 JpgDog
        
        Args:
            file_path: 要上传的文件路径
            title: 文件标题
            album_id: 相册ID（可选，不提供时使用配置中的默认值）
            description: 文件描述（可选）
            tags: 标签，逗号分隔（可选）
            category_id: 分类ID（可选）
            width: 目标宽度（可选）
            expiration: 过期时间，如PT5M（5分钟）或P3D（3天）（可选）
            nsfw: 是否不适合工作场所[0,1]（可选）
            format: 返回格式[json, redirect, txt]（可选）
            
        Returns:
            UploadResult: 上传结果对象
        """
        try:
            # 使用配置的相册ID或传入的相册ID
            final_album_id = album_id or self.default_album_id
            
            # 准备表单数据
            with open(file_path, 'rb') as file:
                files = {
                    'source': file
                }
                
                data = {}
                if final_album_id:
                    data['album_id'] = final_album_id
                if title:
                    data['title'] = title
                if description:
                    data['description'] = description
                if tags:
                    data['tags'] = tags
                if category_id:
                    data['category_id'] = category_id
                if width:
                    data['width'] = str(width)
                if expiration:
                    data['expiration'] = expiration
                if nsfw is not None:
                    data['nsfw'] = str(nsfw)
                if format:
                    data['format'] = format
                
                # 发送请求
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=30  # 添加超时设置
                )
            
            # 检查响应
            if response.status_code == 200:
                image_url = self._parse_response(response, format)
                print(f'  ✅ JpgDog 上传成功: {image_url}')
                return UploadResult(
                    file_path=file_path,
                    title=title,
                    success=True,
                    image_url=image_url
                )
            else:
                error_msg = f"JpgDog 上传失败，状态码: {response.status_code}, 响应: {response.text}"
                print(f'  ❌ {error_msg}')
                return UploadResult(
                    file_path=file_path,
                    title=title,
                    success=False,
                    error_msg=error_msg
                )
                
        except Exception as e:
            error_msg = f"JpgDog 上传失败: {str(e)}"
            print(f'  ❌ {error_msg}')
            return UploadResult(
                file_path=file_path,
                title=title,
                success=False,
                error_msg=error_msg
            )
    
    def _parse_response(self, response: requests.Response, format: str) -> str:
        """
        解析 JpgDog API 响应
        
        Args:
            response: 请求响应对象
            format: 响应格式
            
        Returns:
            图片URL
            
        Raises:
            Exception: 解析失败时抛出
        """
        if format == "json":
            result = response.json()
            if "image" in result and "url" in result["image"]:
                return result["image"]["url"]
            elif "url" in result:
                return result["url"]
            else:
                raise Exception(f"响应中未找到URL: {result}")
        elif format == "txt":
            url = response.text.strip()
            if url.startswith("http"):
                return url
            else:
                raise Exception(f"无效的URL响应: {url}")
        else:  # redirect格式
            redirect_url = response.headers.get('Location', '')
            if redirect_url and redirect_url.startswith("http"):
                return redirect_url
            else:
                raise Exception(f"无效的重定向URL: {redirect_url}")
    
    def upload_from_url(
        self,
        image_url: str,
        title: str = "",
        album_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        category_id: Optional[str] = None,
        width: Optional[int] = None,
        expiration: Optional[str] = None,
        nsfw: Optional[int] = 0,
        format: str = "json"
    ) -> UploadResult:
        """
        通过URL上传图片到 JpgDog（便捷方法）
        
        Args:
            image_url: 图片的URL
            title: 文件标题
            album_id: 相册ID（可选）
            description: 文件描述（可选）
            tags: 标签，逗号分隔（可选）
            category_id: 分类ID（可选）
            width: 目标宽度（可选）
            expiration: 过期时间（可选）
            nsfw: 是否不适合工作场所[0,1]（可选）
            format: 返回格式[json, redirect, txt]（可选）
            
        Returns:
            UploadResult: 上传结果对象
        """
        try:
            final_album_id = album_id or self.default_album_id
            
            data = {
                'source': image_url
            }
            
            if final_album_id:
                data['album_id'] = final_album_id
            if title:
                data['title'] = title
            if description:
                data['description'] = description
            if tags:
                data['tags'] = tags
            if category_id:
                data['category_id'] = category_id
            if width:
                data['width'] = str(width)
            if expiration:
                data['expiration'] = expiration
            if nsfw is not None:
                data['nsfw'] = str(nsfw)
            if format:
                data['format'] = format
            
            # 发送请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=data,
                timeout=30
            )
            
            # 检查响应
            if response.status_code == 200:
                result_url = self._parse_response(response, format)
                return UploadResult(
                    file_path=image_url,  # 注意：这里使用 URL 作为文件路径
                    title=title,
                    success=True,
                    image_url=result_url
                )
            else:
                error_msg = f"JpgDog URL上传失败，状态码: {response.status_code}"
                return UploadResult(
                    file_path=image_url,
                    title=title,
                    success=False,
                    error_msg=error_msg
                )
                
        except Exception as e:
            return UploadResult(
                file_path=image_url,
                title=title,
                success=False,
                error_msg=f"JpgDog URL上传失败: {str(e)}"
            )

# # 使用示例
# if __name__ == "__main__":
#     # 初始化上传器（替换为您的API密钥）
#     uploader = JpgDogUploader("")
    
#     # 示例1：上传本地文件到指定相册
#     image_url = uploader.upload(
#         file_path="C:/Users/10514/Downloads/Snipaste_2025-10-20_16-18-29.jpg",
#         album_id="blog",  # 替换为您的相册ID
#         title="Snipaste_2025-10-20_16-18-29"
#     )
    
#     # 直接检查返回的是URL还是错误信息
#     if image_url.startswith("http"):
#         print(f"上传成功！图片URL: {image_url}")
#     else:
#         print(f"上传失败: {image_url}")