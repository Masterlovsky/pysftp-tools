from tqdm import tqdm
import shutil
import warnings 
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
import paramiko

class SSHConnection(object):

    def __init__(self, host=None, port=None, username=None, pwd=None, pkey=None):
        """
        :param host: 服务器ip
        :param port: 接口
        :param username: 登录名
        :param pwd: 密码
        """
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.pkey = pkey
        self.__k = None

    def connect(self):
        transport = paramiko.Transport((self.host, self.port))
        # Priority use secret key to login
        if self.pkey:
            self.__k = paramiko.RSAKey.from_private_key_file(self.pkey)
            transport.connect(username=self.username, pkey=self.__k)
        else:
            # check if the password is empty
            if self.pwd:
                transport.connect(username=self.username, password=self.pwd)
            else:
                raise ValueError("Password is empty!")
        self.__transport = transport

    def close(self):
        self.__transport.close()

    def upload(self, local_path, target_path):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # use tqdm to show the progress bar
        sftp.put(local_path, target_path, callback=lambda x, y: tqdm(total=y, unit='B', unit_scale=True, desc=local_path.split('/')[-1], leave=True))

    def download(self, remote_path, local_path):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        # use tqdm to show the progress bar
        sftp.get(remote_path, local_path, callback=lambda x, y: tqdm(total=y, unit='B', unit_scale=True, desc=remote_path.split('/')[-1], leave=True))
        # original method
        # sftp.get(remote_path, local_path)

    def download_slowly(self, remote_path, local_path):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)

        # # 旧方法下载大文件会出现Server connection dropped
        # sftp.get(remote_path, local_path)

        # 新方法下载大文件成功
        # 这将避免Paramiko预取缓存，并允许您下载文件，即使它不是很快
        with sftp.open(remote_path, 'rb') as fp:
            shutil.copyfileobj(fp, open(local_path, 'wb'))

    def cmd(self, command):
        ssh = paramiko.SSHClient()
        ssh._transport = self.__transport
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        # 获取命令结果
        result = stdout.read()
        result = str(result, encoding='utf-8')
        return result


class SSHConnectionManager(object):
    def __init__(self, host, port, username, pwd=None, pkey=None):
        self.ssh_args = {
            "host": host,
            "port": port,
            "username": username,
            "pwd": pwd,
            "pkey": pkey
        }

    def __enter__(self):
        self.ssh = SSHConnection(**self.ssh_args)
        self.ssh.connect()
        return self.ssh

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()
        return True
