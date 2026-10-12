"""
图片上传工具主入口
"""
from cli import parse_args
from config import load_config
from uploader import UploaderManager
from image_table import update_image_table

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    config = load_config()
    
    # 初始化上传管理器
    upload_manager = UploaderManager(config)
    
    # 上传图片
    results = upload_manager.upload_files(
        file_title_pairs=args.file_title_pairs,
        services=args.include
    )
    
    # 显示结果
    upload_manager.print_results(results)
    
    # 更新图片表格
    if results.success_files:
        update_image_table(
            config=config,
            file_title_pairs=args.file_title_pairs,
            results=results,
            force_update=args.force
        )

if __name__ == "__main__":
    main()