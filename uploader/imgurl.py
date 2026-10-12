import json
import requests
from typing import Optional

from .base import BaseUploader, UploadResult


class ImgURLUploader(BaseUploader):
    """
    ImgURL 图床上传器
    用于上传图片到 ImgURL API (v3)
    """

    def __init__(self, config: dict):
        """
        初始化 ImgURL 上传器

        Args:
            config: 配置字典，包含 ImgURL 相关配置
        """
        super().__init__(config)
        imgurl_config = config.get('imgurl', {})

        self.token = imgurl_config.get('token')
        self.base_url = imgurl_config.get('base_url', 'https://www.imgurl.org') + '/api/v3/upload'
        self.default_album_id = imgurl_config.get('album_id', 0)

        if not self.token:
            raise ValueError("ImgURL 配置中缺少 token")

        # API 要求 Bearer 前缀
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def upload(
        self,
        file_path: str,
        title: str = "",
        album_id: Optional[int] = None,
        dedup: bool = True,
        watermark: bool = False,
        compress: bool = False,
    ) -> UploadResult:
        """
        上传本地文件到 ImgURL

        Args:
            file_path: 要上传的文件路径
            title: 文件标题（ImgURL 不直接支持 title，会作为 params 中的附加信息保留）
            album_id: 相册ID（可选，不提供时使用配置中的默认值）
            dedup: 是否去重，默认 True
            watermark: 是否启用文字水印，默认 False
            compress: 是否压缩图片，默认 False

        Returns:
            UploadResult: 上传结果对象
        """
        try:
            final_album_id = album_id if album_id is not None else self.default_album_id

            # 构造 params 字段（JSON 字符串）
            params = {
                "dedup": dedup,
                "album_id": final_album_id,
                "watermark": watermark,
                "compress": compress,
            }

            # 准备表单数据
            with open(file_path, 'rb') as file:
                files = {
                    'file': file
                }
                data = {
                    'params': json.dumps(params)
                }

                # ===== 加这几行日志 =====
                print(f"  → 请求地址: {self.base_url}")
                print(f"  → 请求头: {self.headers}")
                print(f"  → 表单参数: {data}")
                print(f"  → 超时: 30")
                # =======================

                # 发送请求
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=30
                )

            # 检查响应
            if response.status_code == 200:
                result = response.json()
                # code 非 200 视为失败
                if result.get("code") == 200:
                    image_url = result.get("data", {}).get("url", "")
                    if image_url:
                        print(f'  ✅ ImgURL 上传成功: {image_url}')
                        return UploadResult(
                            file_path=file_path,
                            title=title,
                            success=True,
                            image_url=image_url
                        )
                    else:
                        error_msg = f"ImgURL 响应中未找到 url: {result}"
                else:
                    error_msg = f"ImgURL 上传失败: {result.get('msg', 'unknown error')} (code={result.get('code')})"
            else:
                error_msg = f"ImgURL 上传失败，状态码: {response.status_code}, 响应: {response.text}"

            print(f'  ❌ {error_msg}')
            return UploadResult(
                file_path=file_path,
                title=title,
                success=False,
                error_msg=error_msg
            )

        except Exception as e:
            error_msg = f"ImgURL 上传失败: {str(e)}"
            print(f'  ❌ {error_msg}')
            return UploadResult(
                file_path=file_path,
                title=title,
                success=False,
                error_msg=error_msg
            )

    def upload_from_url(
        self,
        image_url: str,
        title: str = "",
        album_id: Optional[int] = None,
        dedup: bool = True,
        watermark: bool = False,
        compress: bool = False,
    ) -> UploadResult:
        """
        通过 URL 上传图片到 ImgURL（便捷方法）

        注意：ImgURL v3 官方文档只说明 file 字段为文件，
        若服务端不支持 URL 作为 file 值，此方法可能失败。
        如需 URL 上传，建议先下载到本地再调用 upload()。

        Args:
            image_url: 图片的 URL
            title: 文件标题
            album_id: 相册ID（可选）
            dedup: 是否去重，默认 True
            watermark: 是否启用文字水印，默认 False
            compress: 是否压缩图片，默认 False

        Returns:
            UploadResult: 上传结果对象
        """
        try:
            final_album_id = album_id if album_id is not None else self.default_album_id

            params = {
                "dedup": dedup,
                "album_id": final_album_id,
                "watermark": watermark,
                "compress": compress,
            }

            data = {
                'file': image_url,  # 部分实现支持直接传 URL 字符串
                'params': json.dumps(params),
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    result_url = result.get("data", {}).get("url", "")
                    if result_url:
                        return UploadResult(
                            file_path=image_url,
                            title=title,
                            success=True,
                            image_url=result_url
                        )
                    else:
                        error_msg = f"ImgURL 响应中未找到 url: {result}"
                else:
                    error_msg = f"ImgURL URL上传失败: {result.get('msg', 'unknown error')} (code={result.get('code')})"
            else:
                error_msg = f"ImgURL URL上传失败，状态码: {response.status_code}"

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
                error_msg=f"ImgURL URL上传失败: {str(e)}"
            )