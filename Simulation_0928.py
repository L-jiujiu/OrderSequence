# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.09.28d

"""

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
    Func_display_order_section_list, Func_display_order_sku_list, Func_display_order,\
    Func_ReadCsv_OrderSku_tool, Func_ReadCsv_OrderSku_improve, Func_ReadCsv_SkuSection, Func_ReadCsv_SkuTime,\
    get_with_default

# 程序计时：记下开始时刻
start = tm.perf_counter()


class Simulation:
    def __init__(self, simulation_config):
        self.T = simulation_config['T']
        self.path_sku_section_map = simulation_config['path_sku_section_map']
        self.path_order_sku_map = simulation_config['path_order_sku_map']
        self.path_sku_time_map = simulation_config['path_sku_time_map']

        self.num_section = simulation_config['num_section']
        self.num_sku = None
        self.num_order = None

        self.order_notstart = simulation_config['order_notstart']
        self.order_finish = simulation_config['order_finish']
        self.order_ing = simulation_config['order_ing']
        self.order_start = simulation_config['order_start']

        self.section_list = simulation_config['section_list']
        self.sku_list = simulation_config['sku_list']
        self.sku_time_list = simulation_config['sku_time_list']
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

        self.y_0_before=[]
        self.y_1_before = []
        self.y_2_before = []
        self.y_3_before = []
        self.y_4_before = []
        self.y_5_before = []

        self.fig = plt.figure()
        # self.sku_processing_time = get_with_default(simulation_config, 'sku_processing_time', 1)
        # self.sku_in_section_info = None

        self.init_section()
        self.init_sku()
        self.init_order()
    def init_section(self):
        # 1\初始化6个section信息：分区名称、正在等待的订单数量、处理订单列表
        for i in range(self.num_section):
            section_input = {
                'name': 'section_{}'.format(i),  # 分区名称
                'num': i,  # 分区序号
                'section_order_num': 0,  # 等待订单的数量，初始为0
                'section_order_list': [],  # 处理订单的列表，可重复
                'section_order_list_simple': [],  # 处理订单的列表，不重复
                'section_sku_list': [],  # 处理sku的信息，可以有多个order1
                'section_sku_name_list': [],  # 处理sku信息的名称（不是实例）
                'section_waiting_order':[] #section中总共需要处理的ordersku的数量
            }
            self.section_list.append(Section(section_input))
        print('所有section个数为：%d' % self.num_section)

    def init_sku(self):
        # 2\初始化sku所在的分区：sku名称，sku处理所需时间、sku所在分区
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
        self.num_sku = len(sku_section_map.columns) - 1
        print('所有sku数量为：%d ' % self.num_sku)

        # sku_time_list:添加sku的处理时长信息
        Func_ReadCsv_SkuTime(
            path_sku_time_map=self.path_sku_time_map,
            num_sku=self.num_sku,
            sku_time_list=self.sku_time_list)
        # print("skutimelist表格为：")
        # print(self.sku_time_list)

        # 从表中读取sku所在的分区信息
        for i in range(0, self.num_sku):
            sku_location_list = Func_ReadCsv_SkuSection(
                i, self.num_section, data, self.section_list)  # 统计每行中不为0的列数
            sku_input = {
                'name': 'sku_{}'.format(i),  # sku名称
                'num': i,  # 分区序号
                'sku_time': self.sku_time_list[i],  # sku处理所需时间（默认为1）
                'sku_location_list': sku_location_list  # 后续考虑在表中读取sku的section信息
            }
            self.sku_list.append(Sku(sku_input))
        # print(self.sku_list[5].sku_time)

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
        # table_OrderSku = PrettyTable()
        # fp = open(self.path_order_sku_map, "r")
        # table_OrderSku = from_csv(fp)
        # print(table_OrderSku)
        # fp.close()

        # 获得行数，即有多少个订单
        self.num_order = sum(1 for line in open(self.path_order_sku_map)) - 1
        print('所有order数量为：%d ' % self.num_order)

        # 从表中读取sku所在的分区信息
        for i in range(0, (self.num_order)):
            # print('order_%d'%i)
            order_sku_list, order_section_list,order_section_time_list = Func_ReadCsv_OrderSku_improve(
                i, self.num_sku, data, self.sku_list, self.num_section)  # 统计每行中不为0的列数
            order_input = {'name': 'order_{}'.format(i),  # 订单名称
                           'num': i,  # 分区序号
                           'order_time_cost': '0',  # 订单等候时间cost
                           'order_sku_list': order_sku_list,  # 订单中的sku信息
                           'order_section_list': order_section_list,  # 剩余分区集合
                           'current_section': [],  # 当前所在分区
                           'time': time,
                           'order_section_list_simple': [],  # 简单的分区经过信息
                           'path_order_sku_map': self.path_order_sku_map,
                           'order_section_time_list':order_section_time_list #订单在每个分区的处理时间
                           }
            self.order_notstart.append(Order(order_input))
        # for order in order_notstart:
        #     print(order.name)
        #     for i in order.order_section_time_list:
        #         print(i)
        # for i in range(len(order_notstart[3].order_sku_list)):
        #     print(order_notstart[3].order_sku_list[i].name)
        # #【测试】order section list和order sku list是否可以正确添加
        # print('order_sku_list:')
        # for order_sku in self.order_notstart[i].order_sku_list:
        #     print(order_sku.name)
        # print('order_section_list:')
        # for order_section in self.order_notstart[i].order_section_list:
        #     print(order_section.name)
        # print('\n')

    def assign_order(self):
        return

    def evaluate_performance(self):
        return

    def plot_results(self, mode, y_lim):
        # 绘制图像

        for i in range(len(self.section_list)):
            exec("ax = self.fig.add_subplot(61{})".format(i + 1))
            exec("plt.title(r'$section{}$', fontsize=10)".format(i))
            if(mode == 1):
                plt.ylim((0, y_lim))
            # plt.title(r'$section{}$', fontsize=10)
            exec(
                "ax.plot(self.x_t, self.y_{}, color=randomcolor(), linewidth=2)".format(i))

        # 显示section_waiting_list最长的时刻和队列长度
        for i in range(6):
            exec('print("Max Section_{}(t=%d"%self.y_{}.index(max(self.y_{})),")=%d" %max(self.y_{}))'.format(i,i,i,i))

        # ax = self.fig.add_subplot(111)
        # plt.ylim((0, 10))

        # ax.plot(self.x_t, self.y_0, color=randomcolor(), linewidth=2)

        plt.show()

    def plot_results_before(self, mode, y_lim):
        # 绘制图像
        for i in range(len(self.section_list)):
            exec("ax = self.fig.add_subplot(61{})".format(i + 1))
            exec("plt.title(r'$section{}$', fontsize=10)".format(i))
            if(mode == 1):
                plt.ylim((0, y_lim))
            # plt.title(r'$section{}$', fontsize=10)

            exec(
                "ax.plot(self.x_t, self.y_{}_before, color=randomcolor(), linewidth=2)".format(i))

        plt.show()

    def func_order_move(self, order_move):
        print('order move not null')
        for i in reversed(range(int(len(order_move)))):
            if(len(section_list[order_move[i].order_section_list[0].num].section_order_list)<6):
                section_list[order_move[i].order_section_list[0].num].add_to_section_OrderSku_list(
                    order_move[i])  # 1.6在下一个分区新增订单sku
                order_move.pop(i)
            else:
                print("%s"%order_move[i].name,'不能移动，因为下一个section堵塞')
                continue


    def func_basic_inf(self):
        num_section_sku=[]
        num_section_order=[]

        # 统计section中安排存放了多少个sku
        print('统计section中安排存放了多少个sku：')
        for section in self.section_list:
            section_sku_num = 0
            for sku in self.sku_list:
                if (len(sku.sku_location_list)!=0):
                    if (sku.sku_location_list[0].name ==section.name):
                        section_sku_num=section_sku_num+1
            num_section_sku.append(section_sku_num)
            # print("%s"%section.name,":%d"%section_sku_num)

        table_sku = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
        row_skuu = ['sku个数', '', '', '', '', '', '']
        for j in range(0, 6):
            row_skuu[j + 1] = num_section_sku[j]
        table_sku.add_row(row_skuu)
        print(table_sku)

        # section中安排了多少个order作为todo
        print('统计section中安排了多少个order作为todo：')
        for section in self.section_list:
            section_order_num = 0
            for order in self.order_notstart:
                for order_section in order.order_section_list:
                    if (order_section.name==section.name):
                        section_order_num=section_order_num+1
            num_section_order.append(section_order_num)
            # print('%s'%section.name,":%d"%section_order_num)

        table_order = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
        row_order = ['order个数', '', '', '', '', '', '']
        for j in range(0, 6):
            row_order[j + 1] = num_section_order[j]
        table_order.add_row(row_order)
        print(table_order)

        # 统计order在每个section中要停留的时间，存在section的列表中
        for section in self.section_list:
            for order in self.order_notstart:
                section_waiting_order_num = 0
                # print(order.name)
                for order_section in order.order_section_list:
                    if (order_section.name==section.name):
                        # print(order_section.name)
                        section_waiting_order_num = section_waiting_order_num+1
                section.section_waiting_order.append(section_waiting_order_num)

            print('-------------')
            print("%s"%section.name,":最久订单号:order_%d"%section.section_waiting_order.index(max(section.section_waiting_order)),"处理时长为:%d"%max(section.section_waiting_order))
        print('\n')
        # print(',,,,,,,,,,,,')
        # print(len(order_notstart[5175].order_section_list))
        # print(section_list[0].section_waiting_order[5175])
        # print(section_list[1].section_waiting_order[5175])
        # print(section_list[2].section_waiting_order[5175])
        # print(section_list[3].section_waiting_order[5175])
        # print(section_list[4].section_waiting_order[5175])
        # print(section_list[5].section_waiting_order[5175])

        # print(order_notstart[4631].order_section_list)
            # print(section.section_waiting_order)

    def run(self, keyy,order_pace):
        order_move=[]
        for t in range(self.T):
            print(
                "\n--------------------------\n     当前时刻为%d\n--------------------------" %
                t)
            # 1）下发notstart的订单
            # 按照一定规律计算订单发出的cost，选择cost最少的订单作为order_now
            # 把order_now的sku信息加到第一个section中的section_order_list中
            # 判断如果section的section_order_list_simple>=6则该步不派发order
            if(t%order_pace==0):
                try:
                    # 考虑cost的算法
                    # if(keyy == 'with_algorithm'):
                    #     Func_order_notstart(
                    #         t=t,
                    #         section_list=self.section_list,
                    #         order_notstart=self.order_notstart,
                    #         order_ing=self.order_ing,
                    #         keyy='with_algorithm',
                    #         order_start=self.order_start)
                    # 不考虑cost的算法
                    if (keyy == 'no_algorithm'):
                        Func_order_notstart(
                            t=t,
                            section_list=self.section_list,
                            order_notstart=self.order_notstart,
                            order_ing=self.order_ing,
                            keyy='no_algorithm',
                            order_start=self.order_start)
                    # 发网+cost算法
                    if (keyy == 'Fa_algorithm'):
                        Func_order_notstart(
                            t=t,
                            section_list=self.section_list,
                            order_notstart=self.order_notstart,
                            order_ing=self.order_ing,
                            keyy='Fa_algorithm',
                            order_start=self.order_start)
                    # 发网的原始算法
                    if (keyy == 'Fa_original_algorithm'):
                        Func_order_notstart(
                            t=t,
                            section_list=self.section_list,
                            order_notstart=self.order_notstart,
                            order_ing=self.order_ing,
                            keyy='Fa_original_algorithm',
                            order_start=self.order_start)

                    if (keyy == 'Fa_pace_change'):
                        Func_order_notstart(
                            t=t,
                            section_list=self.section_list,
                            order_notstart=self.order_notstart,
                            order_ing=self.order_ing,
                            keyy='Fa_pace_change',
                            order_start=self.order_start)

                except BaseException:
                    print('*********order派发结束*********\n')


            # 统计派发完成后的section中的section_sku_list，记录y轴数据
            for i in range(len(self.section_list)):
                exec(
                    "self.y_{}_before.append(len(section_list[{}].section_sku_list))".format(
                        i, i))

            # 【展示】
            Func_display_section_sku_list_all(self.section_list)
            print('#########order移动##########')
            table_task = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
            row_task = ['task', '', '', '', '', '', '']

            # 建立move订单队列
            # order_move = []

            # 2）依次完成每个section中的任务
            # 判断：无任务 - 跳过，有任务 - 继续操作
            for i in range(num_section):
                section_now = self.section_list[i]
                if (len(section_now.section_sku_list) == 0):
                    # print('【【【【%s】】】】无任务' % section_now.name)
                    row_task[i + 1] = 0
                else:
                    # print("【【【【%s】】】】有任务 *"%section_now.name)
                    order_now = section_now.section_sku_list[0]
                    sku_now = section_now.section_sku_list[0].order_sku_list[0]
                    # 【展示】
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

                    # 分类讨论：根据当前完成order的任务的性质进行讨论
                    # 任务性质包括：Order_section_list中元素的个数，Order_section_list中最近的两个section是否相同
                    # 1：如果当前Order_section_list只剩下一个，即Order在所有section中都只剩下这一个任务，则调整order到Order_finish的队列中
                    if (len(order_now.order_section_list) == 1):
                        print("$$$%s进入最后一个周期" % order_now.name)
                        order_now.refresh_order_time(section_now)  # 更新订单时间信息
                        # 在分区sku等待队列中删除派发sku的信息
                        self.section_list[order_now.order_section_list[0].num].del_section_Sku_list(
                        )
                        # 在分区sku等待队列中删除派发订单的信息
                        self.section_list[order_now.order_section_list[0].num].del_section_Order_list(
                        )

                        # 删除order的section和sku记录
                        order_now.del_order_SectionSku_list()

                        # 更新order信息
                        self.order_ing.remove(order_now)
                        self.order_finish.append(order_now)

                    # 2：如果当前订单的下一个sku的section与当前操作相同，则不需要进行移动
                    elif ((order_now.order_section_list[1] == order_now.order_section_list[0])):
                        print('下一个section与当前相同，不需要移动')
                        order_now.refresh_order_time_2(section_now)
                        # 在分区sku等待队列中删除派发sku的信息
                        self.section_list[order_now.order_section_list[0].num].del_section_Sku_list(
                        )

                        # 删除order的section和sku记录
                        order_now.del_order_SectionSku_list()

                    # 3：如果当前订单的下个sku的section与当前操作不同，则需要将订单信息移动到下一个section中
                    elif ((order_now.order_section_list[1] != order_now.order_section_list[0])):
                        print(
                            "$$$%s在当前section只剩1个sku，将在下一时间转移到下一个section" %
                            order_now.name)
                        order_now.refresh_order_time_2(section_now)
                        # 在分区sku等待队列中删除派发sku的信息
                        self.section_list[order_now.order_section_list[0].num].del_section_Sku_list(
                        )
                        # 在分区sku等待队列中删除派发订单的信息
                        self.section_list[order_now.order_section_list[0].num].del_section_Order_list(
                        )

                        # 删除order的section和sku记录
                        order_now.del_order_SectionSku_list()

                        # 记录待移动的订单，在遍历所有section后进行移动，防止同一时间订单在多个section完成
                        order_move.append(order_now)
                    else:
                        print("特别情况，for no reason")

                    # 1.4显示每个分区的订单\sku排序、订单信息
                    # print('【order完成后】')
                    # Func_display_section_sku_list_all(self.section_list)
                    # Func_display_order(
                    #     order_notstart=self.order_notstart,
                    #     order_ing=self.order_ing,
                    #     order_finish=self.order_finish,
                    #     order_start=self.order_start)

            #         row_task[i + 1] = 1
            #         row_task[i + 1] = len(section_now.section_sku_list)
            #
            # table_task.add_row(row_task)
            # print(table_task)
            # print('\n')

            # 3）进行order的移动
            if (len(order_move) != 0):
                self.func_order_move(order_move)

            for i in range(num_section):
                section_now = self.section_list[i]
                row_task[i + 1] = 1
                row_task[i + 1] = len(section_now.section_sku_list)
            table_task.add_row(row_task)
            print('各section剩余task数量')
            print(table_task)
            print('\n')

            print('各section剩余order数量')
            table_task_2 = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
            row_task_2 = ['order', '', '', '', '', '', '']
            for i in range(num_section):
                section_now = self.section_list[i]
                row_task_2[i + 1] = 1
                row_task_2[i + 1] = len(section_now.section_order_list)
            table_task_2.add_row(row_task_2)
            print(table_task_2)
            print('\n')

            # 【展示】
            # print('【order move完成后】')
            # Func_display_section_sku_list_all(self.section_list)
            print('\nt=%d时刻order状态：' % t)
            Func_display_order(
                order_notstart=self.order_notstart,
                order_ing=self.order_ing,
                order_finish=self.order_finish,
                order_start=self.order_start)

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
        # # 2：逐个对每个section进行遍历，依次完成当前section中的任务
        # for section in self.section_list:
        #     # 2.1：如果section
        #     section.process_order()  # 实现分区内订单的处理（更新时间）以及移动的过程
        #     if first_section_id == section.num:
        #         section.section_order_list.append(new_order)
        return


if __name__ == "__main__":
    start = tm.perf_counter()

    cwd = os.getcwd()  # 读取当前文件夹路径

    # 1、初始化section
    num_section = 6
    section_list = []
    # 2、初始化sku
    sku_list = []
    sku_time_list = []

    # 3、初始化订单
    order_notstart = []  # 未发出的order
    order_finish = []  # 已经流转结束的order
    order_ing = []  # 正在流转过程中的order
    order_start = []  # 表示订单派发顺序的列表

    simulation_config = {
        'T': 1900000,  # 仿真时长
        # 初始数据
        # 'path_sku_section_map': cwd + '/input/SkuSectionMap_0922.csv',
        # 'path_order_sku_map': cwd + '/input/OrderSkuMap_0924.csv',
        # 'path_sku_time_map': cwd + '/input/SkuTimeMap_0922.csv',

        # # ONum3432_SNum444
        # 'path_sku_section_map': cwd + '/datas/ONum3432_SNum444/SkuSectionMap_ONum3432_SNum444_930_heuristic.csv',
        # 'path_order_sku_map': cwd + '/datas/ONum3432_SNum444/OrderSKUMap_ONum3432_SNum444_930_heuristic.csv',
        # 'path_sku_time_map': cwd + '//datas/ONum3432_SNum444/SkuTimeMap_SNum444_930_heuristic.csv',

        # ONum5610_SNum399
        # 'path_sku_section_map': cwd + '/datas/ONum5610_SNum399/SkuSectionMap_ONum5610_SNum399_930_heuristic.csv',
        # 'path_order_sku_map': cwd + '/datas/ONum5610_SNum399/OrderSKUMap_ONum5610_SNum399_930_heuristic.csv',
        # 'path_sku_time_map': cwd + '//datas/ONum5610_SNum399/SkuTimeMap_SNum399_930_heuristic.csv',

        # ONum5610_SNum399_1
        # 'path_sku_section_map': cwd + '/datas/ONum5610_SNum399/SkuSectionMap_ONum5610_SNum399_930_heuristic.csv',
        # 'path_order_sku_map': cwd + '/datas/ONum5610_SNum399/OrderSKUMap_ONum5610_SNum399_930_heuristic_test.csv',
        # 'path_sku_time_map': cwd + '//datas/ONum5610_SNum399/SkuTimeMap_SNum399_930_heuristic.csv',

        # # ONum6544_SNum537
        'path_sku_section_map': cwd + '/datas/ONum6544_SNum537/SkuSectionMap_ONum6544_SNum537_930_heuristic.csv',
        'path_order_sku_map': cwd + '/datas/ONum6544_SNum537/OrderSKUMap_ONum6544_SNum537_930_heuristic.csv',
        'path_sku_time_map': cwd + '//datas/ONum6544_SNum537/SkuTimeMap_SNum537_930_heuristic.csv',

        'num_section': num_section,

        'order_notstart': order_notstart,
        'order_finish': order_finish,
        'order_ing': order_ing,
        'order_start': order_start,

        'section_list': section_list,
        'sku_list': sku_list,
        'sku_time_list': sku_time_list

    }
    simulation_1 = Simulation(simulation_config)
    simulation_1.func_basic_inf()

    simulation_1.run(keyy='Fa_algorithm',order_pace=1)
    # simulation_1.run(keyy='Fa_pace_change',order_pace=1)

    # simulation_1.run(keyy='Fa_original_algorithm',order_pace=1)
    # simulation_1.run(keyy='no_algorithm',order_pace=2)
    # simulation_1.run(keyy='with_algorithm',order_pace=1)


    end = tm.perf_counter()
    print("程序共计用时 : %s Seconds " % (end - start))


    # # 绘制图像
    # simulation_1.plot_results(mode='0', y_lim=100000)
    # simulation_1.plot_results_before(mode='0', y_lim=100000)

    simulation_1.plot_results(mode='1',y_lim=100000)
