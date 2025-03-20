import backtrader as bt
import os
import pytz
from datetime import datetime, timedelta, timezone
import time
import requests
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.IndexListIndicator import IndexListIndicator

__ALL__ = ['PricePattern']

class PricePattern(IndexListIndicator):
    params = (
        ('url', os.getenv('INDEX_COLLECT_LIST_URL', default='http://192.168.25.127:8285/index/collect/list')),
        ('symbol', 'PV_MONITOR:HSI1'),
    )

    lines = (
        'close',
        'turnover',
        'premium',
    )

    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['timeClose'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.close[0] = float('-inf')
        self.lines.turnover[0] = float('-inf')
        self.lines.premium[0] = float('-inf')

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        cache_key_time = current_bar_time
        cache_key_time_str = cache_key_time.strftime('%Y-%m-%d %H:%M:%S')

        result = None
        if cache_key_time_str in self.cache:
            result = self.cache[cache_key_time_str]
        else:
            for i in range(1, 5):
                hist_bar_time = cache_key_time - timedelta(seconds=i*30)
                hist_bar_time_str = hist_bar_time.strftime('%Y-%m-%d %H:%M:%S')
                if hist_bar_time_str in self.cache:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, kline time: {current_bar_time_str}, value[0] inherited from value[-{i}]")
                    result = self.cache[hist_bar_time_str]
                    break

        if result is not None:
            for key, value in dict(result).items():
                if key == 'timeOpen' or key == 'timeClose':
                    continue

                if key == 'close' or key == 'turnover' or key == 'premium':
                    line = getattr(self.lines, key)
                    line[0] = float(value)
            return result['timeClose']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': 'PV_MONITOR:HSI1',    # 这个信号只针对这个symbol
            'interval': '30S',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params

    def next(self):
        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cur_bar_local_time_str = cur_bar_local_time.strftime('%Y-%m-%d %H:%M:%S')

        # 实时模式
        is_live = self.data.islive()
        if is_live:
            # 如果不在缓存中 则请求数据
            if cur_bar_local_time_str not in self.cache:
                tdelta = timedelta(minutes=2)
                start_time = cur_bar_local_time - tdelta
                end_time = cur_bar_local_time
                self.batch_fetch(start_time, end_time)
            else:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]}")
        else:
            # 非实时模式 一次性把所有的数据都捞回来
            if len(self.cache) == 0:
                start_time_str = self.data.p.start_time
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                if self.data.p.backfill_size > 0:
                    tdelta = timedelta(seconds=self.data.p.backfill_size * self.data.p.compression)
                    if self.data.p.timeframe == bt.TimeFrame.Minutes:
                        tdelta = timedelta(minutes=self.data.p.backfill_size * self.data.p.compression)
                    start_time = start_time - tdelta

                end_time_str = self.data.p.end_time
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                self.batch_fetch(start_time, end_time)

            if cur_bar_local_time_str in self.cache:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]}")

        # 不管是实时模式还是非实时模式 都在此判断最终应该返回什么数值
        create_time = self.determine_final_result()

        # Replace -info with previous value. Starting value is zero. heartbeat info print
        for line_name in self.lines.getlinealiases():
            line = getattr(self.lines, line_name)
            kline_local_time_str = cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
            create_local_time_str = datetime.fromtimestamp(create_time / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

            # 这里的打印最终会输出到标准输出日志中 这样的日志被用于分析行情的延迟等问题
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, create_time: {create_local_time_str}, {line_name}: {line[0]}")

    def batch_fetch(self, start_time: datetime, end_time: datetime):
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        params = self.prepare_params(start_time_str, end_time_str)

        retry_count = 0
        max_retry_count = self.p.max_retries
        while retry_count < max_retry_count:
            retry_count += 1
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

            response = requests.get(self.p.url, params=params).json()
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

            if response.get('code') != '200':
                raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

            if response.get('results') is not None and len(response['results']) > 0:
                results = response['results']
                results.sort(key=lambda x: x['timeClose'])
                for result in results:
                    self.handle_api_resp(result)
                break
            time.sleep(1)