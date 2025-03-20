from functools import wraps
import time
import json
import re
import webbrowser
import ctypes
import os
from datetime import datetime
import shutil
from jiwer import wer
import sys
import subprocess
import pyperclip
import Levenshtein


def retry(exceptions, tries=5, delay=1):
    """
    重试装饰器，当函数抛出指定的异常时，自动重试。
    :param exceptions: 触发重试的异常类型
    :param tries: 最大重试次数
    :param delay: 初始延迟时间
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"警告：{func.__name__} - {e}, 正在重试...")
                    time.sleep(mdelay)
                    mtries -= 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_clipboard_text():
    """
    获取剪贴板中的文本
    """
    return pyperclip.paste()


def load_dict_from_json_file(file_path):
    """
    从 json 文件中加载数据
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def save_dict_to_json_file(file_path, data):
    """
    将数据保存到 json 文件中
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_random(name):
    """
    是否是随机类声音
    """
    tail = name.split("_")[-1]
    pattern = r"0[1-9]$"
    return bool(re.match(pattern, tail))


def is_loop(name):
    """
    是否是 Loop 类声音
    """
    tail = name.split("_")[-1]
    pattern1 = r"Loop$"
    pattern2 = r"Lp$"
    return bool(re.match(pattern1, tail) or re.match(pattern2, tail))


def is_voice(name):
    """
    是否是 voice 类声音
    """
    head = name.split("_")[0]
    pattern = r"VO$"
    return bool(re.fullmatch(pattern, head))


def is_death(name):
    """
    是否是死亡类声音
    """
    tail = name.split("_")[-1]
    pattern = r"Death$"
    return bool(re.match(pattern, tail))


def open_url(url):
    """
    打开指定的 URL
    """
    webbrowser.open(url)


def get_clipboard_text():
    """
    获取剪贴板中的文本
    """
    return pyperclip.paste()


def minimize_console():
    """
    最小化控制台窗口
    """
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')

    SW_MINIMIZE = 6

    console_window = kernel32.GetConsoleWindow()
    if console_window:
        user32.ShowWindow(console_window, SW_MINIMIZE)


def get_wav_path_in_folder(folder_path):
    """
    获取文件夹中的 wav 文件路径
    """
    wav_path = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav"):
                file_name = os.path.splitext(file)[0]
                wav_path[file_name] = os.path.join(root, file)

    return wav_path


def replace_file(cur_file, new_file):
    """
    替换文件
    """
    if os.path.exists(cur_file):
        os.remove(cur_file)
        print(f"文件 {cur_file} 已删除。")
    else:
        print(f"文件 {cur_file} 不存在。")
        return False

    shutil.copy2(new_file, cur_file)
    print(f"文件 {new_file} 已复制到 {cur_file}。")

    return True


def check_file_exists(file_path):
    """
    检查文件是否存在
    """
    if os.path.exists(file_path):
        print(f"文件 {file_path} 存在。")
        return True
    else:
        print(f"文件 {file_path} 不存在。")
        return False


def replace_audios(match_files):
    """
    替换匹配的文件
    """
    try:
        for match_file in match_files:
            cur_file = match_file[1]
            new_file = match_file[0]
            replace_file(cur_file, new_file)
        return True
    except Exception as e:
        print(f"替换文件时出错: {e}")
        return False


def create_placeholder_folder():
    """创建一个临时占位文件夹"""
    folder_path = f'\\placeholder'
    cur_path = os.getcwd()
    abs_path = cur_path + folder_path

    if not os.path.exists(abs_path):
        os.makedirs(abs_path)

    return abs_path


def delete_files_name_with_keyword(folder_path, keyword):
    """
    删除指定文件夹中，文件名包含指定关键字的文件
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if keyword in file_name:
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)  # 删除文件
                    print(f"已删除文件: {file_path}")
                except OSError as e:
                    print(f"删除文件 {file_path} 失败: {e}")
        for dir_name in dirs:
            if keyword in dir_name:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)  # 删除文件夹及其内容
                    print(f"已删除文件夹: {dir_path}")
                except OSError as e:
                    print(f"删除文件夹 {dir_path} 失败: {e}")


def clear_folder(folder_path):
    """
    清空文件夹
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            os.remove(os.path.join(root, file))
    return True


def get_desktop_path():
    """
    获取桌面路径
    """
    return os.path.join(os.path.expanduser("~"), 'Desktop')


def get_current_time():
    """
    使用 datetime.now() 获取当前时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def text_distance(text1, text2):
    """
    计算两个文本之间的 Levenshtein 距离
    """
    distance = Levenshtein.distance(text1, text2)

    return distance


def get_most_similar_name(file_name, name_list):
    """
    获取与给定文件名最相似的名称
    """

    min_distance = 100
    most_similar_name = ""

    for name in name_list:
        distance = text_distance(file_name, name)
        if distance < min_distance:
            min_distance = distance
            most_similar_name = name

    return most_similar_name


def text_wrong_proportion(text1, text2):
    """
    使用 Jiwer 计算两个字符串之间的词错误率
    """
    proportion = wer(text1, text2)

    return proportion


def keep_only_character(text):
    """
    定义一个正则表达式模式，匹配所有标点符号
    # 包括英文和CJK（中文、日文、韩文）标点符号
    """

    pattern = re.compile(r'[!"#$%&\'()*+,-./:;<=>?@\[\\\]^`{|}~，？！…。、【】；‘’“”·（）— ]')

    # 使用正则表达式的sub方法将这些标点符号替换为空
    text = pattern.sub('', text)

    # 将连续的空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text)

    # 移除头部和尾部的空白字符
    return text.strip()


def filename_validation(folder_path, name_list):
    """
    验证文件名是否符合规范, 返回不符合规范的文件名
    """

    filename_pair = []
    empty_folder = True
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.wav'):
                empty_folder = False
                file_name, file_extension = os.path.splitext(file)

                # 初步修改文件名，去除冗余符号
                cur_file_path = os.path.join(root, file_name + file_extension)
                file_name = keep_only_character(file_name)
                new_file_path = os.path.join(root, file_name + file_extension)
                if cur_file_path != new_file_path:
                    os.rename(cur_file_path, new_file_path)

                # 初步修改后，文件名拼写仍有错误
                if file_name not in name_list:
                    most_similar_name = get_most_similar_name(file_name, name_list)
                    filename_pair.append([file_name, most_similar_name, root, file_extension])

    return filename_pair, empty_folder


def run_exe(relative_path):
    """
    运行 exe 文件
    """
    file_type = relative_path.split('.')[-1]
    absolute_path = os.path.abspath(relative_path)
    cmd = f'"{absolute_path}"' if file_type == 'bat' else f'"{relative_path}"'

    CREATE_NEW_CONSOLE = 0x10
    cur_work_path = relative_path[:relative_path.rfind('\\')]
    subprocess.Popen(cmd, cwd=cur_work_path, creationflags=CREATE_NEW_CONSOLE)


def open_excel(relative_path):
    """
    打开 Excel 文件
    """
    absolute_path = os.path.abspath(relative_path)
    os.startfile(absolute_path)


def open_hyperlink(url):
    """
    打开超链接，根据操作系统的不同，使用不同的方式打开
    """
    if sys.platform == "win32":
        os.startfile(url)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, url])
