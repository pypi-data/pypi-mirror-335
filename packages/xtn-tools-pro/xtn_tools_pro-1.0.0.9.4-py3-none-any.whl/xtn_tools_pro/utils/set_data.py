#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明
#    大文件去重
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/3/11    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os
import fnmatch
import hashlib
from tqdm import tqdm
from xtn_tools_pro.utils.log import Log
from xtn_tools_pro.utils.helpers import get_orderId_random
from xtn_tools_pro.utils.file_utils import mkdirs_dir, get_file_extension, is_dir, get_listdir


class PSetDataObj:
    def __init__(self):
        # 随机生成一个临时文件夹
        self.__order_id = get_orderId_random()
        temp_dir_name = f"temp_{self.__order_id}\\"
        now_current_working_dir = os.getcwd()
        self.__now_current_working_dir = os.path.join(now_current_working_dir, temp_dir_name)
        mkdirs_dir(self.__now_current_working_dir)

        self.__logger = Log('set_data', './xxx.log', log_level='DEBUG', is_write_to_console=True,
                            is_write_to_file=False,
                            color=True, mode='a', save_time_log_path='./logs')

    def set_file_data_air(self, set_file_path, num_shards=1000):
        """
            对单个文件去重，air版本，不对文件做任何修改，去重任何数据
        :param set_file_path:单文件路径
        :param num_shards:临时文件切片，推荐:数据越大值越大 1000
        :return:
        """
        if get_file_extension(set_file_path) != ".txt":
            self.__logger.critical("文件不合法，只接受.txt文件")
            return
        self.__logger.info("正在读取文件总行数...")

        with open(set_file_path, "r", encoding="utf-8") as fp_r:
            line_count = sum(1 for _ in fp_r)
        self.__logger.info(f"读取文件完成,总行数为:{line_count}")

        num_shards = 3000 if num_shards >= 3000 else num_shards
        num_shards = 3000 if line_count >= 30000000 else num_shards
        num_shards = 1000 if num_shards <= 1 else num_shards

        shard_file_obj_list = []
        shard_path_list = []
        for _ in range(num_shards):
            shard_path = f"{os.path.join(self.__now_current_working_dir, f'{self.__order_id}_shard_{_}.tmp')}"
            shard_path_list.append(shard_path)
            shard_file_obj_list.append(open(shard_path, "w", encoding="utf-8"))

        with open(set_file_path, "r", encoding="utf-8") as f_r:
            tqdm_f = tqdm(f_r, total=line_count, desc="正在去重(1/2)",
                          bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
            for line_i in tqdm_f:
                line = line_i.strip().encode()
                line_hash = hashlib.md5(line).hexdigest()
                shard_id = int(line_hash, 16) % num_shards
                shard_file_obj_list[shard_id].write(line_i)

        for shard_file_obj in shard_file_obj_list:
            shard_file_obj.close()

        result_w_path = os.path.join(self.__now_current_working_dir, "000_去重结果.txt")
        tqdm_f = tqdm(shard_path_list, total=len(shard_path_list), desc="正在去重(2/2)",
                      bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
        with open(result_w_path, "w", encoding="utf-8") as f_w:
            for shard_path in tqdm_f:
                with open(shard_path, "r", encoding="utf-8") as f_r:
                    seen_list = []
                    for line_i in f_r.readlines():
                        line = line_i.strip()
                        seen_list.append(line)
                    seen_list = list(set(seen_list))
                    w_txt = "\n".join(seen_list)
                    f_w.write(w_txt + "\n")
                os.remove(shard_path)  # 删除临时文件

        with open(result_w_path, "r", encoding="utf-8") as fp_r:
            line_count = sum(1 for _ in fp_r)
        self.__logger.info(f"文件处理完毕,去重后总行数为:{line_count},结果路径:{result_w_path}")

    def set_file_data_pro(self, set_file_dir_path, num_shards=3000):
        """
            对文件夹下的所有txt文件去重，pro版本，不对文件做任何修改，去重任何数据
        :param set_file_dir_path:文件夹路径
        :param num_shards:临时文件切片，推荐:数据越大值越大 1000
        :return:
        """
        if not is_dir(set_file_dir_path):
            self.__logger.critical("文件夹不存在或不合法")
            return

        self.__logger.info("正在统计文件可去重数量...")
        set_file_path_list = []
        for set_file_name in get_listdir(set_file_dir_path):
            if fnmatch.fnmatch(set_file_name, '*.txt'):
                set_file_path_list.append(os.path.join(set_file_dir_path, set_file_name))
        self.__logger.info(f"当前文件夹下可去重文件数量为:{len(set_file_path_list)}")

        num_shards = 3000 if num_shards >= 3000 else num_shards
        num_shards = 1000 if num_shards <= 1000 else num_shards

        shard_file_obj_list = []
        shard_path_list = []
        for _ in range(num_shards):
            shard_path = f"{os.path.join(self.__now_current_working_dir, f'{self.__order_id}_shard_{_}.tmp')}"
            shard_path_list.append(shard_path)
            shard_file_obj_list.append(open(shard_path, "w", encoding="utf-8"))

        for _ in range(len(set_file_path_list)):
            set_file_path = set_file_path_list[_]
            with open(set_file_path, "r", encoding="utf-8") as fp_r:
                line_count = sum(1 for _ in fp_r)
            # self.__logger.info(f"{set_file_path}读取完成,总行数为:{line_count}")

            with open(set_file_path, "r", encoding="utf-8") as f_r:
                tqdm_f = tqdm(f_r, total=line_count, desc=f"正在去重({_ + 1}/{len(set_file_path_list) + 1})",
                              bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
                for line_i in tqdm_f:
                    line = line_i.strip().encode()
                    line_hash = hashlib.md5(line).hexdigest()
                    shard_id = int(line_hash, 16) % num_shards
                    shard_file_obj_list[shard_id].write(line_i)

        for shard_file_obj in shard_file_obj_list:
            shard_file_obj.close()

        result_w_path = os.path.join(self.__now_current_working_dir, "000_去重结果.txt")
        tqdm_f = tqdm(shard_path_list, total=len(shard_path_list),
                      desc=f"正在去重({len(set_file_path_list) + 1}/{len(set_file_path_list) + 1})",
                      bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
        with open(result_w_path, "w", encoding="utf-8") as f_w:
            for shard_path in tqdm_f:
                with open(shard_path, "r", encoding="utf-8") as f_r:
                    seen_list = []
                    for line_i in f_r.readlines():
                        line = line_i.strip()
                        seen_list.append(line)
                    seen_list = list(set(seen_list))
                    w_txt = "\n".join(seen_list)
                    f_w.write(w_txt + "\n")
                os.remove(shard_path)  # 删除临时文件

        with open(result_w_path, "r", encoding="utf-8") as fp_r:
            line_count = sum(1 for _ in fp_r)
        self.__logger.info(f"文件处理完毕,去重后总行数为:{line_count},结果路径:{result_w_path}")

    def merging_data(self, file_dir_path, merging_new_file_name="合并"):
        """
            传入一个文件夹,合并这个文件夹下所有.txt的数据
        :param file_dir_path: 文件夹
        :param merging_new_file_name: 新的输出位置
        :return:
        """
        if not is_dir(file_dir_path):
            self.__logger.critical("文件夹不存在或不合法")
            return

        self.__logger.info("正在统计文件可合并数量...")
        file_path_list = []
        for set_file_name in get_listdir(file_dir_path):
            if fnmatch.fnmatch(set_file_name, '*.txt'):
                if set_file_name == f"{merging_new_file_name}.txt": continue
                file_path_list.append(os.path.join(file_dir_path, set_file_name))
        self.__logger.info(f"当前文件夹下可合并文件数量为:{len(file_path_list)}")

        result_w_path = os.path.join(file_dir_path, f"{merging_new_file_name}.txt")

        with open(result_w_path, "w", encoding="utf-8") as f_w:
            for _ in range(len(file_path_list)):
                file_path = file_path_list[_]
                with open(file_path, "r", encoding="utf-8") as fp_r:
                    line_count = sum(1 for _ in fp_r)

                with open(file_path, "r", encoding="utf-8") as f_r:
                    tqdm_f = tqdm(f_r, total=line_count,
                                  desc=f"正在合并({_ + 1}/{len(file_path_list)})",
                                  bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
                    for line_i in tqdm_f:
                        line = line_i.strip()
                        f_w.write(line + "\n")

    def split_data(self, file_path, split_new_file_name="分割", file_index=1, file_max_line=1000000):
        if get_file_extension(file_path) != ".txt":
            self.__logger.critical("文件不合法，只接受.txt文件")
            return
        self.__logger.info("正在读取文件总行数...")

        with open(file_path, "r", encoding="utf-8") as fp_r:
            line_count = sum(1 for _ in fp_r)
        self.__logger.info(f"读取文件完成,总行数为:{line_count}")

        with open(file_path, "r", encoding="utf-8") as f_r:
            tqdm_f = tqdm(f_r, total=line_count, desc="正在分割(1/1)",
                          bar_format="{l_bar}{bar}|{n}/{total} [预计完成时间:{remaining}]")
            temp_line_list = []
            parent_path = os.path.dirname(file_path)
            for line_i in tqdm_f:
                line = line_i.strip()
                temp_line_list.append(line)
                if len(temp_line_list) == file_max_line:
                    result_w_path = os.path.join(parent_path, f"{split_new_file_name}_{file_index}.txt")
                    self.__list_to_write_file(result_w_path, temp_line_list)
                    temp_line_list = []
                    file_index += 1
            if temp_line_list:
                result_w_path = os.path.join(parent_path, f"{split_new_file_name}_{file_index}.txt")
                self.__list_to_write_file(result_w_path, temp_line_list)

    def __list_to_write_file(self, file_w_path, data_list):
        with open(file_w_path, "w", encoding="utf-8") as result_w_f:
            result_w_f.write("\n".join(data_list))
