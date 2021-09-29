# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.08.20

1212·1·121-1111
"""

# todos:
#     1\未测试如果move到某阶段并且此阶段为最后一段，为何不可以直接finish只能保留在ing

import sys
import os

import pandas as pd
import time as tm
import numpy as np
import matplotlib.pyplot as plt

from prettytable import PrettyTable
from prettytable import from_csv

from Class import Sku, Section, Order, CostList

from Utilities import randomcolor,Func_Cost_sequence,Func_order_notstart,\
    Func_display_section_sku_list_all,Func_display_section_order_list_all,\
    Func_display_section_sku_list,Func_display_section_order_list,\
    Func_display_order_section_list,Func_display_order_sku_list,\
    Func_display_order,Func_ReadCsv_OrderSku_tool,Func_ReadCsv_OrderSku_improve,Func_ReadCsv_SkuSection


# 程序计时：记下开始时刻
start = tm.perf_counter()
cwd = os.getcwd()  # 读取当前文件夹路径

# SkuSectionMap.csv
path_sku_section_map = cwd + '/SkuSectionMap_0922.csv'
# SkuSectionMap.csv
path_order_sku_map = cwd + '/OrderSkuMap_0922improve.csv'
# T为需要仿真最多需要的时间

T = 1000000

##########################################################################
if __name__ == "__main__":
# 1\初始化6个分区信息：分区名称、正在等待的订单数量、处理订单列表
    num_section = 6
    section_list = []
    for i in range(0, (num_section)):
        section_input = {
            'name': 'section_{}'.format(i),  # 分区名称
            'num': i,  # 分区序号
            'section_order_num': 0,  # 等待订单的数量，初始为0
            'section_order_list': [],  # 处理订单的列表，不重复
            'section_sku_list': [],  # 处理sku的信息，可以有多个order1
            'section_sku_name_list': []  # 处理sku信息的名称（不是实例）
        }
        section_list.append(Section(section_input))
    print('所有section个数为：%d' % num_section)

# 2\初始化sku所在的分区：sku名称，sku处理所需时间、sku所在分区
    # 同一分区中的不同sku
    sku_list = []
    sku_time = 1  # sku处理所需要的时间

    data = np.genfromtxt(path_sku_section_map, delimiter=",")  # 打开Excel文件
    table_SkuSection = PrettyTable()
    fp = open(path_sku_section_map, "r")
    table_SkuSection = from_csv(fp)
    print(table_SkuSection)
    fp.close()
    # 获得列数，即有多少个sku
    sku_section_map = pd.read_csv(path_sku_section_map)
    num_sku = len(sku_section_map.columns) - 2
    print('所有sku数量为：%d ' % num_sku)

    # 从表中读取sku所在的分区信息
    for i in range(0, (num_sku)):
        sku_location_list = Func_ReadCsv_SkuSection(
            i, num_section,data,section_list)  # 统计每行中不为0的列数
        sku_input = {
            'name': 'sku_{}'.format(i),  # sku名称
            'num': i,                            # 分区序号
            'sku_time': sku_time,  # sku处理所需时间（默认为1）
            'sku_location_list': sku_location_list  # 后续考虑在表中读取sku的section信息
        }
        sku_list.append(Sku(sku_input))
        # print(sku_list[i].sku_location_list[0].name)

# 3\初始化订单：订单等候cost、订单中的sku信息、订单的分区经停顺序，计算总等待cost
    # 订单构建
    time = {'enter_section': '',                  # 进入分区时间
            'leave_section': '',                  # 离开分区时间
            'start_processing': '',               # 开始加工时间
            'section_processing_time_list': [],   # 每个订单在所需经过的分区所需要分拣的时间
            'waiting_time': '',                   # 在某个分区所需等待的时间
            }

    order_notstart = []  # 未发出的order
    order_finish = []  # 已经流转结束的order
    order_ing = []  # 正在流转过程中的order

    data = np.genfromtxt(path_order_sku_map, delimiter=",")  # 打开Excel文件

    table_OrderSku = PrettyTable()
    fp = open(path_order_sku_map, "r")
    table_OrderSku = from_csv(fp)
    print(table_OrderSku)
    fp.close()

    # 获得行数，即有多少个订单
    num_order = sum(1 for line in open(path_order_sku_map)) - 1
    print('所有order数量为：%d ' % num_order)

    # 从表中读取sku所在的分区信息
    for i in range(0, (num_order)):
        order_sku_list = Func_ReadCsv_OrderSku_improve(
            i, num_sku,data,sku_list)  # 统计每行中不为0的列数
        order_input = {'name': 'order_{}'.format(i),        # 订单名称
                       'num': i,                            # 分区序号
                       'order_time_cost': '0',              # 订单等候时间cost
                       'order_sku_list': order_sku_list,   # 订单中的sku信息
                       'order_section_list': [],           # 剩余分区集合
                       'current_section': [],              # 当前所在分区
                       'time': time,
                       'order_section_list_simple': []     # 简单的分区经过信息
                       }
        order_notstart.append(Order(order_input))
        # print(order_notstart[i].order_sku_list)

# 仿真Simulation
    cost = []
    # #T为需要计算的时间
    # T=100

    # 画图表示每个section的工作负荷
    x_t = []
    for i in range(len(section_list)):
        exec("y_{}=[]".format(i))

    for t in range(1, T):
        print("\n")
        print("--------------------------\n     当前时刻为%d\n--------------------------" %t)

        try:
            Func_order_notstart(
                t=t,
                section_list=section_list,
                order_notstart=order_notstart,
                order_ing=order_ing)
        except BaseException:
            print('*********order派发结束*********\n')

        Func_display_section_sku_list_all(section_list)
        print('#########order移动##########')
        order_move = []

        table_task = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
        row_task = ['task', '', '', '', '', '', '']

        for i in range(0, 6):
            section_now = section_list[i]
            if (len(section_now.section_sku_list) == 0):
                # print('【【【【%s】】】】无任务' % section_now.name)
                row_task[i + 1] = 0
            else:
                # print("【【【【%s】】】】有任务 *"%section_now.name)
                row_task[i + 1] = 1

                # print('【order移动前】')
                # Func_display_section_sku_list_all(section_list)
                # Func_display_section_sku_list(section_now)

                order_now = section_now.section_sku_list[0]
                sku_now = section_now.section_sku_list[0].order_sku_list[0]
                try:
                    print(
                        '%s' %
                        section_now.name,
                        '要完成的order为：%s' %
                        order_now.name,
                        ',sku为%s' %
                        sku_now.name,
                        ',下一个sku为%s' %
                        section_now.section_sku_list[0].order_sku_list[1].name)
                except BaseException:
                    print(
                        '%s' %
                        section_now.name,
                        '要完成的order为：%s' %
                        order_now.name,
                        ',sku为%s' %
                        sku_now.name)
                # Func_display_order_section_list(order_now)
                # Func_display_section_sku_list(section_now)

                # 分类讨论
                # 1:如果order_section_list只剩下一个，则调整order至order finish
                if (len(order_now.order_section_list) == 1):
                    print("$$$%s进入最后一个周期" % order_now.name)
                    # 1。1更新订单时间信息
                    order_now.current_section.append(section_now.name)
                    order_now.time['section_processing_time_list'] = 1
                    order_now.time['waiting_time'] = len(
                        section_now.section_sku_list) - 1

                    # 1.2 在分区sku等待队列中删除派发sku的信息
                    exec(
                        "section_list[{}].section_sku_list.pop(0)".format(
                            order_now.order_section_list[0].num))
                    exec(
                        "section_list[{}].section_sku_name_list.pop(0)".format(
                            order_now.order_section_list[0].num))
                    # 1.3 在分区订单等待队列删除派发的一个订单名称
                    Func_display_section_order_list(section_now)
                    exec(
                        "section_list[{}].section_order_list.pop(0)".format(
                            order_now.order_section_list[0].num))

                    # 1.4 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)
                    # 1.5更新order信息
                    order_ing.remove(order_now)
                    order_finish.append(order_now)

                # 2:如果order_section_list还剩下多个，并且下一个section与当前相同，则不需要移动
                elif ((order_now.order_section_list[1] == order_now.order_section_list[0])):
                    # 1.1更新order的当前分区current_section
                    print('下一个section与当前相同，不需要移动')
                    order_now.current_section.append(section_now.name)
                    # 1.2更新order的时间
                    # 在该section的实际操作时间（仅本订单）
                    key = 1
                    for i in range(1, len(order_now.order_section_list)):
                        if (order_now.order_section_list[i]
                                != order_now.order_section_list[0]):
                            break
                        else:
                            key = key + 1
                    order_now.time['section_processing_time_list'] = key
                    # 在该section的等待时间
                    order_now.time['waiting_time'] = len(
                        section_now.section_sku_list) - 1
                    # print("【%s" % order_now.name, "移动】waiting time=%s" % order_now.time['waiting_time'])

                    # 1.2 在分区等待队列中删除派发订单的信息
                    exec(
                        "section_list[{}].section_sku_list.pop(0)".format(
                            order_now.order_section_list[0].num))
                    exec(
                        "section_list[{}].section_sku_name_list.pop(0)".format(
                            order_now.order_section_list[0].num))

                    # 1.4 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)

                # 3:如果order_section_list还剩下多个，下一个section与当前不同，则将订单信息加到下一个section中
                elif ((order_now.order_section_list[1] != order_now.order_section_list[0])):
                    print(
                        "$$$%s在当前section只剩1个sku，将在下一时间转移到下一个section" %
                        order_now.name)

                    # 1.1更新order的当前分区current_section
                    order_now.current_section.append(section_now.name)
                    # 1.2更新order的时间
                    # 在该section的实际操作时间（仅本订单）
                    key = 1
                    for i in range(1, len(order_now.order_section_list)):
                        if (order_now.order_section_list[i]
                                != order_now.order_section_list[0]):
                            break
                        else:
                            key = key + 1
                    order_now.time['section_processing_time_list'] = key
                    # 在该section的等待时间
                    order_now.time['waiting_time'] = len(
                        section_now.section_sku_list) - 1
                    # print("【%s" % order_now.name, "移动】waiting time=%s" % order_now.time['waiting_time'])

                    # 1.3 在分区等待队列中删除派发订单的信息
                    exec(
                        "section_list[{}].section_sku_list.pop(0)".format(
                            order_now.order_section_list[0].num))
                    exec(
                        "section_list[{}].section_sku_name_list.pop(0)".format(
                            order_now.order_section_list[0].num))
                    # Func_display_section_order_list(section_now)

                    # 1.4 在分区订单等待队列删除派发的一个订单名称
                    exec(
                        "section_list[{}].section_order_list.pop(0)".format(
                            order_now.order_section_list[0].num))

                    # 1.5 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)

                    # 记录待移动的订单，在遍历所有section后进行移动，防止同一时间订单在多个section完成
                    order_move.append(order_now)
                    # print(order_move[0])
                else:
                    print("特别情况，for no reason")
                # 1.4显示每个分区的订单\sku排序、订单信息
                # print('【order完成后】')
                Func_display_section_sku_list_all(section_list)
                # print('****************')
                Func_display_order(order_notstart=order_notstart, order_ing=order_ing, order_finish=order_finish)
                # print("\n【删除结束后】当前操作%s的:order_section_list" % order_now.name)
                # Func_display_order_section_list(order_now)
                #
                # print("\n【删除结束后】当前操作分区%s的:section_order_list" % section_now.name)
                # Func_display_section_sku_list(section_now)

        table_task.add_row(row_task)
        print(table_task)
        print('\n')

        # section遍历结束后进行order移动
        if (len(order_move) != 0):
            print('order move not null')
            for i in range(len(order_move)):
                # 1.6在下一个分区新增订单sku
                # 1.6在分区等待队列中增加派发订单的信息(如order_1在section_1有3个sku要做，那就加3个order_1)
                # sku队列加多个order
                # 在section的等待队列中只加order名称
                # exec("section_list[{}].section_order_list.append(order_move[i])".format(order_move[i].order_section_list[0].num))
                # print('.............................%d'%order_move[i].order_section_list[0].num)
                exec(
                    "section_list[{}].section_order_list.append(order_move[i])".format(
                        order_move[i].order_section_list[0].num))

                for k in range(len(order_move[i].order_sku_list)):
                    exec(
                        "section_list[{}].section_sku_list.append(order_move[i])".format(
                            order_move[i].order_section_list[0].num))
                    exec(
                        "section_list[{}].section_sku_name_list.append(order_move[i].name)".format(
                            order_move[i].order_section_list[0].num))
                    try:
                        if (order_move[i].order_sku_list[k + 1].sku_location_list[0].name ==
                                order_move[i].order_sku_list[k].sku_location_list[0].name):
                            continue
                        else:
                            break
                    except BaseException:
                        break

        print('【order move完成后】')
        Func_display_section_sku_list_all(section_list)

        print('\nt=%d时刻order状态：' % t)
        Func_display_order(order_notstart=order_notstart, order_ing=order_ing, order_finish=order_finish)


        # 统计循环次数，作为section中order作业统计的x轴
        x_t.append(t)
        # 统计section中的section_sku_list，记录y轴数据
        for i in range(len(section_list)):
            exec(
                "y_{}.append(len(section_list[{}].section_sku_list))".format(
                    i,
                    i))
        # for i in range(len(section_list)):
        #     exec("print(y_{})".format(i))

        # 统计最后循环次数
        if((len(order_ing) + len(order_notstart)) == 0):
            T_last = t
            break

    print('完成全部订单共计循环次数：%d' % T_last)

# 统计程序用时
end = tm.perf_counter()
print("程序共计用时 : %s Seconds " % (end - start))

# 绘制图像
fig = plt.figure()
for i in range(len(section_list)):
    exec("ax = fig.add_subplot(61{})".format(i + 1))
    exec("plt.title(r'$section{}$', fontsize=10)".format(i))

    # plt.title(r'$section{}$', fontsize=10)
    exec("ax.plot(x_t, y_{}, color=randomcolor(), linewidth=2)".format(i))
plt.show()
