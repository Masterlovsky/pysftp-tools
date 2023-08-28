## PySFTP-TOOLS
### Install
- Using a self built venv environment for installation is suggested
```shell
# python3 -m venv venv
# source venv/bin/activate

python3 -m pip install -r requirements.txt
```

### Use
- Copy conf.yml to conf_private.yml
```shell
cp conf.yml conf_private.yml
```
- Fill in the required fields
```
vim conf_private.yml
```
#### Usage 1 -- use main.py to upload files to remote server via jumpserver or download file from remote repository.
```shell
python3 main.py push/pull
```


#### Usage 2 -- upload or download files via test.csv
- Copy test.csv to test_private.csv
```shell
cp test.csv test_private.csv
```
- Fill in the required server information
- Refer to the following code for uploading and downloading
```python

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
```
