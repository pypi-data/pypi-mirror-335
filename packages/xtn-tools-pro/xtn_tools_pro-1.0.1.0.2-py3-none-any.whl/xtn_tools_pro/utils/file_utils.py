#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    文件
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/13    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os
import re


def get_file_extension(file_name):
    """
        根据文件名获取文件扩展名/后缀名
    :param file_name: 文件名称
    :return:
    """
    _, file_extension = os.path.splitext(file_name)
    return file_extension


def get_file_check_filename(file_name):
    """
        传入文件名返回一个合法的文件名 会替换掉一些特殊符号 常用于爬虫写文件时文件名中带有特殊符号的情况...
    :param filename: 文件名
    :return:
    """
    file_extension = get_file_extension(file_name)
    # 删除非法字符
    sanitized_filename = re.sub(r'[\/:*?"<>|]', '', file_name)
    max_length = 255  # 操作系统限制文件名的最大长度为255个
    sanitized_filename = sanitized_filename[:max_length]
    return sanitized_filename


def mkdirs_dir(file_path):
    """
        传入一个文件路径创建对应的文件夹，如果某一段不存在则一路创建下去
    :param file_path:
    :return:
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def check_file_exists(file_path):
    """
        传入一个文件路径，判断文件是否存在
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        return True
    return False


def is_dir(dir_path):
    """
        传入文件夹判断是否为文件夹或文件夹是否存在
        传入的如果是文件路径则返回False
        传入的如果是一个不存在的文件夹则返回False
    :param dir_path:
    :return:
    """
    if not os.path.isdir(dir_path):
        return False
    return True


def get_listdir(dir_path):
    """
        获取指定文件夹下的所有文件
    :param dir_path:
    :return:
    """
    return os.listdir(dir_path)


if __name__ == '__main__':
    pass
    print(get_file_extension('file/2024-04-19/BOSCH GEX 125-1A/125-1AE砂磨机操作说明书:[1]_jingyan.txt'))
    print(get_file_check_filename('file/2024-04-19/BOSCH GEX 125-1A/125-1AE砂磨机操作说明书:[1]_jingyan.txt'))
