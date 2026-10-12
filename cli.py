import argparse
from pathlib import Path

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='图片上传工具 - 支持上传到多个图床',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 默认模式 - 使用文件名作为标题，上传到所有图床
  imgul image1.jpg image2.png
  
  # 使用-t参数指定标题
  imgul -t "图片1.jpg" "美丽的风景" "图片2.png" "城市夜景"
  
  # 只上传到指定图床
  imgul image1.jpg -i jpg_dog cloudflare
  imgul image1.jpg image2.png -i jpg_dog
  imgul image1.jpg -i cloudflare local
  
  # 强制更新图片表格（不询问确认）
  imgul -f image1.jpg image2.png
        '''
    )
    
    parser.add_argument(
        'files', 
        nargs='*',
        help='要上传的图片文件路径'
    )
    
    parser.add_argument(
        '-t', '--titles',
        action='store_true',
        help='使用标题模式，后面接 文件路径 标题 文件路径 标题 的成对形式'
    )
    
    parser.add_argument(
        '-i', '--include',
        nargs='+',
        choices=['local', 'imgurl', 'jpg_dog', 'cloudflare'],
        default=['local', 'imgurl', 'cloudflare'],
        help='指定要上传的图床服务（可选: local, imgurl, jpg_dog, cloudflare）'
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='强制更新图片表格，如果标题已存在则直接覆盖，不询问确认'
    )
    
    args = parser.parse_args()
    
    # 处理文件标题对
    args.file_title_pairs = _process_file_args(args.files, args.titles)
    
    if not args.file_title_pairs:
        print("错误: 没有有效的文件可上传")
        exit(1)
    
    return args

def _process_file_args(files, use_titles):
    """处理文件参数，返回文件路径和标题的配对列表"""
    file_title_pairs = []
    
    if use_titles:
        # 标题模式：参数应该是成对的
        if len(files) % 2 != 0:
            print("错误: 在标题模式下，参数数量必须是偶数（文件路径和标题成对出现）")
            exit(1)
        
        for i in range(0, len(files), 2):
            file_path = files[i]
            title = files[i + 1]
            
            if not Path(file_path).exists():
                print(f"警告: 文件不存在 - {file_path}")
                continue
                
            file_title_pairs.append((file_path, title))
    else:
        # 默认模式：使用文件名stem作为标题
        for file_path in files:
            if not Path(file_path).exists():
                print(f"警告: 文件不存在 - {file_path}")
                continue
                
            title = Path(file_path).stem
            file_title_pairs.append((file_path, title))
    
    return file_title_pairs