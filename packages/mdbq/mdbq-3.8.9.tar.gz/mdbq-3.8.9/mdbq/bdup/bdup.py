# -*- coding: UTF-8 –*-
import os
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor
from bypy import ByPy


class BaiDu:
    """
    如果通过调用命令行终端运行, 云端路径必须使用linux格式，不要使用windows格式,否则在windows系统里面会上传失败(无法在云端创建文件)
    """
    def __init__(self):
        self.local_path = None
        self.remote_path = None
        self.skip:list = []
        self.delete_remote_files:list = []
        self.bp = ByPy()
        self.count = 0
        self.total = 0

    def upload_dir(self, local_path, remote_path):
        """
        上传整个文件夹，执行完后删除指定文件, 指定 self.delete_remote_files
        如果通过调用命令行终端运行, 《云端路径!!》必须使用linux格式，不要使用反斜杆,否则在windows系统里面会上传失败
        """
        self.local_path = local_path
        self.remote_path = remote_path.replace('\\', '/')
        if not os.path.exists(self.local_path):
            print(f'{self.local_path}: 本地目录不存在，没有什么可传的')
            return

        if platform.system() == 'Windows':
            self.bp.upload(localpath=self.local_path, remotepath=self.remote_path.replace('\\', '/'))  # 上传文件到百度云
        else:
            command = f'bypy upload "{self.local_path}" "{self.remote_path}" --on-dup skip'  # 相同文件跳过
            try:
                subprocess.run(command, shell=True)
            except Exception as e:
                print(e)
        self.delete_files()  # 最好是在内部执行删除, 避免路径异常

    def upload_file(self, local_path, remote_path, processes=False):
        """
        上传文件夹，按单个文件上传，可以跳过指定文件/文件夹, 指定 self.skip
        《云端路径!!》必须使用linux格式
        """
        if not isinstance(self.skip, list):
            raise TypeError('skip must be a list')
        self.skip += ['.DS_Store', '.localized', 'desktop.ini', '$RECYCLE.BIN', 'Icon']
        self.local_path = local_path
        self.remote_path = remote_path.replace('\\', '/')
        if not os.path.exists(self.local_path):
            print(f'{self.local_path}: 本地目录不存在，没有什么可传的')
            return

        local_files = os.listdir(self.local_path)

        local_file_list = []
        for file in local_files:
            if file in self.skip:  # 跳过指定文件/文件夹
                continue
            local_p = os.path.join(self.local_path, file)
            if os.path.isfile(local_p):
                rt_path = os.path.join(self.remote_path, file).replace('\\', '/')
                self.total += 1
                local_file_list.append({local_p: rt_path})
            elif os.path.isdir(local_p):
                for root, dirs, files in os.walk(local_p, topdown=False):
                    for name in files:
                        if name in self.skip:  # 从子文件夹内跳过指定文件
                            continue
                        lc_path = os.path.join(root, name)
                        rt_path = lc_path.replace(self.local_path, self.remote_path).replace('\\', '/')
                        self.total += 1
                        local_file_list.append({lc_path: rt_path})
        if processes:
            # 不指定 max_workers 参数，默认值是 os.cpu_count() * 5
            with ThreadPoolExecutor() as executor:
                    executor.map(self.up_one_file, local_file_list)
        else:
            for item in local_file_list:
                self.up_one_file(file_dict=item)

    def up_one_file(self, file_dict:dict):
        if not isinstance(file_dict, dict):
            raise TypeError('file_dict must be a dict')
        for k, v in file_dict.items():
            self.count += 1
            print(f'上传: {self.count}/{self.total}  {k}')
            self.bp.upload(localpath=k, remotepath=v)  # 上传文件到百度云

    def delete_files(self):
        """ 移除云端文件，位于 self.remote_path 文件夹下的子文件 """
        self.delete_remote_files += ['.DS_Store', '.localized', 'desktop.ini', '$RECYCLE.BIN', 'Icon']
        for delete_file in self.delete_remote_files:
            self.bp.remove(remotepath=f'{self.remote_path.replace('\\', '/')}/{delete_file}')  # 移除文件

    def download_dir(self, local_path, remote_path):
        """ 下载文件夹到本地 """
        self.local_path = local_path
        self.remote_path = remote_path.replace('\\', '/')
        if not os.path.exists(self.local_path):
            os.mkdir(self.local_path)

        self.bp.download(localpath=f'{self.local_path}', remotepath=f'{self.remote_path.replace('\\', '/')}')


if __name__ == '__main__':
    bp = ByPy()
    bp.list()
