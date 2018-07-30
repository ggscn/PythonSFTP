import pytest

from pythonsftp.sftp import SFTP

with open('.env') as f:
    content = f.readlines()
creds = [x.strip() for x in content] 

def test_create_connection_with_password_auth():
    assert SFTP(creds[1],creds[0],creds[2]).conn is not None


