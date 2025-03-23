import os


def check_os():
    platform = os.name
    if platform == 'nt':
        return 'Windows'
    elif platform == 'posix':
        if 'ubuntu' in os.uname().sysname.lower():
            return 'Ubuntu'
        else:
            return 'Linux/Unix'
    else:
        return 'Unknown'
