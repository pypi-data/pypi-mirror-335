import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log

__ALL__ = ['TrendOscillate']

class TrendOscillate(IndexListIndicator):
    lines = (
        "oscUpperBound",
        "subTrendSize",
        "mainTrendSize",
        "mainTrendTsFm",
        "trendOscSize",
        "trendDir",
        "trendOscUpDn",
        "trendOscTsFm",
        "oscLowerBound",
        "isOscillating",
        "subTrendTsFm",
        "mainTrendPattern",
        "mainTrendId",
        "closeTime",
        "openTime",
    )

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.oscUpperBound[0] = float('-inf')
        self.lines.subTrendSize[0] = float('-inf')
        self.lines.mainTrendSize[0] = float('-inf')
        self.lines.mainTrendTsFm[0] = float('-inf')
        self.lines.trendOscSize[0] = float('-inf')
        self.lines.trendDir[0] = float('-inf')
        self.lines.trendOscUpDn[0] = float('-inf')
        self.lines.trendOscTsFm[0] = float('-inf')
        self.lines.oscLowerBound[0] = float('-inf')
        self.lines.isOscillating[0] = float('-inf')
        self.lines.subTrendTsFm[0] = float('-inf')
        self.lines.mainTrendPattern[0] = float('-inf')
        self.lines.mainTrendId[0] = float('-inf')
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
                if key != 'trendDir' and key != 'isOscillating':
                    if isinstance(value, float) or isinstance(value, int):
                        line = getattr(self.lines, key)
                        line[0] = float(value)
                elif str(value) != '':
                    line = getattr(self.lines, key)
                    if str(value) == 'UP':
                        line[0] = 1
                    elif str(value) == 'DOWN':
                        line[0] = -1
                    elif str(value).lower() == 'true':
                        line[0] = 1
                    elif str(value).lower() == 'false':
                        line[0] = 0
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': self.p.symbol,
            'type': 'index_zyj',
            'key_list': 'trend_and_oscillation',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params