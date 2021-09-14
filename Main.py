# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.08.20
"""

import operator
from Class import Sku,Section,Order,Cost_list
from order_list import *
from section_list import *
#添加一行注释

def Func_display_section_sku_list_all():
    print("所有section订单sku信息：")
    for j in range(1, 7):
        exec("print('   section_{}:%s'%section_{}.section_sku_name_list)".format(j, j))
    print('\n')

def Func_display_section_order_list_all():
    print("所有section订单信息：")
    for j in range(1, 7):
        exec("print('section_{}:%s'%section_{}.section_order_list)".format(j, j))
    print('\n')

def Func_display_section_sku_list(section_now):
    print("【%s"%section_now.name,"】的剩余sku队列section_sku_list(%d)"%len(section_now.section_sku_list),end=': ')
    for j in range(len(section_now.section_sku_list)):
        print(section_now.section_sku_list[j].name,end=',')
    print('\n')

def Func_display_section_order_list(section_now):
    print("【%s"%section_now.name,"】的剩余订单队列section_order_list(%d)"%len(section_now.section_order_list),end=': ')
    for j in range(len(section_now.section_order_list)):
        print(section_now.section_order_list[j].name,end=',')
    print('\n')

def Func_display_order_section_list(order_now):
    print("【%s"%order_now.name,"】的剩余分区集合order_section_list(%d)"%len(order_now.order_section_list),end=': ')
    for j in range(len(order_now.order_section_list)):
        print(order_now.order_section_list[j].name,end=',')
    print('\n')

def Func_display_order():
    print('   *order_notstart(%d): '%len(order_notstart),end='')
    for i in range(len(order_notstart)):
        print("%s"%order_notstart[i].name,end=',')
    print('\n   *order_ing(%d): '%len(order_ing),end='')
    for j in range(len(order_ing)):
        print("%s"%order_ing[j].name,end=',')
    print('\n   *order_finish(%d): '%len(order_finish),end='')
    for j in range(len(order_finish)):
        print("%s"%order_finish[j].name,end=',')
    print('\n')




# 成本排序函数：
def Func_Cost_sequence(order):
    # 成本排序队列构建
    cost = []
    for i in range(len(order)):
        order[i].make_section_list()    # 根据SKU制作分区访问序列
        order[i].make_section_list_simple() #制作经停section的list
        order[i].cal_time_cost()        # 计算所有order的等待成本
        cost.append(Cost_list(order[i].name,0,order[i].order_time_cost,i))
    #对成本以cost为键进行排序
    sortkey=operator.attrgetter('cost')
    cost.sort(key=sortkey)

    # 【可视化：展示订单发出排序和所用cost】
    for i in range(len(cost)):
        cost[i].order=i
        # print("第 %d"%cost[i].order,"发出的订单为 %s"%cost[i].name,"，其cost为：%.1f"%cost[i].cost)

    return cost,order[cost[0].orderfororder]


def Func_order_notstart(order_notstart,order_ing):
    #######################################if order_notstart
    # 1 order_notstart：对未发出的order进行cost计算，决策应该先派出哪单
    # 1.1对派发order计算cost并进行排序
    print('*********order发出*********')
    print("待派发的orders各自的cost:")
    cost, order_now = Func_Cost_sequence(order_notstart)  # order_now是选出来将要进行派发的单子
    section_now = order_now.order_section_list[0]  # section_now是将要进行派发的section
    sku_now = order_now.order_sku_list[0]  # sku_now是将要进行派发的sku

    print("【当前派发的订单为：%s" % order_now.name, "sku为：%s" % sku_now.name, ",其cost=%.1f】" % cost[0].cost,",分区(第一站)为：%s" % section_now.name)
    Func_display_order_section_list(order_now)


    # 1.2改变order的当前分区current_section
    order_now.current_section.append(section_now.name)

    # 1.3更新order时间
    # 进入section时间：对于第一次派发=当前时间
    order_now.time['enter_section'] = t  # 进入分区的时间是t，但不一定进入之后立即加工
    # 在该section的实际操作时间（仅本订单）
    key = 1
    for i in range(1, len(order_now.order_section_list)):
        if (order_now.order_section_list[i] != order_now.order_section_list[0]):
            break
        else:
            key = key + 1
    order_now.time['section_processing_time_list'] = key
    # 在该section的等待时间
    order_now.time['waiting_time'] = len(section_now.section_sku_list)
    # print("waiting time=%s" % order_now.time['waiting_time'])


    # 1.4在分区等待队列中增加派发订单的信息(如order_1在section_1有3个sku要做，那就加3个order_1)
    # sku队列加多个order
    for k in range(len(order_now.order_sku_list)):
        exec("{}.section_sku_list.append(order_now)".format(order_now.order_section_list[0].name))
        exec("{}.section_sku_name_list.append(order_now.name)".format(order_now.order_section_list[0].name))
        try:
            if (order_now.order_sku_list[k + 1].sku_location == order_now.order_sku_list[k].sku_location):
                continue
            else:
                break

        except:
            break
    # 在section的等待队列中只加order名称
    exec("{}.section_order_list.append(order_now)".format(order_now.order_section_list[0].name))

    # 1.5显示每个分区的订单\sku排序
    print('【新order派发后】')

    # 1.6更新order信息,由order_notstart到正在进行order_ing,在订单排队、成本队列中踢出
    order_ing.append(order_now)
    order_notstart.pop(cost[0].orderfororder)
    cost.pop(0)





#######################################################################################################################
if __name__ == "__main__":
#1\初始化6个分区信息：分区名称、正在等待的订单数量、处理订单列表
    num_section=6
    section_list=[]
    for i in range(1,(num_section+1)):
        section_input = {'name': 'section_{}'.format(i),
                         'section_order_num': 0,
                         'section_order_list': [],
                         'section_sku_list': [],
                         'section_sku_name_list': []
                        }

        section_list.append(Section(section_input))

    section_config={'name':'',
                    'section_order_num':'',
                    'section_order_list':[],
                    'section_sku_list': []
                    }
    section_1=Section(section_1_config)
    section_2=Section(section_2_config)
    section_3=Section(section_3_config)
    section_4=Section(section_4_config)
    section_5=Section(section_5_config)
    section_6=Section(section_6_config)


# section_1.section_order_list.extend(['1','3','6'])
    # print(section_1.__dict__)  # 查询每个实例的属性

#2\初始化sku所在的分区：sku名称，sku处理所需时间、sku所在分区
    #同一分区中的不同sku
    num_sku=6
    sku_list=[]
    sku_selection_map=[] #read data from SkuSectionMap
    sku_time=1
    for i in range(1,(num_sku+1)):
        sku_input={'name':'sku_{}'.format(i),
                   'sku_time':sku_time,
                   'sku_location':'' #后续考虑在表中读取sku的section信息
                   }
        sku_list.append(Sku(sku_input))
    sku_1=Sku(sku_1_config)
    sku_11=Sku(sku_11_config)
    sku_111=Sku(sku_111_config)
    #不同分区的sku
    sku_2=Sku(sku_2_config)
    sku_3=Sku(sku_3_config)
    sku_4=Sku(sku_4_config)
    sku_5=Sku(sku_5_config)
    sku_6=Sku(sku_6_config)

    # print("sku_1.location:%s"%sku_1.sku_location.name)
    # print("sku_1.time:%d"%sku_1.sku_time)
    # print(sku_111.__dict__)

#3\初始化订单：订单等候cost、订单中的sku信息、订单的分区经停顺序，计算总等待cost
    #订单构建

    time={'enter_section': '',  # 进入分区时间
          'leave_section': '',  # 离开分区时间
          'start_processing': '',  # 开始加工时间
          'section_processing_time_list': [],  # 每个订单在所需经过的分区所需要分拣的时间
          'waiting_time': '',  # 在某个分区所需等待的时间
          }

    order_config={'name':'',
                  'order_time_cost':'',
                  'order_sku_list':'',
                  'order_section_list':'',
                  'current_section':'',
                  'time':''
                  }

    order_notstart=[]   #未发出的order
    order_finish=[]     #已经流转结束的order
    order_ing=[]        #正在流转过程中的order

    #记录订单信息到未发出的order中
    order_notstart.extend([Order(order_1_con),
                           Order(order_2_con),
                           Order(order_3_con),
                           Order(order_4_con),
                           Order(order_5_con),
                           Order(order_6_con),
                           Order(order_7_con)
                           ])


    cost=[]


    #T为需要计算的时间
    T=10
    for t in range(1,T):

        print("\n")
        print("--------------------------\n     当前时刻为%d\n--------------------------" % t)
        try:
            Func_order_notstart(order_notstart=order_notstart, order_ing=order_ing)
        except:
            print('*********order派发结束*********\n')

        Func_display_section_sku_list_all()


        print('#########order移动##########')
        order_move = []
        for i in range(1,7):
            exec("section_now=section_{}".format(i))
            if (len(section_now.section_sku_list) == 0):
                print('【【【【%s】】】】无任务' % section_now.name)
            else:

                print("【【【【%s】】】】有任务*"%section_now.name)

                print('【order移动前】')
                # Func_display_section_sku_list_all()
                # Func_display_section_sku_list(section_now)

                order_now=section_now.section_sku_list[0]
                sku_now=section_now.section_sku_list[0].order_sku_list[0]
                print('要完成的order为：%s'%order_now.name,',sku为%s'%sku_now.name)
                # Func_display_order_section_list(order_now)
                # Func_display_section_sku_list(section_now)

                #如果order_section_list只剩下一个，则调整order至order finish
                if (len(order_now.order_section_list) == 1):
                    print("$$$%s进入最后一个周期"%order_now.name)
                    #1。1更新订单时间信息
                    order_now.current_section.append(section_now.name)
                    order_now.time['section_processing_time_list'] = 1
                    order_now.time['waiting_time'] = len(section_now.section_sku_list) - 1

                    #1.2 在分区sku等待队列中删除派发sku的信息
                    exec("{}.section_sku_list.pop(0)".format(order_now.order_section_list[0].name))
                    exec("{}.section_sku_name_list.pop(0)".format(order_now.order_section_list[0].name))
                    #1.3 在分区订单等待队列删除派发的一个订单名称
                    Func_display_section_order_list(section_now)
                    exec("{}.section_order_list.pop(0)".format(order_now.order_section_list[0].name))


                    #1.4 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)
                    #1.5更新order信息
                    order_ing.remove(order_now)
                    order_finish.append(order_now)

                #如果order_section_list还剩下多个，并且下一个section与当前相同，则不需要移动

                elif ((order_now.order_section_list[1] == order_now.order_section_list[0])):
                    # 1.1更新order的当前分区current_section
                    order_now.current_section.append(section_now.name)
                    # 1.2更新order的时间
                    # 在该section的实际操作时间（仅本订单）
                    key = 1
                    for i in range(1, len(order_now.order_section_list)):
                        if (order_now.order_section_list[i] != order_now.order_section_list[0]):
                            break
                        else:
                            key = key + 1
                    order_now.time['section_processing_time_list'] = key
                    # 在该section的等待时间
                    order_now.time['waiting_time'] = len(section_now.section_sku_list) - 1
                    # print("【%s" % order_now.name, "移动】waiting time=%s" % order_now.time['waiting_time'])

                    # 1.2 在分区等待队列中删除派发订单的信息
                    exec("{}.section_sku_list.pop(0)".format(order_now.order_section_list[0].name))
                    exec("{}.section_sku_name_list.pop(0)".format(order_now.order_section_list[0].name))


                    # 1.4 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)

                # 如果order_section_list还剩下多个，下一个section与当前不同，则将订单信息加到下一个section中
                elif ((order_now.order_section_list[1] != order_now.order_section_list[0])):
                    print("$$$%s在当前section只剩1个sku，将在下一时间转移到下一个section"%order_now.name)

                    # 1.1更新order的当前分区current_section
                    order_now.current_section.append(section_now.name)
                    # 1.2更新order的时间
                    # 在该section的实际操作时间（仅本订单）
                    key = 1
                    for i in range(1, len(order_now.order_section_list)):
                        if (order_now.order_section_list[i] != order_now.order_section_list[0]):
                            break
                        else:
                            key = key + 1
                    order_now.time['section_processing_time_list'] = key
                    # 在该section的等待时间
                    order_now.time['waiting_time'] = len(section_now.section_sku_list) - 1
                    # print("【%s" % order_now.name, "移动】waiting time=%s" % order_now.time['waiting_time'])


                    # 1.3 在分区等待队列中删除派发订单的信息
                    exec("{}.section_sku_list.pop(0)".format(order_now.order_section_list[0].name))
                    exec("{}.section_sku_name_list.pop(0)".format(order_now.order_section_list[0].name))
                    # Func_display_section_order_list(section_now)

                    # 1.4 在分区订单等待队列删除派发的一个订单名称
                    exec("{}.section_order_list.pop(0)".format(order_now.order_section_list[0].name))

                    # 1.5 删除order的section和sku记录
                    order_now.order_section_list.pop(0)
                    order_now.order_sku_list.pop(0)

                    #记录待移动的订单，在遍历所有section后进行移动，防止同一时间订单在多个section完成
                    order_move.append(order_now)

                # 1.4显示每个分区的订单\sku排序、订单信息
                print('【order完成后】')
                Func_display_section_sku_list_all()
                # print('****************')
                # Func_display_order()

                # print("\n【删除结束后】当前操作%s的:order_section_list" % order_now.name)
                # Func_display_order_section_list(order_now)
                #
                # print("\n【删除结束后】当前操作分区%s的:section_order_list" % section_now.name)
                # Func_display_section_sku_list(section_now)

        #section遍历结束后进行order移动
        if (len(order_move) != 0):
            # print('order move not null')
            for i in range(len(order_move)):
                # 1.6在下一个分区新增订单sku
                # 1.6在分区等待队列中增加派发订单的信息(如order_1在section_1有3个sku要做，那就加3个order_1)
                # sku队列加多个order
                # 在section的等待队列中只加order名称
                exec("{}.section_order_list.append(order_move[i])".format(order_move[i].order_section_list[0].name))

                for k in range(len(order_move[i].order_sku_list)):
                    exec("{}.section_sku_list.append(order_move[i])".format(order_move[i].order_section_list[0].name))
                    exec("{}.section_sku_name_list.append(order_move[i].name)".format(
                        order_move[i].order_section_list[0].name))
                    try:
                        if (order_move[i].order_sku_list[k + 1].sku_location == order_move[i].order_sku_list[
                            k].sku_location):
                            continue
                        else:
                            break
                    except:
                        break

        print('\nt=%d时刻order状态：'%t)
        Func_display_order()
