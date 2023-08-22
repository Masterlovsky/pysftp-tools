"""
This is a tool for sending and receiving file through SSH protocol.
Need a csv file to record the server information.
Powered by Seanet.DSP / mazl@dsp.ac.cn 2023.8.22 v1.0
"""

from SSHFileManager import SFTPFileManager_Tool
from csvreader import CSVReader
from threading import Thread


def test_single_t_upload(csvfile):
    ssh_conf_list = CSVReader(csvfile).read()
    for ssh_conf in ssh_conf_list:
        sshtool = SFTPFileManager_Tool(**ssh_conf)
        sshtool.upload_file(
            local_path=ssh_conf["local_path"],
            target_path=ssh_conf["remote_path"]
        )


def test_multi_t_upload(csvfile):
    # multithread upload
    ThreadList = []
    ssh_conf_list = CSVReader(csvfile).read()
    for ssh_conf in ssh_conf_list:
        sshtool = SFTPFileManager_Tool(**ssh_conf)
        t = Thread(target=sshtool.upload_file, args=(ssh_conf["local_path"],
                                                     ssh_conf["remote_path"]))
        t.start()
        ThreadList.append(t)
    for t in ThreadList:
        t.join()


def test_single_t_download(csvfile):
    ssh_conf_list = CSVReader(csvfile).read()
    for ssh_conf in ssh_conf_list:
        sshtool = SFTPFileManager_Tool(**ssh_conf)
        sshtool.download_file(
            remote_path=ssh_conf["remote_path"],
            local_path=ssh_conf["local_path"]
        )


def test_multi_t_download(csvfile):
    # multithread download
    ThreadList = []
    ssh_conf_list = CSVReader(csvfile).read()
    for ssh_conf in ssh_conf_list:
        sshtool = SFTPFileManager_Tool(**ssh_conf)
        t = Thread(target=sshtool.download_file, args=(ssh_conf["remote_path"],
                                                       ssh_conf["local_path"]))
        t.start()
        ThreadList.append(t)
    for t in ThreadList:
        t.join()


if __name__ == '__main__':
    csv_f = "data/test.csv"
    # test_single_t_upload(csv_f)
    # test_multi_t_upload(csv_f)
    test_single_t_download(csv_f)
    # test_multi_t_download(csv_f)
