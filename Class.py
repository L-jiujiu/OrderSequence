# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.08.20
"""
import pandas as pd
import time as tm
import os
import numpy as np
import matplotlib.pyplot as plt

from prettytable import PrettyTable
from prettytable import from_csv


class Sku:
    def __init__(self, sku_config):
        self.name = sku_config['name']  # sku名称
        self.num=sku_config['num']      # sku序号
        self.sku_time = sku_config['sku_time']  # sku处理所需时间
        self.sku_location_list = sku_config['sku_location_list']  # sku所在分区信息


class Section:
    def __init__(self, section_config):
        self.name = section_config['name']  # 分区名称
        self.num=section_config['num']      # 分区序号
        self.section_order_num = section_config['section_order_num']  # 等待订单数量
        self.section_order_list = section_config['section_order_list']  # 处理订单列表,只有1个order1,对于同一个订单在此地有多个货物要拣选的只录入一条
        self.section_sku_list = section_config['section_sku_list']  # 处理sku信息，可以有多个order1
        self.section_sku_name_list = section_config['section_sku_name_list']  # 处理sku信息的名称(不是实例)，可以有多个order1

    def add_to_section_OrderSku_list(self,order_now):
        self.section_order_list.append(order_now)
        for i in range(len(order_now.order_sku_list)):
            self.section_sku_list.append(order_now)
            self.section_sku_name_list.append(order_now.name)
            try:
                if(order_now.order_sku_list[i + 1].sku_location_list[0].name ==
                    order_now.order_sku_list[i].sku_location_list[0].name):
                    continue
                else:
                    break
            except BaseException:
                break

    # 在分区sku等待队列中删除派发sku的信息
    def del_section_Sku_list(self):
        self.section_sku_list.pop(0)
        self.section_sku_name_list.pop(0)

    def del_section_Order_list(self):
        self.section_order_list.pop(0)


    def display_section_OrderSku_list(self):
        print('当前section的order排列：display_section_order_list:')
        for section_order in self.section_order_list:
            print(section_order.name)
        print('当前section的考虑sku的order排列：display_section_sku_list:')
        for section_sku in self.section_sku_list:
            print(section_sku.name)





class Order:
    def __init__(self, order_config):
        self.name = order_config['name']  # 订单名称
        self.num=order_config['num']      # 分区序号
        self.order_time_cost = order_config['order_time_cost']  # 订单等候cost
        self.order_sku_list = order_config['order_sku_list']  # 订单中的sku信息
        self.order_section_list = order_config['order_section_list']  # 剩余分区集合，表示当前分区结束后要去的分区（按顺序从0,1,...）；
        # 若为空集，表示订单在完成当前分区分拣后，就完成了全部分拣作业
        self.order_section_list_simple = order_config['order_section_list_simple']  # 简单的分区经过信息，不同sku在同一分区只记录一次
        # 新增状态
        self.current_section = order_config['current_section']  # 当前所在分区：若非空，则表示已经在分区中等待或分拣
        # 时间
        self.time = order_config['time']

        self.path_order_sku_map=order_config['path_order_sku_map']

    # 更新订单时间
    def refresh_order_time(self,section_now):
        # 1。1更新订单时间信息
        self.current_section.append(section_now.name)
        self.time['section_processing_time_list'] = 1
        self.time['waiting_time'] = len(section_now.section_sku_list) - 1

    def refresh_order_time_2(self, section_now):
        self.current_section.append(section_now.name)
        # 1.2更新order的时间
        # 在该section的实际操作时间（仅本订单）
        key = 1
        for i in range(1, len(self.order_section_list)):
            if (self.order_section_list[i]!= self.order_section_list[0]):
                break
            else:
                key = key + 1
        self.time['section_processing_time_list'] = key
        # 在该section的等待时间
        self.time['waiting_time'] = len(section_now.section_sku_list) - 1
        # print("【%s" % order_now.name, "移动】waiting time=%s" % order_now.time['waiting_time'])




    def del_order_SectionSku_list(self):
        self.order_section_list.pop(0)
        self.order_sku_list.pop(0)

    # 根据SKU制作分区访问序列
    def make_section_list(self):
        # print("%s经停分区："%self.name)
        self.order_section_list = []
        order_section_list_name = []  # 初始化订单分区经停顺序


        for i in range(len(self.order_sku_list)):
            sku_add_time = int(self.order_sku_list[i].sku_time)
            for add in range(sku_add_time):
                self.order_section_list.append(self.order_sku_list[i].sku_location_list[0])
            # 【可视化：不同分区等待的订单数，注意：如果是不同sku在相同分区，则等待订单数需要+1】
                order_section_list_name.append(self.order_sku_list[i].sku_location_list[0].name)
            # print('%s'%order_section_list_name[i],"中正在等待的订单数%d"%self.order_sku_list[i].sku_location.section_order_num)

    # def make_order_sectionsku_list(self):
    #     data = np.genfromtxt(self.path_order_sku_map, delimiter=",")  # 打开Excel文件
    #
    #     # #表格展示
    #     # table_OrderSku = PrettyTable()
    #     # fp = open(self.path_order_sku_map, "r")
    #     # table_OrderSku = from_csv(fp)
    #     # print(table_OrderSku)
    #     # fp.close()
    #





    def make_section_list_simple(self):
        self.order_section_list_simple = []
        order_section_list_simple_name = []
        for i in range(len(self.order_sku_list)):
            if(i == 0):
                self.order_section_list_simple.append(self.order_sku_list[i].sku_location_list[0])  # 记录第一个sku的section信息
                order_section_list_simple_name.append(self.order_sku_list[i].sku_location_list[0].name)
            else:
                if(self.order_sku_list[i].sku_location_list[0] != self.order_sku_list[i - 1].sku_location_list[0]):
                    self.order_section_list_simple.append(self.order_sku_list[i].sku_location_list[0])  # 如果与前面的section不同，则做新的纪录，不记录重复的section信息
                    order_section_list_simple_name.append(self.order_sku_list[i].sku_location_list[0].name)
        # print("订单经停的section有：%s"%order_section_list_simple_name)

    # 计算由权重和等待order计算cost进行派件排序

    def cal_time_cost(self):
        self.order_time_cost = 0
        i = 0
        for i in range(4):
            # 输入权重（1，0.5，0.3）
            weight = 1
            if (i == 1):
                weight = 0.5
            if (i == 2):
                weight = 0.3
            if (i == 3):
                weight = 0.2

            try:
                # cost为权重*分区等待数的和
                if(self.order_section_list[i] is not None):
                    waiting = len(self.order_section_list[i].section_sku_list)
                    # waiting = len(self.order_section_list[i].section_order_list)
                    self.order_time_cost = self.order_time_cost + waiting * weight
                    waiting = 0
            except BaseException:
                break
        # print("%s" % self.name, "的cost为：%.2f" % self.order_time_cost)
    # print("\n")

# 用于将排序后的cost和订单order对应

class Sku:
    def __init__(self, sku_config):
        self.name = sku_config['name']  # sku名称
        self.num=sku_config['num']      # sku序号
        self.sku_time = sku_config['sku_time']  # sku处理所需时间
        self.sku_location_list = sku_config['sku_location_list']  # sku所在分区信息


class CostList:
    def __init__(self, cost_config):
        self.name = cost_config['name']
        self.order = cost_config['order']  # 指排序后的顺序，按增序排列
        self.cost = cost_config['cost']
        self.orderfororder = cost_config['orderfororder']  # 用于删除Order序列中已被分配的订单，记录了原始Order的顺序


class OrderTime:
    def __init__(self, time):
        self.time = time
        if (time['start_processing'] != '') & (time['enter_section'] != ''):
            time['waiting'] = time['start_processing'] - time['enter_section']
