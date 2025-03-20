import pytz
import os
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log

__ALL__ = ['BondVolume']

class BondVolume(IndexListIndicator):
    lines = (
        "HsisHkd",
        "HsidBond",
        "HkdBond",
        "closeTime",
        "openTime"
    )

    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.HsisHkd[0] = float('-inf')
        self.lines.HsidBond[0] = float('-inf')
        self.lines.HkdBond[0] = float('-inf')
        self.lines.closeTime[0] = 0
        self.lines.openTime[0] = 0

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        cache_key_time = current_bar_time
        if current_bar_time.second != 0:
            # 回测模式下往前未来1分钟 实盘模式下往历史退30秒
            cache_key_time = current_bar_time.replace(second=0, microsecond=0)
            # if not self.data.islive():
            #     cache_key_time = cache_key_time + timedelta(minutes=1)
        cache_key_time_str = cache_key_time.strftime('%Y-%m-%d %H:%M:%S')

        result = None
        if cache_key_time_str in self.cache:
            result = self.cache[cache_key_time_str]
        else:
            for i in range(1, 5):
                hist_bar_time = cache_key_time - timedelta(minutes=i)
                hist_bar_time_str = hist_bar_time.strftime('%Y-%m-%d %H:%M:%S')
                if hist_bar_time_str in self.cache:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, kline time: {current_bar_time_str}, value[0] inherited from value[-{i}]")
                    result = self.cache[hist_bar_time_str]
                    break

        if result is not None:
            for key, value in dict(result).items():
                line = getattr(self.lines, key)
                line[0] = float(value)
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'type': 'indicator_bond_volume',
            'key_list': 'bond_volume',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params