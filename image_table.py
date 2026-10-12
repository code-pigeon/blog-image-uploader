import yaml
from pathlib import Path

def load_image_table(config):
    """加载图片表格"""
    table_path = config.get('image-table-path')
    if not table_path or not Path(table_path).exists():
        return {}
    
    try:
        with open(table_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"警告: 无法加载图片表格 - {e}")
        return {}

def save_image_table(config, image_table):
    """保存图片表格"""
    table_path = config.get('image-table-path')
    if not table_path:
        print("错误: 配置文件中未指定 image-table-path")
        return False
    
    try:
        with open(table_path, 'w', encoding='utf-8') as f:
            yaml.dump(image_table, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        print(f"错误: 无法保存图片表格 - {e}")
        return False

def update_image_table(config, file_title_pairs, results, force_update=False):
    """更新图片表格"""
    image_table = load_image_table(config)

    success_data = results.data_urls

    if not success_data:
        print("没有成功上传的图片，无需更新图片表格")
        return True

    # 检查冲突
    need_confirmation = False
    conflicting_titles = []

    for title, data_url in success_data:
        if title in image_table:
            need_confirmation = True
            conflicting_titles.append(title)

    action = "overwrite"
    insert_pos = 0   # 默认插到最前面

    if need_confirmation and not force_update:
        print("\n" + "="*50)
        print("警告: 以下标题在图片表格中已存在:")
        for title in conflicting_titles:
            print(f"  - {title}")

        while True:
            response = input("\n请选择操作: [y]覆盖 / [n]跳过 / [a]追加: ").strip().lower()
            if response in ['y', 'yes', '是']:
                action = "overwrite"
                break
            elif response in ['n', 'no', '否']:
                action = "skip"
                break
            elif response in ['a', 'append', '追加']:
                action = "append"
                break
            else:
                print("请输入 y、n 或 a")

        if action == "skip":
            print("取消更新图片表格")
            return True

        # 追加时再问插入位置
        if action == "append":
            while True:
                pos_input = input(
                    "插入位置 (0=最前, 1=第二位, ... 直接回车=默认插到最前): "
                ).strip()
                if pos_input == "":
                    insert_pos = 0
                    break
                if pos_input.isdigit():
                    insert_pos = int(pos_input)
                    break
                print("请输入非负整数，或直接回车")

    # 更新表格
    updated_count = 0
    new_count = 0
    appended_count = 0

    for title, data_url in success_data:
        if title in image_table:
            if action == "overwrite":
                image_table[title] = data_url
                updated_count += 1
                print(f"  ✓ 覆盖图片表格: {title}")
            elif action == "append":
                existing = image_table[title]

                # 统一按 ';' 拆成列表，并去掉空项
                if isinstance(existing, list):
                    # 兼容：万一之前存成了 YAML 数组
                    existing_list = [str(x) for x in existing if str(x).strip()]
                else:
                    existing_list = [x for x in str(existing).split(';') if x.strip()]

                # 去重
                if data_url in existing_list:
                    print(f"  - 已存在相同 URL，跳过: {title}")
                    image_table[title] = ';'.join(existing_list)
                    continue

                # 按位置插入（越界就放末尾）
                pos = min(insert_pos, len(existing_list))
                existing_list.insert(pos, data_url)

                # 再用 ';' 拼回字符串
                image_table[title] = ';'.join(existing_list)
                appended_count += 1
                print(f"  ✓ 追加图片表格: {title} (插入位置 {pos}, 共 {len(existing_list)} 条)")
        else:
            image_table[title] = data_url
            new_count += 1
            print(f"  ✓ 新增图片表格: {title}")
            
    # 保存
    if save_image_table(config, image_table):
        print(f"\n图片表格更新完成: 新增 {new_count} 个, 覆盖 {updated_count} 个, 追加 {appended_count} 个")
        return True
    else:
        print("\n错误: 图片表格保存失败")
        return False