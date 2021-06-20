# coding=utf-8

import configparser
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import xlrd
import re
import datetime


# 根据列名获取相应序号
def get_column_index(table, column_name):
    columnIndex = None
    for i in range(table.ncols):
        if table.cell_value(0, i).__contains__(column_name):
            columnIndex = i
            break
    return columnIndex


# 读取行纵坐标列的数据
def read_excel(excel_name, x_axis_name, y_axis_name):
    # 打开文件
    work_book = xlrd.open_workbook(excel_name)

    # 1. 获取 sheet 的名字
    all_sheet_names = work_book.sheet_names()

    # 1.2 按索引号获取sheet的名字（string类型）
    sheet1_name = all_sheet_names[0]

    # 2. 获取 sheet 内容
    sheet_content = work_book.sheet_by_name(sheet1_name)

    # 3. sheet 行数，列数
    # print('rows : ', sheet_content.nrows)
    # print('cols : ', sheet_content.ncols)

    # 4. 根据列名获取相应序号
    x_axis_index = get_column_index(sheet_content, x_axis_name)
    # print('(', x_axis_name, ') index : ', x_axis_index)
    y_axis_index = []
    for name in y_axis_name:
        index = get_column_index(sheet_content, name)
        # print('(', name, ') index : ', index)
        y_axis_index.append(index)
    # print('y axis index', y_axis_index)

    table = {}
    # 5. 获取行数据
    x_axis_data = sheet_content.col_values(x_axis_index)
    del (x_axis_data[0])  # 第 1 个元素内容为列名 应该去掉
    # Python读Excel, 返回的单元格内容的类型有5种
    # ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
    x_axis_ctype = sheet_content.cell(1, x_axis_index).ctype  # 第二行第 x_axis_index 列单元格的类型
    if x_axis_ctype == 3:
        time_data = []
        for data in x_axis_data:
            time_data.append(xlrd.xldate.xldate_as_datetime(data, 0))  # 将数据转换为 datatime 格式
        x_axis_data = time_data
    table['x_axis'] = x_axis_data

    y_axis_data = []
    # 6. 获取列数据
    for index in y_axis_index:
        data = sheet_content.col_values(index)
        del (data[0])
        y_axis_data.append(data)
    table['y_axis'] = y_axis_data
    return table


colors = ['blue', 'red', 'green', 'yellow', 'purple', 'orange', 'pink']


# 绘制图形
def draw(x_axis_data, y_axis_data, y_axis_name):
    fig = plt.figure(figsize=(20, 10), dpi=80)
    ax = fig.add_subplot(1, 1, 1)
    index = 0
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    for y_data in y_axis_data:
        ax.plot(x_axis_data, y_data, color=colors[index], linewidth=1.0, linestyle='-', label=y_axis_name[index])
        index = index + 1
    # 如果是时间类型, 设置时间格式
    if isinstance(x_axis_data[0], datetime.datetime):
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d %H:%M'))
        # plt.gcf().autofmt_xdate()  # 自动旋转日期标记
    plt.legend()
    plt.title('figure')
    plt.savefig('figure.png')  # 将图形保存为图片
    plt.show()


config_name = "config.ini"
info = "info"
x_axis_name = "x_axis_name"
y_axis_name = "y_axis_name"

if __name__ == '__main__':
    # 1. 从配置文件读取要画图的行、列信息
    cf = configparser.ConfigParser()
    # 不加编码报错 UnicodeDecodeError: 'gbk' codec can't decode byte 0x80 in position 56: illegal multibyte sequence
    cf.read(config_name, encoding='utf-8')
    excel_name = cf.get(info, "excel_name")
    x_axis_name = cf.get(info, x_axis_name)
    y_axis_name = re.split(r" +", cf.get('info', y_axis_name))  # 此处用正则匹配多个空格
    if len(y_axis_name) > len(colors):
        print("too many y axis name")
        exit()

    # 2. 获取行、列数据
    table = read_excel(excel_name, x_axis_name, y_axis_name)
    x_axis_data = table['x_axis']
    y_axis_data = table['y_axis']

    # 3. 绘制图形
    draw(x_axis_data, y_axis_data, y_axis_name)
