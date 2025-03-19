import pytz
import os
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator

__ALL__ = ['VolStrengthWarrant']

class VolStrengthWarrant(IndexListIndicator):
    lines = (
        "volumeRankLevel",
        "volumeStrengthTodayCoverDays",
        "today",
        "volumeIntraU",
        "consecutiveDays",
        "window20",
        "VolumeStrengthRankLevelTest",
        "VolumeEqualizationLevel",
        "days7",
        "VolumeLevelWithSpeed",
        "closeTime",
        "openTime"
    )

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.volumeRankLevel[0] = float('-inf')
        self.lines.volumeStrengthTodayCoverDays[0] = float('-inf')
        self.lines.today[0] = float('-inf')
        self.lines.volumeIntraU[0] = float('-inf')
        self.lines.consecutiveDays[0] = float('-inf')
        self.lines.window20[0] = float('-inf')
        self.lines.VolumeStrengthRankLevelTest[0] = float('-inf')
        self.lines.VolumeEqualizationLevel[0] = float('-inf')
        self.lines.days7[0] = float('-inf')
        self.lines.VolumeLevelWithSpeed[0] = float('-inf')
        self.lines.closeTime[0] = 0
        self.lines.openTime[0] = 0

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        if current_bar_time.second != 0:
            current_bar_time = current_bar_time.replace(second=0, microsecond=0)
            current_bar_time = current_bar_time + timedelta(minutes=1)
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')

        if current_bar_time_str in self.cache:
            result = self.cache[current_bar_time_str]

            for key, value in dict(result).items():
                line = getattr(self.lines, key)
                line[0] = float(value)
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': "hk_warrant",
            'type': 'indicator_volume_strength',
            'key_list': 'vol_list',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params