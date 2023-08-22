from SSHConnection import SSHConnectionManager
import multiprocessing
from pathlib import Path


def clear_dir(path):
    """
    清空文件夹：如果文件夹不存在就创建，如果文件存在就清空！
    :param path: 文件夹路径
    :return:
    """
    import os
    import shutil
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)
        return True
    except:
        return False


class SFTPFileManager_Tool(object):
    """
    SFTP文件管理工具
    """

    def __init__(self, host, port, username, pwd=None, pkey=None, **kwargs):
        """
        init
        :param host:        ip
        :param port:        端口
        :param username:    用户名
        :param pwd:         密码
        :param pkey:        私钥
        """
        self.ssh_args = {"host": host, "port": port,
                         "username": username, "pwd": pwd, "pkey": pkey}

    def cmd(self, command):
        """
        执行命令
        :param command:
        :return:
        """
        with SSHConnectionManager(**self.ssh_args) as ssh:
            return ssh.cmd(f"{command}")

    def exists(self, path):
        """
        判断路径是否存在
        :param path:
        :return:
        """
        is_exists = False
        with SSHConnectionManager(**self.ssh_args) as ssh:
            result = ssh.cmd(f"ls {path}")
            if result:
                is_exists = True
        return is_exists

    def is_file(self, path):
        """
        判断路径是否是文件
        :param path:
        :return:
        """
        if self.exists(path):
            with SSHConnectionManager(**self.ssh_args) as ssh:
                prefix = ssh.cmd(f"ls -ld {path}")[0]
                if prefix == '-':
                    return True
                else:
                    return False
        else:
            return False

    def is_dir(self, path):
        """
        判断路径是否是目录
        :param path:
        :return:
        """
        if self.exists(path):
            with SSHConnectionManager(**self.ssh_args) as ssh:
                prefix = ssh.cmd(f"ls -ld {path}")[0]
                if prefix == 'd':
                    return True
                else:
                    return False
        else:
            return False

    def makedirs(self, path):
        """
        创建目录
        :param path: 远程文件夹路径
        :return:
        """
        with SSHConnectionManager(**self.ssh_args) as ssh:
            # path = str(Path(path)).replace("\\", "/")
            cmd_str = f"mkdir -p {path}"
            print(cmd_str)
            ssh.cmd(cmd_str)

    def walkFolderFile(self, path):
        """
        获取文件夹下的所有文件
        :param path:    远程文件夹路径
        :return:
        """
        files = []
        with SSHConnectionManager(**self.ssh_args) as ssh:
            _list = ssh.cmd(f"ls -R {path}")
            _list = _list.split('\n')
            _list = [x for x in _list if x]
            cur_folder = None
            for item in _list:
                if item[-1] == ":":
                    cur_folder = item[:-1]
                else:
                    if Path(item).suffix:
                        file = cur_folder + "/" + item
                        files.append(file)
        return files

    def download_file(self, remote_path, local_path):
        """
        下载文件
        :param remote_path: 远程文件路径
        :param local_path:  本地文件路径
        :return:
        """
        with SSHConnectionManager(**self.ssh_args) as ssh:
            if not Path(local_path).parent.exists():
                Path(local_path).parent.mkdir(parents=True)
            print(f'Start downloading from remote: "{remote_path}"...')
            try:
                # ssh.download_slowly(remote_path=remote_path, local_path=local_path)
                ssh.download(remote_path=remote_path, local_path=local_path)
            except Exception as e:
                print(f"File {remote_path} download failed!")
                print(e)
            print(f'Download success, save to "{local_path}"')

    def download_folder(self, remote_folder, local_folder):
        """
        下载文件夹
        :param remote_folder:   远程文件夹目录
        :param local_folder:    本地文件夹目录
        :return:
        """
        with SSHConnectionManager(**self.ssh_args) as ssh:
            dst_folder = Path(local_folder)
            if not dst_folder.exists():
                dst_folder.mkdir(parents=True)
            clear_dir(str(dst_folder))
            files_list = ssh.cmd("ls {}".format(remote_folder))
            files_list = files_list.split('\n')
            files_list = [x for x in files_list if x]

            # 多进程下载文件
            cpu_count = multiprocessing.cpu_count() // 2
            if cpu_count == 0:
                cpu_count = 1
            pool = multiprocessing.Pool(cpu_count)
            for file in files_list:
                remote_path = remote_folder + "/" + file
                local_path = dst_folder.joinpath(file)
                pool.apply_async(func=self.download_file,
                                 args=(remote_path, local_path))
            pool.close()
            pool.join()

            # 主进程下载文件
            # for file in files_list:
            #     remote_path = remote_folder + "/" + file
            #     local_path = dst_folder.joinpath(file)
            #     print(f"正下载{remote_path}...")
            #     ssh.download_slowly(remote_path=remote_path, local_path=local_path)

    def download_walk_folder(self, remote_folder, local_folder):
        """
        下载所有文件夹数据
        :param remote_folder:   远程文件夹路径
        :param local_folder:    本地文件夹路径
        :return:
        """
        files = self.walkFolderFile(path=remote_folder)
        # 先创建文件夹
        for file in files:
            remain_path = file.replace(remote_folder, "")
            remain_path = remain_path.split("/")
            remain_path = [x for x in remain_path if x and not Path(x).suffix]
            if remain_path:
                _folder = Path(local_folder).joinpath(*remain_path)
                if not _folder.exists():
                    _folder.mkdir(parents=True)
                else:
                    clear_dir(str(_folder))

        # 开始下载文件
        cpu_count = multiprocessing.cpu_count() // 2
        if cpu_count == 0:
            cpu_count = 1
        pool = multiprocessing.Pool(cpu_count)
        for file in files:
            remain_path = file.replace(remote_folder, "")
            remain_path = remain_path.split("/")
            remain_path = [x for x in remain_path if x and not Path(x).suffix]
            if remain_path:
                _folder = Path(local_folder).joinpath(*remain_path)
            else:
                _folder = Path(local_folder)
            filename = Path(file).name
            remote_path = file
            local_path = _folder.joinpath(filename)
            pool.apply_async(func=self.download_file,
                             args=(remote_path, local_path))
        pool.close()
        pool.join()

    def upload_file(self, local_path, target_path):
        """
        上传文件
        :param local_path:  本地文件路径
        :param target_path: 远程文件路径
        :return:
        """
        # if remote path is not exists, create remote folder first
        # check path style
        style = "Linux" if "/" in target_path else "Windows"
        if style == "Windows":
            target_folder = Path(target_path).parent.as_posix().replace("/", "\\")
        else:
            target_folder = Path(target_path).parent.as_posix()
        if not self.exists(target_folder):
            self.makedirs(target_folder)
        with SSHConnectionManager(**self.ssh_args) as ssh:
            # print(f'Start uploading file "{local_path}, to {target_path}"...')
            _path = Path(local_path)
            if not _path.exists() or not _path.is_file():
                return False
            try:
                ssh.upload(local_path=local_path, target_path=target_path)
                print(f"Upload success, save to {target_path}")
            except Exception as e:
                print(f'File "{local_path}" upload failed!')
                print(e)
