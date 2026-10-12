from .base import UploadResults, UploadResult
from .jpg_dog import JpgDogUploader
from .cloudflare import CloudflareUploader
from .local import LocalUploader
from .imgurl import ImgURLUploader   # 新增

class UploaderManager:
    """上传器管理器 - 核心类，管理所有上传器"""
    
    # 在这里定义上传顺序！想要调整顺序只需修改这个字典
    UPLOADER_CLASSES = {
        'local': LocalUploader,
        'imgurl': ImgURLUploader,   # 新增
        'jpg_dog': JpgDogUploader, 
        'cloudflare': CloudflareUploader,
    }
    
    def __init__(self, config):
        self.config = config
        self.uploaders = self._init_uploaders()
    
    def _init_uploaders(self):
        """初始化所有上传器"""
        uploaders = {}
        for service_name, uploader_class in self.UPLOADER_CLASSES.items():
            try:
                uploaders[service_name] = uploader_class(self.config)
                print(f"  ✓ 初始化 {service_name} 上传器")
            except Exception as e:
                print(f"  ⚠ 初始化 {service_name} 上传器失败 - {e}")
        return uploaders
    
    def upload_files(self, file_title_pairs, services):
        """上传文件到指定服务"""
        results = UploadResults()
        
        for file_path, title in file_title_pairs:
            print(f"\n📤 正在上传: {file_path} (标题: {title})")
            
            # 按指定顺序上传到各个服务
            image_urls = []
            
            # 需要传 album_id 的服务
            ALBUM_SERVICES = ('jpg_dog', 'imgurl')

            for service in services:
                if service in self.uploaders:
                    uploader = self.uploaders[service]

                    if service in ALBUM_SERVICES:
                        album_id = self.config.get(service, {}).get('album_id')
                        result = uploader.upload(
                            file_path=file_path,
                            title=title,
                            album_id=album_id
                        )
                    else:
                        result = uploader.upload(file_path=file_path, title=title)

                    if result.success:
                        image_urls.append(result.image_url)
            
            # 生成最终结果
            if image_urls:
                data_url = ';'.join(image_urls)
                final_result = UploadResult(
                    file_path=file_path, 
                    title=title, 
                    success=True, 
                    image_url=data_url
                )
                results.add(final_result)
                print(f"✅ 上传完成: {file_path}")
            else:
                final_result = UploadResult(
                    file_path=file_path, 
                    title=title, 
                    success=False, 
                    error_msg="所有服务均上传失败"
                )
                results.add(final_result)
                print(f"❌ 上传失败: {file_path}")
        
        return results
    
    def print_results(self, results):
        """打印上传结果"""
        print("\n" + "="*60)
        print("📊 上传结果汇总")
        print("="*60)
        
        # 成功文件
        print(f"\n✅ 成功文件 ({len(results.success_files)}个):")
        for result in results.success_files:
            print(f"  📁 {result.file_path}")
            print(f"     🔗 {result.image_url}")
        
        # 失败文件  
        print(f"\n❌ 失败文件 ({len(results.failed_files)}个):")
        for result in results.failed_files:
            print(f"  📁 {result.file_path}")
            print(f"     💥 {result.error_msg}")
        
        # 图片标签
        print(f"\n🏷️ 图片标签 ({len(results.img_tags)}个):")
        for tag in results.img_tags:
            print(f"  {tag}")
        
        print(f"\n📈 总计: {len(results.success_files)}/{len(results.results)} 个文件上传成功")