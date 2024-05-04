# -*- coding: utf-8 -*-：
##ZXW
import os


def wirte_error(info):
    path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '\log'
    # print(path)
    if os.path.exists(path):
        path = path + '\error.txt'
        if os.path.exists(path):
            f = open(path, 'a')
            f.write(info)
            f.close()
        else:
            f = open(path, 'w')
            f.write(info)
            f.close()

    else:
        os.makedirs(path)
        path = path + '\error.txt'
        f = open(path, 'w')
        f.write(info)
        f.close()