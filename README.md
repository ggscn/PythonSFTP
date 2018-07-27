# PythonSFTP
A simple Python SFTP client

# Basic Operations

**Instantiate**

```client = SFTP('username', 'hostname', 'password')```

**Upload file**

```client.upload('source_path', 'destination_path')```

**Download file**

```client.download('source_path', 'destination_path')```

**List files in directory**

```client.describe('path')```

**Recursively list files in a directory**

```client.recurse('path')```

