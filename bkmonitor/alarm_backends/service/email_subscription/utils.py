# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import datetime

import arrow

from alarm_backends.core.context import logger
from bkmonitor.models import HourFrequencyTime
from bkmonitor.utils.range import TIME_MATCH_CLASS_MAP
from bkmonitor.utils.range.period import TimeMatch, TimeMatchBySingle
from bkmonitor.utils.send import Sender


def parse_frequency(frequency, last_send_time=None) -> list:
    """
    解析发送频率
    """
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    run_time_strings = []
    if frequency["type"] == 1:
        run_time_strings = [frequency["run_time"]]
    elif frequency["type"] == 5:
        current_hour = datetime.datetime.today().strftime("%H")
        run_time_config = HourFrequencyTime.TIME_CONFIG.get(str(frequency["hour"]))
        if run_time_config:
            hours = run_time_config.get("hours", [current_hour])
            minutes = run_time_config.get("minutes", ["00"])
            for hour in hours:
                if hour != current_hour:
                    # 发送小时非当前时间，直接返回
                    continue
                for minute in minutes:
                    if last_send_time:
                        last_send_hour = last_send_time.strftime("%H")
                        last_send_min = last_send_time.strftime("%M")
                        if last_send_hour == current_hour and last_send_min >= minute:
                            # 当前这个小时，且在检测的这个分钟已经发送过，则不再检测发送
                            # 因为有一分钟裕量，否则有可能前后一分钟都会命中
                            continue
                    run_time_strings.append(f'{today} {hour}:{minute}:00')
    else:
        run_time_strings = [f'{datetime.datetime.today().strftime("%Y-%m-%d")} {frequency["run_time"]}']
    return run_time_strings


def is_run_time(frequency, run_time_strings: list) -> bool:
    """
    是否到执行时间
    """
    now_time = arrow.now()
    one_minute_ago = TimeMatch.convert_datetime_to_arrow(datetime.datetime.now() - datetime.timedelta(minutes=1))
    time_match_class = TIME_MATCH_CLASS_MAP.get(frequency["type"], TimeMatchBySingle)
    frequency["begin_time"] = one_minute_ago.format("HH:mm:ss")
    frequency["end_time"] = now_time.format("HH:mm:ss")
    time_check = time_match_class(frequency, one_minute_ago, now_time)

    for run_time in run_time_strings:
        run_time = TimeMatch.convert_datetime_to_arrow(datetime.datetime.strptime(run_time, "%Y-%m-%d %H:%M:%S"))
        if time_check.is_match(run_time):
            return True
    return False


def get_data_range(frequency) -> dict:
    now_time = datetime.datetime.now()
    # 如果没有频率参数，默认取最近一天的数据
    if not frequency:
        from_time = now_time + datetime.timedelta(hours=-24)
        return {"start_time": from_time, "end_time": now_time}
    # 如果存在用户自定义的数据范围，取用户自定义的数据范围
    if frequency.get("data_range", {}):
        time_level = frequency["data_range"]["time_level"]
        number = frequency["data_range"]["number"]
        kwargs = {time_level: -int(number)}
        from_time = now_time + datetime.timedelta(**kwargs)
    # 如果用户没有自定义的数据范围，取发送频率对应的数据范围
    else:
        if frequency["type"] == 3:
            from_time = now_time + datetime.timedelta(hours=-24 * 7)
        elif frequency["type"] == 4:
            from_time = now_time + datetime.timedelta(hours=-24 * 30)
        elif frequency["type"] == 5:
            now_time = datetime.datetime.strptime(now_time.strftime("%Y-%m-%d %H:%M:00"), "%Y-%m-%d %H:%M:%S")
            from_time = now_time - datetime.timedelta(minutes=frequency["hour"] * 60)
        else:
            from_time = now_time + datetime.timedelta(hours=-24)
    return {"start_time": from_time, "end_time": now_time}


def is_invalid(subscription) -> bool:
    """
    是否已失效
    """
    now_timestamp = arrow.now().timestamp
    # 超出有效时间
    if now_timestamp > subscription.end_time or now_timestamp < subscription.start_time:
        return True
    # 仅发送一次类型订阅的已有上一次发送时间
    if subscription.frequency["type"] == 1 and subscription.last_send_time:
        return True
    return False


def send_email(context: dict, subscribers: list) -> dict:
    sender = Sender(
        title_template_path=context["title_template_path"],
        content_template_path=context["content_template_path"],
        context=context,
    )
    if context.get("title"):
        sender.title = context["title"]
    if context.get("content"):
        sender.content = context["content"]
    try:
        result = sender.send_mail(subscribers)
        return result
    except Exception as e:
        logger.exception(e)


def send_wxbot(context: dict, chatids: list):
    sender = Sender(
        title_template_path=context["title_template_path"],
        content_template_path=context["content_template_path"],
        context=context,
    )
    if context.get("title"):
        sender.title = context["title"]
    if context.get("content"):
        sender.content = context["content"]
    try:
        result = sender.send_wxwork_content("markdown", sender.content, chatids)
        return result
    except Exception as e:
        logger.exception(e)
