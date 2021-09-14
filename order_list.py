# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.08.22
"""
from Main import *
from section_list import  *

section_1=Section(section_1_config)
section_2=Section(section_2_config)
section_3=Section(section_3_config)
section_4=Section(section_4_config)
section_5=Section(section_5_config)
section_6=Section(section_6_config)

sku_1=Sku(sku_1_config)
sku_11=Sku(sku_11_config)
sku_111=Sku(sku_111_config)
#不同分区的sku
sku_2=Sku(sku_2_config)
sku_3=Sku(sku_3_config)
sku_4=Sku(sku_4_config)
sku_5=Sku(sku_5_config)
sku_6=Sku(sku_6_config)
sku_55=Sku(sku_5_config)

time={'enter_section': '',  # 进入分区时间
          'leave_section': '',  # 离开分区时间
          'start_processing': '',  # 开始加工时间
          'section_processing_time_list': '',  # 每个订单在所需经过的分区所需要分拣的时间
          'waiting_time': '',  # 在某个分区还需等待的时间
          }

order_1_con={'name':'order_1',
          'order_time_cost':'0',
          'order_sku_list':[sku_1,sku_3,sku_5],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]

}

# print(order_1_con['time'].)

order_2_con={'name':'order_2',
          'order_time_cost':'0',
          'order_sku_list':[sku_1, sku_11, sku_111, sku_4],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }

order_3_con={'name':'order_3',
          'order_time_cost':'0',
          'order_sku_list':[sku_1,sku_5],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }

order_4_con={'name':'order_4',
          'order_time_cost':'0',
          'order_sku_list':[sku_2],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }

order_5_con={'name':'order_5',
          'order_time_cost':'0',
          'order_sku_list':[sku_1,sku_11,sku_4,sku_5],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }

order_6_con={'name':'order_6',
          'order_time_cost':'0',
          'order_sku_list':[sku_3,sku_6],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }
order_7_con={'name':'order_7',
          'order_time_cost':'0',
          'order_sku_list':[sku_5],
          'order_section_list':[],
          'current_section':[],
          'time':time,
          'order_section_list_simple':[]
          }