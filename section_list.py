# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.08.22
"""

from Main import *
from section_list import *


section_1_config={'name':'section_1',
                  'section_order_num':1,
                  'section_order_list':[],
                  'section_sku_list': [],
                  'section_sku_name_list':[]
                  }

section_2_config={'name':'section_2',
                  'section_order_num':2,
                  'section_order_list':[],
                  'section_sku_list': [],
                  'section_sku_name_list':[]

                  }

section_3_config={'name':'section_3',
                  'section_order_num':30,
                  'section_order_list':[],
                  'section_sku_list':[],
                  'section_sku_name_list':[]

                  }

section_4_config={'name':'section_4',
                  'section_order_num':4,
                  'section_order_list':[],
                  'section_sku_list': [],
                  'section_sku_name_list':[]

                  }

section_5_config={'name':'section_5',
                  'section_order_num':0,
                  'section_order_list':[],
                  'section_sku_list':[],
                  'section_sku_name_list':[]
                  }
section_6_config={'name':'section_6',
                  'section_order_num':6,
                  'section_order_list':[],
                  'section_sku_list': [],
                  'section_sku_name_list':[]

                  }

section_1=Section(section_1_config)
section_2=Section(section_2_config)
section_3=Section(section_3_config)
section_4=Section(section_4_config)
section_5=Section(section_5_config)
section_6=Section(section_6_config)


sku_1_config={'name':'sku_1',
              'sku_time':1,
              'sku_location':section_1
              }

sku_11_config={'name':'sku_11',
               'sku_time':1,
               'sku_location':section_1
               }

sku_111_config={'name':'sku_111',
               'sku_time':1,
               'sku_location':section_1
               }


sku_2_config={'name':'sku_2',
               'sku_time':1,
               'sku_location':section_2
               }

sku_3_config={'name':'sku_3',
               'sku_time':1,
               'sku_location':section_3
               }

sku_4_config={'name':'sku_4',
               'sku_time':1,
               'sku_location':section_4
               }

sku_5_config={'name':'sku_5',
               'sku_time':1,
               'sku_location':section_5
               }

sku_6_config={'name':'sku_6',
               'sku_time':1,
               'sku_location':section_6
               }


