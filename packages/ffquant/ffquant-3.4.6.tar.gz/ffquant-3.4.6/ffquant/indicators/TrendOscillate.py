import pytz
from ffquant.indicators.IndexListIndicator import IndexListIndicator

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
        "mainTrendId"
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

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')

        if current_bar_time_str in self.cache:
            result = self.cache[current_bar_time_str]

            for key, value in dict(result).items():
                if key == 'openTime' or key == 'closeTime':
                    continue

                if key != 'trendDir' and key != 'isOscillating':
                    if isinstance(value, float) or isinstance(value, int):
                        line = getattr(self.lines, key)
                        line[0] = float(value)
                elif str(value) != '':
                    line = getattr(self.lines, key)
                    if str(value) == 'UP':
                        line[0] == 1
                    elif str(value) == 'DOWN':
                        line[0] == -1
                    elif str(value) == 'true':
                        line[0] == 1
                    elif str(value) == 'false':
                        line[0] == 0
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