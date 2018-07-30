import base64
import getpass
from pathlib import Path
import os
import socket
import sys
import traceback
import stat
import io
#import python-gssapi

import paramiko
from paramiko.py3compat import input
#from exceptions import FileError

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
        try:
            self.conn.mkdir(path)
        except:
            print('Could not create directory')

    def upload(self, source_path=None, destination_path=None, file_obj=None):

        if source_path is None and file_obj is None:
            raise Exception('Source file path or file_obj must be supplied')

        if source_path is not None and not Path(source_path).is_file():
            raise Exception('Source file does not exist')
        
        if file_obj is not None:
            try:
                file_contents = file_obj.read()
            except io.UnsupportedOperation:
                print('File must be opened with "r"')

        if source_path is not None:
            file_obj = open(source_path, "r")
            file_contents = file_obj.read()

        if destination_path is None:
            destination_path = os.path.basename(file_obj.name)
        #catch os error and see if destination path exists

        if source_path is not None:
            file_obj.close()
   
        self.conn.open(destination_path, "w").write(file_contents)


    def download(self, source_path, destination_path):

        with self.conn.open(source_path, "r") as f:
            data = f.read()
        with open(destination_path, "w") as f:
            f.write(data)

    def delete(self, path):
        self.conn.remove(path)

    def describe(self, path='.'):
        dirlist = self.conn.listdir(path)
        print(dirlist)
        return dirlist

    def recurse(self, path='.', _results = []):
        self.conn.chdir(path)

        for item in self.describe():        
            if self.isdir(item):
                item = '{}/'.format(item)
                _results.append(item)
                self.recurse(item, _results)
            else:
                _results.append(item)
        return _results

    def sync(self, local_path, source_path, mode='PUSH'):

        if mode == 'PULL':
            source_files = self._get_source_files(remote_path, 'REMOTE')
        else:
            source_files = self._get_source_files(local_path)
        
                
    def _get_source_files(self, path):
        pass

    def _recurse_local(self):
        pass

    def _isdir_local(self):
        pass
    
    def _isfile_local(self):
        pass

    def _mkdir_local(self):
        pass

    def isdir(self, path):
        try:
            st_mode = self.conn.stat(path).st_mode
            st_mode_str = stat.filemode(st_mode)
            return str(st_mode_str)[0] == 'd'
        except:
            return False

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()