# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.09.27
"""


# 507sku & 4857order
import sys

import pandas as pd
import time as tm
import os
import numpy as np
import matplotlib.pyplot as plt

from prettytable import PrettyTable
from prettytable import from_csv

from Class import Sku, Section, Order, CostList

from Utilities import randomcolor, Func_Cost_sequence, Func_order_notstart,\
    Func_display_section_sku_list_all, Func_display_section_order_list_all,\
    Func_display_section_sku_list, Func_display_section_order_list,\
    Func_display_order_section_list, Func_display_order_sku_list,\
    Func_display_order, Func_ReadCsv_OrderSku_tool, Func_ReadCsv_OrderSku_improve, Func_ReadCsv_SkuSection,\
    get_with_default


# 程序计时：记下开始时刻


class Simulation:
    def __init__(self, simulation_config):
        self.T = simulation_config['T']
        self.path_sku_section_map = simulation_config['path_sku_section_map']
        self.path_order_sku_map = simulation_config['path_order_sku_map']

        self.num_section = simulation_config['num_section']
        self.num_sku = None
        self.num_order = None

        self.order_notstart = simulation_config['order_notstart']
        self.order_finish = simulation_config['order_finish']
        self.order_ing = simulation_config['order_ing']

        self.section_list = simulation_config['section_list']
        self.sku_list = simulation_config['sku_list']

        # self.read_csv_data()

        self.sku_section_map = None
        self.order_sku_map = None

        # 画图参数
        self.x_t = []
        self.y_0 = []
        self.y_1 = []
        self.y_2 = []
        self.y_3 = []
        self.y_4 = []
        self.y_5 = []

        self.fig = plt.figure()
        # self.sku_processing_time = get_with_default(simulation_config, 'sku_processing_time', 1)
        # self.sku_in_section_info = None

        self.init_section()
        self.init_sku()
        self.init_order()

    # def read_csv_data(self):
    #     self.sku_section_map = pd.read_csv(self.sku_section_file_path).to_numpy()  # 通过pandas读取csv并转化成np.array
    #     self.order_sku_map = pd.read_csv(self.order_sku_file_path).to_numpy()

    def init_section(self):
        # 1\初始化6个section信息：分区名称、正在等待的订单数量、处理订单列表
        for i in range(self.num_section):
            section_input = {
                'name': 'section_{}'.format(i),  # 分区名称
                'num': i,  # 分区序号
                'section_order_num': 0,  # 等待订单的数量，初始为0
                'section_order_list': [],  # 处理订单的列表，不重复
                'section_sku_list': [],  # 处理sku的信息，可以有多个order1
                'section_sku_name_list': []  # 处理sku信息的名称（不是实例）
            }
            self.section_list.append(Section(section_input))
        print('所有section个数为：%d' % self.num_section)

    def init_sku(self):
        # 2\初始化sku所在的分区：sku名称，sku处理所需时间、sku所在分区
        sku_time = 1  # sku处理所需要的时间

        data = np.genfromtxt(
            self.path_sku_section_map,
            delimiter=",")  # 打开Excel文件
        table_SkuSection = PrettyTable()
        fp = open(self.path_sku_section_map, "r")
        table_SkuSection = from_csv(fp)
        print(table_SkuSection)
        fp.close()
        # 获得列数，即有多少个sku
        sku_section_map = pd.read_csv(self.path_sku_section_map)
        self.num_sku = len(sku_section_map.columns) - 2
        print('所有sku数量为：%d ' % self.num_sku)

        # 从表中读取sku所在的分区信息
        for i in range(0, self.num_sku):
            sku_location_list = Func_ReadCsv_SkuSection(
                i, self.num_section, data, self.section_list)  # 统计每行中不为0的列数
            sku_input = {
                'name': 'sku_{}'.format(i),  # sku名称
                'num': i,  # 分区序号
                'sku_time': sku_time,  # sku处理所需时间（默认为1）
                'sku_location_list': sku_location_list  # 后续考虑在表中读取sku的section信息
            }
            self.sku_list.append(Sku(sku_input))

    def init_order(self):
        # 3\初始化订单：订单等候cost、订单中的sku信息、订单的分区经停顺序，计算总等待cost
        time = {
            'enter_section': '',  # 进入分区时间
            'leave_section': '',  # 离开分区时间
            'start_processing': '',  # 开始加工时间
            'section_processing_time_list': [],  # 每个订单在所需经过的分区所需要分拣的时间 【！！！】 初始化需完成
            'waiting_time': '',  # 在某个分区所需等待的时间
        }
        data = np.genfromtxt(
            self.path_order_sku_map,
            delimiter=",")  # 打开Excel文件
        table_OrderSku = PrettyTable()
        fp = open(self.path_order_sku_map, "r")
        table_OrderSku = from_csv(fp)
        print(table_OrderSku)
        fp.close()

        # 获得行数，即有多少个订单
        self.num_order = sum(1 for line in open(self.path_order_sku_map)) - 1
        print('所有order数量为：%d ' % self.num_order)

        # 从表中读取sku所在的分区信息
        for i in range(0, (self.num_order)):
            self.order_sku_list = Func_ReadCsv_OrderSku_improve(
                i, self.num_sku, data, self.sku_list)  # 统计每行中不为0的列数
            order_input = {'name': 'order_{}'.format(i),  # 订单名称
                           'num': i,  # 分区序号
                           'order_time_cost': '0',  # 订单等候时间cost
                           'order_sku_list': self.order_sku_list,  # 订单中的sku信息
                           'order_section_list': [],  # 剩余分区集合
                           'current_section': [],  # 当前所在分区
                           'time': time,
                           'order_section_list_simple': []  # 简单的分区经过信息
                           }
            self.order_notstart.append(Order(order_input))
            # print(self.order_notstart[i].order_sku_list)

    def assign_order(self):
        return

    def evaluate_performance(self):
        return

    def plot_results(self):
        # 绘制图像
        for i in range(len(self.section_list)):
            exec("ax = self.fig.add_subplot(61{})".format(i + 1))
            exec("plt.title(r'$section{}$', fontsize=10)".format(i))

            # plt.title(r'$section{}$', fontsize=10)
            exec(
                "ax.plot(self.x_t, self.y_{}, color=randomcolor(), linewidth=2)".format(i))
        plt.show()

    def func_order_move(self, order_move):
        print('order move not null')
        for i in range(len(order_move)):
            # 1.6在下一个分区新增订单sku
            # 1.6在分区等待队列中增加派发订单的信息(如order_1在section_1有3个sku要做，那就加3个order_1)
            # sku队列加多个order
            # 在section的等待队列中只加order名称
            # exec("section_list[{}].section_order_list.append(order_move[i])".format(order_move[i].order_section_list[0].num))
            # print('.............................%d'%order_move[i].order_section_list[0].num)

            section_list[order_move[i].order_section_list[0].num].section_order_list.append(
                order_move[i])

            for k in range(len(order_move[i].order_sku_list)):
                section_list[order_move[i].order_section_list[0].num].section_sku_list.append(
                    order_move[i])
                section_list[order_move[i].order_section_list[0].num].section_sku_name_list.append(
                    order_move[i].name)
                try:
                    if (order_move[i].order_sku_list[k + 1].sku_location_list[0].name ==
                            order_move[i].order_sku_list[k].sku_location_list[0].name):
                        continue
                    else:
                        break
                except BaseException:
                    break

    def run(self):
        cost = []

        for t in range(1, self.T):
            print("\n")
            print(
                "--------------------------\n     当前时刻为%d\n--------------------------" %
                t)

        # step1：下发新的订单
            try:
                Func_order_notstart(
                    t=t,
                    section_list=self.section_list,
                    order_notstart=self.order_notstart,
                    order_ing=self.order_ing)
            except BaseException:
                print('*********order派发结束*********\n')

            Func_display_section_sku_list_all(self.section_list)
            print('#########order移动##########')
            order_move = []

            table_task = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
            row_task = ['task', '', '', '', '', '', '']

        # step2：对每个section进行遍历，依次完成当前section中的任务
            for i in range(0, 6):
                section_now = self.section_list[i]
                if (len(section_now.section_sku_list) == 0):
                    # print('【【【【%s】】】】无任务' % section_now.name)
                    row_task[i + 1] = 0
                else:
                    # print("【【【【%s】】】】有任务 *"%section_now.name)
                    row_task[i + 1] = 1

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
                        self.section_list[order_now.order_section_list[0].num].section_sku_list.pop(
                            0)
                        self.section_list[order_now.order_section_list[0].num].section_sku_name_list.pop(
                            0)

                        # 1.3 在分区订单等待队列删除派发的一个订单名称
                        Func_display_section_order_list(section_now)
                        self.section_list[order_now.order_section_list[0].num].section_order_list.pop(
                            0)

                        # 1.4 删除order的section和sku记录
                        order_now.order_section_list.pop(0)
                        order_now.order_sku_list.pop(0)
                        # 1.5更新order信息
                        self.order_ing.remove(order_now)
                        self.order_finish.append(order_now)

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
                        section_list[order_now.order_section_list[0].num].section_sku_list.pop(
                            0)
                        section_list[order_now.order_section_list[0].num].section_sku_name_list.pop(
                            0)

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
                        section_list[order_now.order_section_list[0].num].section_sku_list.pop(
                            0)
                        section_list[order_now.order_section_list[0].num].section_sku_name_list.pop(
                            0)
                        # Func_display_section_order_list(section_now)

                        # 1.4 在分区订单等待队列删除派发的一个订单名称
                        section_list[order_now.order_section_list[0].num].section_order_list.pop(
                            0)

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
                    Func_display_section_sku_list_all(self.section_list)
                    Func_display_order(
                        order_notstart=self.order_notstart,
                        order_ing=self.order_ing,
                        order_finish=self.order_finish)
                    # print("\n【删除结束后】当前操作%s的:order_section_list" % order_now.name)
                    # Func_display_order_section_list(order_now)
                    # print("\n【删除结束后】当前操作分区%s的:section_order_list" % section_now.name)
                    # Func_display_section_sku_list(section_now)

            table_task.add_row(row_task)
            print(table_task)
            print('\n')

            # step3：进行order的移动
            if (len(order_move) != 0):
                self.func_order_move(order_move)

            print('【order move完成后】')
            Func_display_section_sku_list_all(self.section_list)

            print('\nt=%d时刻order状态：' % t)
            Func_display_order(
                order_notstart=self.order_notstart,
                order_ing=self.order_ing,
                order_finish=self.order_finish)

            # step5：统计循环次数，作为section中order作业统计的x轴
            self.x_t.append(t)
            # 统计section中的section_sku_list，记录y轴数据
            for i in range(len(self.section_list)):
                exec(
                    "self.y_{}.append(len(section_list[{}].section_sku_list))".format(
                        i, i))
            # for i in range(len(section_list)):
            #     exec("print(y_{})".format(i))

            # 统计最后循环次数
            if ((len(self.order_ing) + len(self.order_notstart)) == 0):
                T_last = t
                break

        print('完成全部订单共计循环次数：%d' % T_last)

        # new_order = self.assign_order()  # 待完成
        #     first_section_id = new_order.order_section_list[0].num
        #     for section in self.section_list:
        #         section.process_order()  # 实现分区内订单的处理（更新时间）以及移动的过程
        #         if first_section_id == section.num:
        #             section.section_order_list.append(new_order)
        # return


if __name__ == "__main__":
    start = tm.perf_counter()

    cwd = os.getcwd()  # 读取当前文件夹路径

    # 1、初始化section
    num_section = 6
    section_list = []
    # 2、初始化sku
    sku_list = []

    # 3、初始化订单
    order_notstart = []  # 未发出的order
    order_finish = []  # 已经流转结束的order
    order_ing = []  # 正在流转过程中的order

    simulation_config = {
        'T': 10000,  # 仿真时长
        'path_sku_section_map': cwd + '/SkuSectionMap_0922.csv',
        'path_order_sku_map': cwd + '/OrderSkuMap_0924.csv',

        'num_section': num_section,

        'order_notstart': order_notstart,
        'order_finish': order_finish,
        'order_ing': order_ing,

        'section_list': section_list,
        'sku_list': sku_list,
    }
    simulation_1 = Simulation(simulation_config)
    simulation_1.run()

    end = tm.perf_counter()
    print("程序共计用时 : %s Seconds " % (end - start))

    # 绘制图像
    simulation_1.plot_results()
