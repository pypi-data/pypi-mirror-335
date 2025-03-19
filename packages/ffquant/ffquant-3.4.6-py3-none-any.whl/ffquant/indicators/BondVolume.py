import pytz
import os
from ffquant.indicators.IndexListIndicator import IndexListIndicator

__ALL__ = ['BondVolume']

class BondVolume(IndexListIndicator):
    lines = (
        "HsisHkd",
        "HsidBond",
        "HkdBond"
    )

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.HsisHkd[0] = float('-inf')
        self.lines.HsidBond[0] = float('-inf')
        self.lines.HkdBond[0] = float('-inf')

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')

        if current_bar_time_str in self.cache:
            result = self.cache[current_bar_time_str]

            for key, value in dict(result).items():
                if key == 'openTime' or key == 'closeTime':
                    continue

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