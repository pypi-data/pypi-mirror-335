# This file is part of mesibo PatANN Python SDK for various platforms.
#         
# By accessing and utilizing this work, you hereby acknowledge that you have thoroughly 
# reviewed, comprehended, and commit to adhering to the terms and conditions stipulated 
# on the mesibo website, thereby entering into a legally binding agreement.
# 
# https://mesibo.com
#
# Copyright (c) 2019-Present Mesibo Inc, San Francisco, United States
# All rights reserved.
#  



__patann_version__ = '0.0.71'


import ctypes
import platform
import multiprocessing
import sys
import os
import warnings
import inspect
import filecmp
import numpy as np

def system_exit_error(err):
    info = "\nSystem: " + platform.system().lower() +  "\nPlatform: " + platform.machine() + "\nVersion: " + get_version_folder() + "\n" + "patann: " + __patann_version__;
    raise SystemExit(info + "\n\n==> Error: " + err + "\n")

def get_version_folder():
    return platform.python_version_tuple()[0] + "." + platform.python_version_tuple()[1]

def get_system():
    system = platform.system().lower()
    if("" == system):
        system = "unknown"

    if("cygwin" in system):
        system = "windows"

    if("darwin" in system):
        system = "macos"

    return system

def get_platform_folder():
    system = get_system()

    machine = platform.machine()
    if("" == machine):
        machine = "unknown"

    if(machine.lower() == "amd64"):
        machine = "x86_64"

    return os.path.join(system.lower(), machine.lower())

def get_patann_lib():
    system = get_system()
    lib = "libpatann.so"
    if(system == "windows"):
        lib = "patann.dll"
    return lib

def get_pypatann_lib():
    system = get_system()
    lib = "_patann.so"
    if(system == "windows"):
        lib = "_patann.pyd"
    system = platform.system().lower()
    if("cygwin" in system):
        lib = "_patann.dll"
    return lib

def get_pypatann_checksum():
    return "_patann.sum"

CLIB_DIR = "clib"
def get_full_path_to_lib():
    package_dir = os.path.dirname(os.path.realpath(__file__))
    clib_dir = os.path.join(package_dir, CLIB_DIR)
    platform_lib = get_platform_folder()
    lib_path = os.path.join(clib_dir, platform_lib)
    return lib_path

def get_pypatann_path():
    path = get_full_path_to_lib()
    path = os.path.join(path, get_version_folder())
    return path

def set_path_to_lib():
    sys.path.append(get_pypatann_path());

def get_patann_lib_path():
    path = get_full_path_to_lib()
    return os.path.join(path, get_patann_lib())

def get_pypatann_lib_path():
    path = get_pypatann_path()
    return os.path.join(path, get_pypatann_lib())

def get_python_lib_path():
    package_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(package_dir, get_pypatann_lib())

def get_pypatann_checksum_path():
    path = get_pypatann_path()
    return os.path.join(path, get_pypatann_checksum())

def get_python_checksum_path():
    package_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(package_dir, get_pypatann_checksum())

def excepthook(type, value, traceback):
    print(value)

def is_installed():
    if not os.path.exists(get_pypatann_checksum_path()):
        return False
    if not os.path.exists(get_pypatann_lib_path()):
        return False
    return True

def is_copied():
    if not os.path.exists(get_python_lib_path()):
        return False

    pypath = get_python_checksum_path()
    patannpath = get_pypatann_checksum_path()
    if not os.path.exists(pypath):
        return False

    try:
        filecmp.clear_cache()
        return filecmp.cmp(pypath, patannpath, False)
    except Exception:
        return False

def copy_files():
    if(is_copied()):
        return

    pypath = get_python_checksum_path()
    patannpath = get_pypatann_checksum_path()

    import shutil
    try:
        shutil.copy2(patannpath, pypath)
        pypath = get_python_lib_path()
        patannpath = get_pypatann_lib_path()
        shutil.copy2(patannpath, pypath)
    except Exception:
        pass

    if(is_copied()):
        return

    sys.excepthook = excepthook
    patannpath = get_pypatann_path()
    package_dir = os.path.dirname(os.path.realpath(__file__))
    error = "patann requires following file to be copied. Execute the following command to copy and try again:\n\n $ sudo /bin/cp -f " + patannpath + "/* " + package_dir + "/\n";
    system_exit_error(error)


if not is_installed():
    error = "missing files. Please uninstall and install patann again\n";
    system_exit_error(error)

set_path_to_lib();
copy_files();

if __package__ or "." in __name__:
    from ._patann import *
else:
    from _patann import *

def _get_raw_string(s):
    if(not s):
        s = ""
    return s.encode('raw_unicode_escape')

_patann_lib = get_patann_lib_path()

print("PatANN Python module Version: " + __patann_version__)
python_version = str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro)
print("Python Version: " + python_version)

system = platform.system().lower()
if("cygwin" in system):
    if 'CYGWINPATH' in os.environ:
        cygpath = os.environ['CYGWINPATH']
        _patann_lib = cygpath + _patann_lib
    else:
        _patann_lib = os.path.relpath(_patann_lib)

if(0 != patann_init(_patann_lib, __patann_version__, python_version)):
    system_exit_error('Unable to load: '+ _patann_lib + ' Platform not supported. Contact us at https://mesibo.com/support')

def getPatANNInstance(dim):
    return PatANNInstance(dim);



