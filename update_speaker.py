# python update_speaker.py 0526.txt last-week-in-tinycorp/2025-05-26/meeting-transcript.md
import re
import os

def load_speaker_mapping(mapping_file_path):
    """
    从文件加载时间戳到说话人的映射。
    文件格式应为: HH:MM:SS speaker_name
    
    Args:
        mapping_file_path (str): 映射文件的路径。
        
    Returns:
        dict: 一个以时间戳为键，说话人为值的字典。
    """
    speaker_map = {}
    print(f"正在从 '{mapping_file_path}' 加载说话人映射...")
    try:
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 去除行首尾的空白，并按空格分割
                parts = line.strip().split()
                if len(parts) >= 2:
                    # timestamp, speaker = parts
                    timestamp = parts[0]
                    speaker = " ".join(parts[1:])
                    # 验证时间戳格式 (可选但推荐)
                    if re.match(r'\d{2}:\d{2}:\d{2}', timestamp):
                        speaker_map[timestamp] = speaker
                    else:
                        pass
                        #print(f"  [警告] 忽略格式不正确的时间戳行: '{line.strip()}'")
                elif line.strip(): # 如果行不为空白，但格式不符
                    #print(f"  [警告] 忽略格式不正确的行: '{line.strip()}'")
                    pass
    except FileNotFoundError:
        print(f"错误: 映射文件 '{mapping_file_path}' 未找到。")
        return None
    
    print(f"加载完成，共找到 {len(speaker_map)} 条映射。")
    return speaker_map

def update_markdown_speakers(markdown_path, speaker_map, output_path):
    """
    读取Markdown文件，根据提供的映射更新说话人，并写入新文件。
    
    Args:
        markdown_path (str): 原始Markdown文件的路径。
        speaker_map (dict): 时间戳到说话人的映射字典。
        output_path (str): 更新后文件的保存路径。
    """
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()
    except FileNotFoundError:
        print(f"错误: Markdown文件 '{markdown_path}' 未找到。")
        return

    updated_lines = []
    lines_updated_count = 0
    
    # 正则表达式，用于匹配标题行并提取时间戳
    # 捕获组 1: 时间戳 (HH:MM:SS)
    header_pattern = re.compile(r'^(##### \*\*.+?\*\* \[\[)(\d{2}:\d{2}:\d{2})(.*\])$')
    # 正则表达式，用于替换说话人名字
    # 捕获组 1: `##### **`
    # 捕获组 2: `** [[...` 之后的所有内容
    speaker_replace_pattern = re.compile(r'(##### \*\*).+?(\*\* \[\[.*)')
    
    print(f"\n正在处理 '{markdown_path}'...")

    for line in lines:
        match = header_pattern.search(line.strip())
        
        if match:
            timestamp = match.group(2)
            # 从映射中查找新的说话人名字
            new_speaker = speaker_map.get(timestamp)
            
            if new_speaker:
                # 格式化说话人名字（例如：首字母大写）
                formatted_speaker = new_speaker.capitalize()
                
                # 使用 re.sub 进行替换，保留前后结构
                # \1 和 \2 是对捕获组的反向引用
                new_line = speaker_replace_pattern.sub(rf'\1{formatted_speaker}\2', line.strip())
                updated_lines.append(new_line + '\n')
                lines_updated_count += 1
                print(f"  - 时间戳 {timestamp}: 说话人已更新为 '{formatted_speaker}'")
            else:
                # 如果在映射中找不到时间戳，保留原始行
                updated_lines.append(line)
                print(f"  - 时间戳 {timestamp}: [警告] 在映射文件中未找到对应说话人，保留原始行。")
        else:
            # 如果不是标题行，直接保留
            updated_lines.append(line)
            
    # 将更新后的内容写入新文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.writelines(updated_lines)
        print(f"\n处理完成！共更新 {lines_updated_count} 行。")
        print(f"结果已保存到: '{output_path}'")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")


# --- 主程序执行部分 ---
if __name__ == "__main__":
    import sys, os, json
    # --- 文件名定义 ---
    mapping_filename = 'speakers.txt'
    input_md_filename = 'transcript.md'
    output_md_filename = 'transcript_updated.md'
    
    mapping_filename = sys.argv[1]
    input_md_filename = sys.argv[2]
    output_md_filename = sys.argv[3]
    
    speaker_data = load_speaker_mapping(mapping_filename)
    
    print(speaker_data)
    if speaker_data:
        update_markdown_speakers(input_md_filename, speaker_data, output_md_filename)