# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.09.27
"""
import random
import operator
import numpy as np
import pandas as pd


from prettytable import PrettyTable
from prettytable import from_csv
from Class import Sku, Section, Order, CostList

# 成本排序函数：


def Func_Cost_sequence(order, CostList,section_list):
    # 成本排序队列构建
    cost = []
    for i in range(len(order)):
        order[i].cal_time_cost(section_list)            # 计算所有order的等待成本

        cost_input = {
            'name': order[i].name,  # 分区名称
            'order': 0,  # 分区序号
            'cost': order[i].order_time_cost,  # 等待订单的数量，初始为0
            'orderfororder': i,  # 处理订单的列表，不重复
        }
        cost.append(CostList(cost_input))

    # 对成本以cost为键进行排序
    sortkey = operator.attrgetter('cost')
    cost.sort(key=sortkey)

    # 【可视化：展示订单发出排序和所用cost】
    for i in range(len(cost)):
        cost[i].order = i
        # print("第 %d"%cost[i].order,"发出的订单为 %s"%cost[i].name,"，其cost为：%.1f"%cost[i].cost)

    return cost, order[cost[0].orderfororder]


# 派发订单
def Func_order_notstart(
        t,
        section_list,
        order_notstart,
        order_ing,
        keyy,
        order_start):
    # if order_notstart
    # 1 order_notstart：对未发出的order进行cost计算，决策应该先派出哪单

    # 1.1对派发order计算cost并进行排序
    print('*********order发出*********')

    if(keyy == 'with_algorithm'):
        # 有排序算法
        print("待派发的orders各自的cost:")
        cost, order_now = Func_Cost_sequence(
            order_notstart, CostList,section_list)  # order_now是选出来将要进行派发的单子

    elif (keyy == 'no_algorithm'):
        # 无排序算法
        order_now = order_notstart[0]

    elif (keyy == 'Fa_algorithm'):
        notice = 0
        # 发网与cost结合算法
        order_can = [] #存储可以派发的单子序列-可以派发指：等待队列最少的section
        for section in section_list:
            # print(section.name)
            if (len(section.section_order_list) == 0):
                for order in order_notstart:
                    if (len(order.order_section_list) != 0):
                        if (order.order_section_list[0].name == section.name):
                            order_can.append(order)
                        else:
                            continue
            else:
                continue

        cost, order_now = Func_Cost_sequence(order_can, CostList, section_list)
        # print('order_can:')
        # if (len(order_can) != 0):
        #     # for order in order_can:
        #         # print(order.name)
        #     cost, order_now = Func_Cost_sequence(order_can, CostList, section_list)
        #     # order_now=order_can[0]
        # else:
        #     # order_now=order_notstart[0]
        #     notice = 1
        #     print('当前没有section为空')
        #     cost, order_now = Func_Cost_sequence(
        #         order_notstart, CostList,section_list)  # order_now是选出来将要进行派发的单子

    elif (keyy == 'Fa_original_algorithm'):
        order_can = []
        orderfororder_original=[]
        notice_original=0
        for i in range(len(order_notstart)):
            if (len(order_notstart[i].order_section_list) == 1):
                order_can.append(order_notstart[i])
                orderfororder_original.append(i)
        print('有且只有一个单位时间需要处理的订单数量%d' % len(order_can))
        if (len(order_can) > 0):
            order_now = order_can[0]
            notice_original=1
        else:
            order_now = order_notstart[0]



    section_now = order_now.order_section_list[0]  # section_now是将要进行派发的section
    sku_now = order_now.order_sku_list[0]  # sku_now是将要进行派发的sku

    try:
        print(
            "当前派发的订单为：%s" %
            order_now.name,
            ",sku为：%s" %
            sku_now.name,
            ",其cost=%.1f" %
            cost[0].cost,
            ",第一站为：%s" %
            section_now.name,
        )
    except:
        print(
            "当前派发的订单为：%s" %
            order_now.name,
            ",sku为：%s" %
            sku_now.name,
            ",第一站为：%s" %
            section_now.name,
        )
    # 【展示】
    # for i in range(len(order_now.order_sku_list)):
    #     print(order_now.order_sku_list[i].name)
    # Func_display_order_section_list(order_now)
    # Func_display_order_sku_list(order_now)

    # 1.2改变order的当前分区current_section
    order_now.current_section.append(section_now.name)
    # 1.3更新order时间
    # 进入section时间：对于第一次派发=当前时间
    order_now.time['enter_section'] = t  # 进入分区的时间是t，但不一定进入之后立即加工
    # 在该section的实际操作时间（仅本订单）
    key = 1
    for i in range(1, len(order_now.order_section_list)):
        if (order_now.order_section_list[i] !=
                order_now.order_section_list[0]):
            break
        else:
            key = key + 1
    order_now.time['section_processing_time_list'] = key
    # 在该section的等待时间
    order_now.time['waiting_time'] = len(section_now.section_sku_list)
    # print("waiting time=%s" % order_now.time['waiting_time'])

    # 1.4在分区等待队列中增加派发订单的信息(如order_1在section_1有3个sku要做，那就加3个order_1)
    section_list[order_now.order_section_list[0].num].add_to_section_OrderSku_list(
        order_now)

    # 1.5显示每个分区的订单\sku排序
    # print('【新order派发后】')
    # section_list[order_now.order_section_list[0].num].display_section_OrderSku_list()

    # 1.6更新order信息,由order_notstart到正在进行order_ing,在订单排队、成本队列中踢出
    order_start.append(order_now)  # 表示订单的派发顺序
    order_ing.append(order_now)
    if (keyy == 'with_algorithm'):
        order_notstart.pop(cost[0].orderfororder)
        cost.pop(0)
    elif((keyy == 'no_algorithm')):
        order_notstart.pop(0)
    elif((keyy == 'Fa_original_algorithm')):
        if(notice_original==0):
            order_notstart.pop(0)
        elif(notice_original==1):
            order_notstart.pop(orderfororder_original[0])

    elif (keyy == 'Fa_algorithm'):
        if(notice==0):
            for i in range(len(order_notstart)):
                if (order_notstart[i].name==order_now.name):
                    order_notstart.pop(i)
                    break
        elif(notice==1):
            order_notstart.pop(cost[0])
            cost.pop(0)





# 展示
def Func_display_section_sku_list_all(section_list):
    print("所有section订单sku信息：")
    table = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
    row_sku = ['sku', '', '', '', '', '', '']

    for j in range(0, 6):
        row_sku[j + 1] = section_list[j].section_sku_name_list
        # exec("print('   section_{}:%s'%section_list[{}].section_sku_name_list)".format(j, j))
    table.add_row(row_sku)
    print(table)
    print('\n')


def Func_display_section_order_list_all(section_list):
    print("所有section订单信息：")
    table = PrettyTable(['section', '0', '1', '2', '3', '4', '5'])
    row_sku = ['sku', '', '', '', '', '', '']

    for j in range(0, 6):
        row_sku[j + 1] = section_list[j].section_sku_name_list
        # exec("print('   section_{}:%s'%section_list[{}].section_order_list)".format(j, j))
    table.add_row(row_sku)
    print(table)
    print('\n')


def Func_display_section_sku_list(section_now):
    print("【%s" %
          section_now.name, "】的剩余sku队列section_sku_list(%d)" %
          len(section_now.section_sku_list), end=': ')
    for j in range(len(section_now.section_sku_list)):
        print(section_now.section_sku_list[j].name, end=',')
    print('\n')


def Func_display_section_order_list(section_now):
    print("【%s" % section_now.name, "】的剩余订单队列section_order_list(%d)" %
          len(section_now.section_order_list), end=': ')
    for j in range(len(section_now.section_order_list)):
        print(section_now.section_order_list[j].name, end=',')
    print('\n')


def Func_display_order_section_list(order_now):
    print("【%s" %
          order_now.name, "】的剩余分区集合order_section_list(%d)" %
          len(order_now.order_section_list), end=': ')
    for j in range(len(order_now.order_section_list)):
        print(order_now.order_section_list[j].name, end=',')
    print('\n')


def Func_display_order_sku_list(order_now):
    print("【%s" %
          order_now.name, "】的剩余sku集合order_section_list(%d)" %
          len(order_now.order_section_list), end=': ')
    for j in range(len(order_now.order_sku_list)):
        print(order_now.order_sku_list[j].name, end=',')
    print('\n')


def Func_display_order(order_notstart, order_ing, order_finish, order_start):
    print('   *order_notstart(%d): ' % len(order_notstart), end='')
    for i in range(len(order_notstart)):
        print("%s" % order_notstart[i].name, end=',')
    print('\n   *order_ing(%d): ' % len(order_ing), end='')
    for j in range(len(order_ing)):
        print("%s" % order_ing[j].name, end=',')
    print('\n   *order_finish(%d): ' % len(order_finish), end='')
    for j in range(len(order_finish)):
        print("%s" % order_finish[j].name, end=',')
    print('\n   *order_start(%d): ' % len(order_start), end='')
    for j in range(len(order_start)):
        print("%s" % order_start[j].name, end=',')
    print('\n')

# 将csv中的数据按行读取为1的值并记录，如读取sku所在section信息，读取order中所含sku信息
# def Func_ReadCsv_OrderSku(i, num_col):
#     sku_location_num_list = []  # sku的全部所在分区（数字）
#     sku_location_list = []  # sku的全部所在分区（实例）
#     temp = []
#
#     # 读取所有数据，统计为1的列目标是在该分区
#     for z in range(0, num_col):
#         temp.append(data[i + 1, z + 1])
#         if ((temp[z]) != 0):
#             sku_location_num_list.append(z)
#     # 将分区信息记录在sku对应分区的列表中
#     for f in range(len(sku_location_num_list)):
#         sku_location_list.append(sku_list[sku_location_num_list[f]])
#         # print("order_%d" % i, "包含的sku为：%s" % sku_location_list[f].name)
#     return sku_location_list

# [改进，按照section的顺序加入order_sku_list]将csv中的数据按行读取为1的值并记录，如读取sku所在section信息，读取order中所含sku信息


# def Func_ReadCsv_OrderSku_tool_2(
#         order_sku_num_list,
#         order_sku_number_list,
#         order_sku_list,
#         order_section_list,
#         a,
#         sku_list):
#     for f in range(len(order_sku_num_list)):
#         if (order_sku_num_list[f] is not None):
#             if (sku_list[order_sku_num_list[f]
#                          ].sku_location_list[0].name == a):
#                 sku_add_time = int(sku_list[order_sku_num_list[f]].sku_time)
#                 for add in range(sku_add_time):
#                     order_sku_list.append(sku_list[order_sku_num_list[f]])
#                     order_section_list.append(
#                         sku_list[order_sku_num_list[f]].sku_location_list[0])
#                 order_sku_num_list[f] = None


def Func_ReadCsv_OrderSku_tool(
        order_sku_num_list,
        order_sku_number_list,
        order_sku_list,
        order_section_list,
        a,
        sku_list,
        section_time_list,
        ii):
    time=0
    for f in range(len(order_sku_num_list)):
        if (order_sku_num_list[f] is not None):
            # #防止出现sku无section分配到问题
            if (sku_list[order_sku_num_list[f]
                         ].sku_location_list[0].name == a):
                for i in range(int(order_sku_number_list[f])):
                    sku_add_time = int(sku_list[order_sku_num_list[f]].sku_time)
                    for add in range(sku_add_time):
                        order_sku_list.append(sku_list[order_sku_num_list[f]])
                        order_section_list.append(sku_list[order_sku_num_list[f]].sku_location_list[0])
                        time=time+1

                # print(sku_list[order_sku_num_list[f]].name)
                # print(sku_list[order_sku_num_list[f]].sku_location_list[0].name)
                order_sku_num_list[f] = None
    section_time_list[ii]=time


def Func_ReadCsv_OrderSku_improve(i, num_col, data, sku_list, num_section):
    order_sku_num_list = []  # sku的全部所在分区（数字）
    order_sku_number_list = []  # 各sku的个数，0，1甚至是2
    order_sku_list = []  # sku的全部所在分区（实例）
    order_section_list = []  # sku的全部所在分区（实例）
    section_time_list=[0,0,0,0,0,0]
    temp = []

    # 读取所有数据，统计为1的列目标是在该分区
    for z in range(0, num_col):
        temp.append(data[i + 1, z + 1])
        if (((temp[z]) != 0)):
            order_sku_num_list.append(z)
            order_sku_number_list.append(temp[z])

    # 将分区信息记录在sku对应分区的列表中
    for i in range(num_section):
        exec("Func_ReadCsv_OrderSku_tool(order_sku_num_list,order_sku_number_list, order_sku_list,order_section_list, 'section_{}',sku_list,section_time_list,i)".format(i))

    return order_sku_list, order_section_list,section_time_list

# 将csv中的数据按行读取为1的值并记录，如读取sku所在section信息，读取order中所含sku信息


def Func_ReadCsv_SkuSection(i, num_section, data, section_list):
    sku_location_num_list = []  # sku的全部所在分区（数字）
    sku_location_list = []  # sku的全部所在分区（实例）
    temp = []

    # 读取所有数据，统计为1的列目标是在该分区
    for z in range(0, num_section):
        temp.append(data[z + 1, i + 1])
        if (((temp[z]) != 0)):
            sku_location_num_list.append(z)
    # 将分区信息记录在sku对应分区的列表中

    for f in range(len(sku_location_num_list)):
        sku_location_list.append(section_list[sku_location_num_list[f]])
        # print("sku_%d" % i, "所在的分区为：%s" % sku_location_list[f].name)
    return sku_location_list

# 读取sku单个用时


def Func_ReadCsv_SkuTime(path_sku_time_map, num_sku, sku_time_list):
    data = np.genfromtxt(path_sku_time_map,
                         delimiter=",")  # 打开Excel文件
    sku_time_map = pd.read_csv(path_sku_time_map)
    for i in range(0, num_sku):
        sku_time_list.append(data[1, i + 1])
    return sku_time_list

# 随机颜色


def randomcolor():
    colorArr = [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        'A',
        'B',
        'C',
        'D',
        'E',
        'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def get_with_default(dictionary, key, default_value):
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value


if __name__ == "__main__":
    pass
