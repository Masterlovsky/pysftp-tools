"""
Read csv file and return a list of dict.
csv format:
host,port,username,pwd,pkey,local_path,remote_path
"""

import csv


class CSVReader(object):

    def __init__(self, csv_path):
        self.csv_path = csv_path

    def read(self):
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # skip the first line
            next(reader)
            # return a list of dict, if pwd of pkey is empty, it will be None
            # change port to int
            return [dict(zip(['host', 'port', 'username', 'pwd', 'pkey', 'local_path', 'remote_path'],
                             [row[0], int(row[1]), row[2], row[3], row[4], row[5], row[6]])) for row in reader]


if __name__ == "__main__":
    csv_path = "data/test.csv"
    reader = CSVReader(csv_path)
    dic = reader.read()
    print(dic)
