# -*- coding: UTF-8 –*-
import platform
import getpass
import os
import sys

"""
专门用来设置 support 文件夹路径
support 文件夹包含很多配置类文件，是程序必不可少的依赖
"""


class SetSupport:
    def __init__(self, dirname):
        self.dirname = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), dirname)


if __name__ == '__main__':
    s = SetSupport(dirname='support').dirname
    print(s)
