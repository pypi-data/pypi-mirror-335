import json
import shutil
import threading
from pathlib import Path

import os
import ctypes
import time
import uuid
import argparse


class FolderNotFound(Exception):
    def __init__(self, folder_path, *args, ):
        self.folder_path = folder_path
        super().__init__(*args, )

    def __str__(self):
        info = f'{self.folder_path} not found.'
        return info


class PythonCode2Safe:
    def __init__(self,
                 target_path: str = '.',
                 exclude_folders: list = None,
                 exclude_folder_names: list = None,
                 threading_count: int = 20,
                 final_pos: Path = Path('.').absolute(),
                 json_path: Path = None,
                 ):
        self.target_path = Path(target_path).absolute()
        self.final_pos = final_pos
        self.json_path = json_path
        self.exclude_folders = exclude_folders if exclude_folders else []
        self.exclude_folder_names = exclude_folder_names if exclude_folder_names else []
        self.exclude_folders.append('pyarmor_runtime_000000')
        self._valid_exclude_folders(self.exclude_folders)
        self.threading_manage = self.init_threading_manage(threading_count)
        # self.pre_handler()

    def pre_handler(self):
        if self.target_path == self.final_pos:
            return
        all_folders = self.get_all_folders()
        for folder in all_folders:

            folder = Path(folder)
            folder_relative_path = folder.relative_to(self.target_path)
            folder_final_path = self.final_pos / folder_relative_path

            file_or_dirs = os.listdir(folder)
            count = 0
            for file_or_dir in file_or_dirs:
                file_or_dir_path = folder / file_or_dir
                if file_or_dir_path.is_dir():
                    continue

                file_path = file_or_dir_path
                if file_path == self.json_path:
                    continue

                file_relative_path = file_path.relative_to(self.target_path)
                new_file_path = self.final_pos / file_relative_path
                new_file_dir_path = new_file_path.parent
                new_file_dir_path.mkdir(parents=True, exist_ok=True, )
                shutil.copy2(file_path, new_file_path)
                count += 1
                print(f'已复制文件[已复制{count}]:{file_path} --> {new_file_path}')
        self.target_path = Path(self.final_pos)

    @staticmethod
    def _run_command(command):
        log_path = f'{uuid.uuid1()}'
        command = f'{command} 2>{log_path} >{log_path}'
        os.system(command)
        os.remove(log_path)
        bug_log = 'pyarmor.bug.log'
        if Path(bug_log).exists():
            os.remove(bug_log)

    @staticmethod
    def init_threading_manage(threading_count):
        threading_manage = {}
        for i in range(1, threading_count + 1):
            threading_manage[i] = False
        return threading_manage

    def _valid_exclude_folders(self, exclude_folders, ) -> None:
        """
        验证传入的排除文件夹是否有效
        """
        for exclude_folder in exclude_folders:
            exclude_folder_path = self.target_path / exclude_folder
            if not exclude_folder_path.exists() or not exclude_folder_path.is_dir():
                FolderNotFound(exclude_folder_path)

    def _exclude_folder_is_ancestor(self, abs_folder_path: Path, ) -> bool:
        """
        传入的文件夹是否位于排除的文件夹中
        """
        if abs_folder_path.name == 'pyarmor_runtime_000000':
            return True

        if abs_folder_path.name in self.exclude_folder_names:
            return True

        for exclude_folder in self.exclude_folders:
            try:
                abs_folder_path.relative_to(exclude_folder)
                return True
            except ValueError:
                continue
        return False

    def get_all_folders(self, ) -> list:
        """
        递归获取指定路径下的所有文件夹
        但是不会包含排序的文件夹 以及排除文件夹的后代文件夹
        """
        folder_list = [self.target_path]

        if os.path.exists(self.target_path):
            for root, dirs, files in os.walk(self.target_path):
                root = Path(root)
                for item in dirs:
                    folder_path = root / item
                    if self._exclude_folder_is_ancestor(folder_path):
                        continue
                    folder_list.append(folder_path)
        return folder_list

    @staticmethod
    def add_write_permission(file_path):
        file_path = str(file_path)
        ctypes.windll.kernel32.SetFileAttributesW(
            file_path,
            ctypes.windll.kernel32.GetFileAttributesW(file_path) & ~0x01,
        )

    def get_task_id(self):
        while True:
            for task_id in self.threading_manage:
                value = self.threading_manage[task_id]
                if value:
                    continue
                return task_id
            time.sleep(0.1)

    def _safe_one_dir(self, folder: Path, ):
        file_or_dirs = list(folder.iterdir())
        for file_or_dir in file_or_dirs:
            if not file_or_dir.is_file():
                continue
            file_path: Path = file_or_dir
            if file_path == self.json_path:
                continue
            file_relative_path = file_path.relative_to(self.target_path)
            new_file_path = self.final_pos / file_relative_path
            new_file_dir_path = new_file_path.parent
            new_file_parent_path = new_file_path.parent
            new_file_parent_path.mkdir(parents=True, exist_ok=True, )

            if file_path.suffix != '.py':
                shutil.copy2(file_path, new_file_path)
                continue

            file_path: Path = file_or_dir
            command = fr"pyarmor gen --output {new_file_parent_path}  {file_path}"
            self._run_command(command)

    def safe_one_dir(self, folder: Path, task_id: int, ):
        self.threading_manage[task_id] = True
        self._safe_one_dir(folder)
        self.threading_manage[task_id] = False

    def safe(self):
        folders = self.get_all_folders()
        total = len(folders)
        for index, folder in enumerate(folders):
            task_id = self.get_task_id()
            thread_obj = threading.Thread(target=self.safe_one_dir, args=(folder, task_id,))
            thread_obj.start()

            info = f'进程累计已开启{index + 1},共需{total},当前处理:{folder}'
            print(info)


def message():
    cd_path = Path('.').absolute()
    info = f'警告!!!!!!将删除所有源代码,将删除所有源代码,将删除所有源代码,并替换为加密代码.请先拷贝一份再加密.[当前目录{cd_path}的源代码会全部替换为加密代码]'
    print(info)
    common = input("输入Yes继续,区分大小写:")
    if common != 'Yes':
        getattr(os, '_exit')(0)


def get_conf(json_path: Path, ):
    if not json_path.exists():
        cd_path = Path('.').absolute()
        idea_path = cd_path / '.idea'
        data = {
            '#': '约定#号开头的配置项作为注释项.',
            '#final_pos': '存放加密代码的根目录.',
            '#exclude_folders': '排除的目录.这些目录不会加密,其后代也不会加密.',
            '#threading_count': '线程数量,如果你的电脑很强悍,看可以设置的高一点.',

            'final_pos': str(cd_path),
            'exclude_folders': [
                str(cd_path / '.idea'),
                str(cd_path / '.vscode'),
                str(cd_path / '.venv'),
            ],
            'exclude_folder_names': [
                '__pycache__',
            ],
            'threading_count': 20,
        }
        data_str = json.dumps(data, ensure_ascii=False, )
        with open(json_path, 'w') as file_obj:
            file_obj.write(data_str)
        time.sleep(1)
    with open(json_path, 'r') as file_obj:
        data_str = file_obj.read()
        data_json = json.loads(data_str)
        return data_json


def get_params():
    args_obj = argparse.ArgumentParser(description="接受一组参数个性化加密", )
    args_obj.add_argument('--json_path', type=Path, required=False, help="json配置文件的路径", )
    args = args_obj.parse_args()

    # 配置文件路径
    json_path = args.json_path if args.json_path else (Path('.') / 'py2safe.json').absolute()

    return {
        "json_path": json_path,
    }


def _main():
    params = get_params()
    json_path = params['json_path']
    conf = get_conf(json_path)
    final_pos = conf['final_pos']
    exclude_folders = conf['exclude_folders']
    threading_count = conf['threading_count']
    exclude_folder_names = conf['exclude_folder_names']
    if final_pos == str(Path('.').absolute()):
        message()
    PythonCode2Safe(
        exclude_folders=exclude_folders,
        threading_count=threading_count,
        final_pos=final_pos,
        exclude_folder_names=exclude_folder_names,
        json_path=json_path,
    ).safe()


def main():
    _main()
