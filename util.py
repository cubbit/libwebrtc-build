import os
import subprocess
import sys

import config

def cd(*path):
    abs_path = getpath(*path)
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)
    os.chdir(abs_path)
    print('cd : ' + abs_path)


def cp(src, dst):
    shutil.copy(src, dst)
    print('cp : ' + src + ' ' + dst)


def emptydir(*path):
    abs_path = getpath(*path)
    if os.path.exists(abs_path):
        shutil.rmtree(abs_path)
    os.mkdir(abs_path)
    print('mkdir : ' + abs_path)


def exec(*cmds):
    print('exec : ' + ' '.join(cmds))
    subprocess.check_call(cmds, shell=(sys.platform == 'win32'))


def exec_stdout(*cmds):
    proc = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    return proc.stdout.read()


def exec_stdin(data, *cmds):
    print('exec : ' + ' '.join(cmds))
    print(data)
    proc = subprocess.Popen(cmds, stdin=subprocess.PIPE)
    proc.communicate(data.encode('utf-8'))


def exists(*path):
    abs_path = getpath(*path)
    return os.path.exists(abs_path)


def getpath(*path):
    return os.path.join(config.PATH_ROOT, *path)


def mv(src, dst):
    shutil.move(src, dst)
    print('mv : ' + src + ' ' + dst)


def rm(*path):
    abs_path = getpath(*path)
    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
