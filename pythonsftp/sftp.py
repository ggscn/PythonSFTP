import base64
import getpass
from pathlib import Path
import os
import socket
import sys
import traceback
#import python-gssapi

import paramiko
from paramiko.py3compat import input
from exceptions import FileError

class SFTP(object):
    def __init__(self, username, hostname, password=None, host_key=None, port=22, verbose=False):
        self.username = username
        self.hostname = hostname
        self.password = password
        self.host_key = host_key
        self.port = port

        self.UseGSSAPI = False  # enable GSS-API / SSPI authentication
        self.DoGSSAPIKeyExchange = False

        if host_key is not None:
            self.UseGSSAPI = True  # enable GSS-API / SSPI authentication
            self.DoGSSAPIKeyExchange = True
            hostkeytype = None

            try:
                host_keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/.ssh/known_hosts")
                )
            except IOError:
                try:
                    # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                    host_keys = paramiko.util.load_host_keys(
                        os.path.expanduser("~/ssh/known_hosts")
                    )
                except IOError:
                    print("*** Unable to open host keys file")
                    host_keys = {}

            if hostname in host_keys:
                hostkeytype = host_keys[hostname].keys()[0]
                hostkey = host_keys[hostname][hostkeytype]
                print("Using host key of type %s" % hostkeytype)
        
        self.conn = self.connect()

    def connect(self):
        port = self.port
        hostname = self.hostname
        username = self.username
        
        password = self.password        
        hostkey = self.host_key
        UseGSSAPI = self.UseGSSAPI
        DoGSSAPIKeyExchange = self.DoGSSAPIKeyExchange
        
        t = paramiko.Transport((hostname, port))

        t.connect(
            hostkey=hostkey,
            username=username,
            password=password,
            gss_host=socket.getfqdn(hostname),
            gss_auth=UseGSSAPI,
            gss_kex=DoGSSAPIKeyExchange,
        )
        conn = paramiko.SFTPClient.from_transport(t)
        return conn

    def mkdir(self, path):
        conn = self.conn
        
        try:
            conn.mkdir(path)
        except:
            print('')

    def upload(self, file_obj=None, source_path=None, destination_path=None):
        
        conn = self.conn

        if not Path(source_path).is_file():
            raise FileError('File path is not correct')

        if file_obj is None and source_path is None:
            raise FileError('Must supply either file like object or path to a file to upload')
        
        if source_path is not None:
            with open(source_path, "r") as f:
                file_obj = f.read()
                print(f.name)
        #catch os error and see if destination path exists
   
        conn.open(destination_path, "w").write(file_obj)



    def download(self):
        pass

    def list_dir(self, directory='.'):
        conn = self.conn
        dirlist = conn.listdir(directory)
        print("Dirlist: %s" % dirlist)

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()