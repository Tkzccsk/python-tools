# coding=utf-8
import configparser
import requests
import os
import glob
import shutil

ts_dir_name = 'video'
info = 'info'
config_name = 'config.ini'
m3u8_get_url = 'm3u8_get_url'
meta_file = 'meta_data.m3u8'
file_name = 'video.mp4'


# 下载 ts 文件
def download_ts(ts_url_prefix):
    f = open(meta_file)
    index = 1
    cur_dir = os.getcwd()
    if not os.path.exists(ts_dir_name):
        os.mkdir(ts_dir_name)
    for line in f:
        line = line.strip("\n")
        if line.endswith(".ts"):
            down_res = requests.get(url='{}/{}'.format(ts_url_prefix, line))
            with open(os.path.join(cur_dir, '{}/{}.ts'.format(ts_dir_name, index)), 'wb+') as ts_file:
                ts_file.write(down_res.content)
            index = index + 1


# 合并 ts 文件
def merge_ts_files(dir_name, merge_file_name):
    ts_file_num = len(glob.glob('./{}/*.ts'.format(dir_name)))
    if os.path.exists(merge_file_name):
        os.remove(merge_file_name)
    with open(merge_file_name, 'wb+') as f:
        for i in range(ts_file_num):
            ts_file_name = './{}/{}.ts'.format(dir_name, i + 1)
            f.write(open(ts_file_name, 'rb').read())
    print("merge finished!")


# 删除 ts 文件
def delete_ts_files(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name, True)


if __name__ == '__main__':
    # 1. 从配置文件读取 meu8 url 信息
    cf = configparser.ConfigParser()
    cf.read(config_name, encoding='utf-8')
    m3u8_url = cf.get(info, m3u8_get_url)

    # 2. 下载文件并保存
    r = requests.get(m3u8_url)
    if os.path.exists(meta_file):
        os.remove(meta_file)
    with open(meta_file, 'w') as file:
        file.write(r.text)

    # 3. 提取 ts 文件 url 前缀
    last_index = m3u8_url.rfind('/')
    ts_url_prefix = m3u8_url[:last_index]

    # 4. 下载 ts 文件
    download_ts(ts_url_prefix)

    # 5. 合并 ts 文件
    merge_ts_files(ts_dir_name, file_name)

    # 6. 删除 ts 文件
    delete_ts_files(ts_dir_name)
