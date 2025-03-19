import pytz
from datetime import datetime
from ffquant.indicators.IndexListIndicator import IndexListIndicator

__ALL__ = ['ActBuySellHedgePos']

class ActBuySellHedgePos(IndexListIndicator):
    lines = (
        'isLczDerActBS',
        'isLczDerStrActBS',
        'isSczStoActBS',
        'isSczStoStrActBS',
        'isSczDerActBS',
        'shList_BULL',
        'shList_BEAR',
        'shList_FUTURES',
        'shList_ETF',
        'shList_CN_ETF',
        'lnList_BULL',
        'lnList_BEAR',
        'lnList_FUTURES',
        'lnList_ETF',
        'lnList_CN_ETF'
    )

    # 根节点的openTime和closeTime表示属于哪根K线，子节点的openTime和closeTime表示信号的原材料的时间
    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.isLczDerActBS[0] = float('-inf')
        self.lines.isLczDerStrActBS[0] = float('-inf')
        self.lines.isSczStoActBS[0] = float('-inf')
        self.lines.isSczStoStrActBS[0] = float('-inf')
        self.lines.isSczDerActBS[0] = float('-inf')
        self.lines.shList_BULL[0] = 0
        self.lines.shList_BEAR[0] = 0
        self.lines.shList_FUTURES[0] = 0
        self.lines.shList_ETF[0] = 0
        self.lines.shList_CN_ETF[0] = 0
        self.lines.lnList_BULL[0] = 0
        self.lines.lnList_BEAR[0] = 0
        self.lines.lnList_FUTURES[0] = 0
        self.lines.lnList_ETF[0] = 0
        self.lines.lnList_CN_ETF[0] = 0

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')

        if current_bar_time_str in self.cache:
            result = self.cache[current_bar_time_str]
            for key, value in dict(result).items():
                if key == 'isLczDerActBS' or key == 'isLczDerStrActBS' or key == 'isSczStoActBS' or key == 'isSczStoStrActBS' or key == 'isSczDerActBS':
                    line = getattr(self.lines, key)
                    line[0] = float(value)
                elif key == 'shList' or key == 'lnList':
                    for item in list(value):
                        line = getattr(self.lines, key + '_' + item)
                        line[0] = 1.0
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'type': 'index_zyj',
            'key_list': 'act_bs_hedging_pos',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params