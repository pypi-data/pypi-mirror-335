"""
Pyinstaller build 脚本，一键将 Python 项目根据指定设置打包成 exe 文件，并复制到指定文件夹中
"""


import os
import shutil
import subprocess


MAIN_FILE = 'main.py'  # 主文件
APP_NAME = 'dvatioff-音频工具集'  # 应用名称
TARGET_PATH = r"dvatioff-音频工具集"  # 目标路径
NOCONSOLE = False  # 是否显示控制台
ONEFILE = False  # 是否打包成一个文件
WINDOWED = False  # 是否隐藏控制台
OTHER_DEPENDENCY = True  # 是否复制其他依赖文件，由于 Pyinstaller 打包对部分胞体存在依赖丢失的问题，每次打包需要手动复制这些依赖文件；这里提前将这些依赖文件复制到 dependency 文件夹中，build 成功后会自动复制到打包文件夹中


def build_main(main_file,  app_name='main', noconsole=True, windowed=False, onefile=False):
    if os.path.exists('../../build'):
        shutil.rmtree('../../build')
    if os.path.exists('../../dist'):
        shutil.rmtree('../../dist')

    command = ['pyinstaller', main_file, '--clean']
    if app_name:
        command.append(f'--name={app_name}')
    if noconsole:
        command.append('--noconsole')
    if windowed:
        command.append('--windowed')
    if onefile:
        command.append('--onefile')

    try:
        subprocess.run(command, check=True)
        print("Build succeeded")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def copy_app(target_path, onefile=False, dependency=False):
    dist_path = 'dist' if onefile else f'dist/{APP_NAME}'
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    if not onefile:
        internal_folder = os.path.join(dist_path, '_internal')
        if os.path.exists(internal_folder):
            if dependency:
                dependency_folder = r'dependency'
                # 将dependency文件夹中的所有子文件夹复制到_internal文件夹中
                for folder in os.listdir(dependency_folder):
                    folder_path = os.path.join(dependency_folder, folder)
                    target_folder_path = os.path.join(internal_folder, folder)
                    if os.path.exists(target_folder_path):
                        shutil.rmtree(target_folder_path)
                    shutil.copytree(folder_path, target_folder_path)
                    print(f"Copied {folder} folder to _internal folder")

            target_internal_folder = os.path.join(target_path, '_internal')
            if os.path.exists(target_internal_folder):
                shutil.rmtree(target_internal_folder)
            shutil.copytree(internal_folder, target_internal_folder)
            print(f"Copied _internal folder to {target_path}")

    for file_name in os.listdir(dist_path):
        if file_name.endswith('.exe'):
            source_file = os.path.join(dist_path, file_name)
            target_file = os.path.join(target_path, file_name)
            shutil.copy2(source_file, target_file)
            print(f"Copied {file_name} to {target_path}")


def main():
    if build_main(MAIN_FILE, app_name=APP_NAME, noconsole=NOCONSOLE, windowed=WINDOWED, onefile=ONEFILE):
        copy_app(TARGET_PATH, onefile=ONEFILE, dependency=OTHER_DEPENDENCY)


if __name__ == '__main__':
    main()
