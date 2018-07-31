import pytest
import os

from pythonsftp.sftp import SFTP

with open('.env') as f:
    content = f.readlines()
creds = [x.strip() for x in content] 

def test_describe_root():
    sftp = SFTP(creds[1],creds[0],creds[2])
    with open('test','w') as f:
        f.write('test')
    sftp.upload('test')
    
    os.remove('test')
    file_list = sftp.describe()
    sftp.delete('test')
    assert len(file_list) > 0

def test_recurse_root():
    sftp = SFTP(creds[1],creds[0],creds[2])
    with open('test','w') as f:
        f.write('test')
    sftp.upload('test')
    
    os.remove('test')
    file_list = sftp.recurse()
    sftp.delete('test')
    print(file_list)
    assert len(file_list) > 0

