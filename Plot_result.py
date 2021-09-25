# -*- coding:utf-8 -*-
"""
作者：l_jiujiu
日期：2021.09.25
"""

import matplotlib.pyplot as plt
import datetime
import matplotlib.gridspec as gridspec  # 分割子图

def plot_results(self):
    plt.plot(range(len(self.stock_info['history']['price'])), self.stock_info['history']['price'])
    plt.ylim([self.stock_info['min_price'], self.stock_info['max_price']])
    plt.show()
    return


def draw_k(self, ):
    today = datetime.datetime.today()
    # date_list = [today - datetime.timedelta(days=x) for x in range(len(self.stock_info['history']['price']))]
    data = {
        'Open': self.stock_info['history']['price'],
        'Close': self.stock_info['history']['price'][1:] + [self.stock_info['current_price']],
        'High': self.stock_info['history']['highest_price'],
        'Low': self.stock_info['history']['lowest_price'],
        'Volume': self.stock_info['history']['volume'],
    }
    df = pd.DataFrame(data, index=pd.date_range(today, periods=len(self.stock_info['history']['price']), freq='T'))

    mc = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='i',
        wick='i',
        volume='in',
        inherit=True
    )
    s = mpf.make_mpf_style(gridstyle='-.',
                           gridaxis='both',
                           y_on_right=False,
                           marketcolors=mc)

    mpf.plot(df,
             type='candle',
             # type='line',
             style=s,
             # title='ETF 300, Nov 2019',
             ylabel='Price (CNY)',
             ylabel_lower='Shares \nTraded',
             volume=True,
             # mav=(3, 6, 9),
             # savefig='test-mplfiance.png',
             )
    return