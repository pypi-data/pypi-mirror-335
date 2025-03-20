import backtrader as bt
from ffquant.utils.Logger import Logger, stdout_log
import pytz
import requests
from ffquant.utils.Apollo import Apollo
from datetime import timedelta, datetime

class BaseStrategy(bt.Strategy):
    params = (
        ('name', None),
        ('logger', None),
        ('debug', None),
        ('test', None),
        ("check_chosen_strat", False)
    )

    def __init__(self):
        if self.p.logger is not None:
            self.logger = self.p.logger
        elif self.p.name is not None:
            self.logger = Logger(self.p.name)

        self.apollo = Apollo()
        if self.logger is not None and self.logger.name is not None:
            # namespace名字长度限制为32
            self.apollo = Apollo(namespace=self.logger.name[-32:])

    def next(self):
        cur_bar_date_str = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d")
        prev_bar_date_str = self.data.datetime.datetime(-1).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d")
        if prev_bar_date_str < cur_bar_date_str:
            stdout_log(f"re-initialize strategy due to date change from {prev_bar_date_str} to {cur_bar_date_str}")
            self.initialize()
            self.start()

    def initialize(self):
        pass

    def start(self):
        pass

    def get_perf_stats(self, port):
        result = None
        try:
            url = f"http://127.0.0.1:{port}/api/stats"
            return requests.get(url).json()
        except Exception as e:
            stdout_log(f"Failed to get performance stats. return None")
        return result

    # 如果是回测模式 永远返回True 如果是实时模式 需要判断下一根k线的时间是否大于当前时间
    def should_continue_current_kline(self):
        if not self.data.islive():
            return True

        timeframe = self.data.p.timeframe
        compression = self.data.p.compression

        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        next_bar_local_time = cur_bar_local_time
        if timeframe == bt.TimeFrame.Seconds:
            next_bar_local_time = cur_bar_local_time + timedelta(seconds=compression)
        elif timeframe == bt.TimeFrame.Minutes:
            next_bar_local_time = cur_bar_local_time + timedelta(minutes=compression)
        elif timeframe == bt.TimeFrame.Days:
            next_bar_local_time = cur_bar_local_time + timedelta(days=compression)

        # 如果下一根k线的时间大于当前时间 那就表明当前k线是最新的k线了 应该继续执行
        return datetime.now().astimezone() < next_bar_local_time