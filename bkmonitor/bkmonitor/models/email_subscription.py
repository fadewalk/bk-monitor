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
import arrow
from django.db import models
from django.utils.translation import ugettext_lazy as _lazy

from bkmonitor.models.external_iam import APPORVAL_STEP_CHOICES, STATUS_CHOICES
from bkmonitor.utils.enum import ChoicesEnum
from bkmonitor.utils.model_manager import AbstractRecordModel, Model


class ChannelEnum(ChoicesEnum):
    # 订阅渠道
    EMAIL = "email"
    WXBOT = "wxbot"
    USER = "user"

    _choices_labels = ((EMAIL, _lazy("外部邮件")), (WXBOT, _lazy("企业微信机器人")), (USER, _lazy("内部用户")))


class ScenarioEnum(ChoicesEnum):
    # 订阅场景
    CLUSTERING = "clustering"
    DASHBOARD = "dashboard"
    SCENE = "scene"

    _choices_labels = ((CLUSTERING, _lazy("日志聚类")), (DASHBOARD, _lazy("仪表盘")), (SCENE, _lazy("观测场景")))


class SendStatusEnum(ChoicesEnum):
    # 订阅发送状态
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_FAILED = "partial_failed"

    _choices_labels = ((SUCCESS, _lazy("成功")), (FAILED, _lazy("失败")), (PARTIAL_FAILED, _lazy("部分失败")))


class SendModeEnum(ChoicesEnum):
    # 订阅模式
    PERIODIC = "periodic"
    ONE_TIME = "one_time"


class HourFrequencyTime:
    HALF_HOUR = {"minutes": ["00", "30"]}
    HOUR = {"minutes": ["00"]}
    HOUR_2 = {"hours": ["00", "02", "04", "06", "08", "10", "12", "14", "16", "18", "20", "22"]}
    HOUR_6 = {"hours": ["00", "06", "12", "18"]}
    HOUR_12 = {"hours": ["09", "21"]}

    TIME_CONFIG = {"0.5": HALF_HOUR, "1": HOUR, "2": HOUR_2, "6": HOUR_6, "12": HOUR_12}


class SubscriptionChannel(Model):
    """
    订阅渠道
    """

    subscription_id = models.IntegerField(verbose_name="订阅ID", db_index=True)
    channel_name = models.CharField(verbose_name="渠道名称", max_length=32, choices=ChannelEnum.get_choices())
    is_enabled = models.BooleanField(verbose_name="是否启用", default=True)
    subscribers = models.JSONField(verbose_name="订阅人", default=list)
    send_text = models.CharField(verbose_name="提示文案", max_length=256, null=True)

    class Meta:
        verbose_name = "订阅渠道"
        verbose_name_plural = "订阅渠道"
        db_table = "subscription_channel"


class EmailSubscription(AbstractRecordModel):
    """
    邮件订阅
    """

    name = models.CharField(verbose_name="订阅名称", max_length=64)
    bk_biz_id = models.IntegerField(verbose_name="业务ID", default=0, blank=True, db_index=True)
    scenario = models.CharField(verbose_name="订阅场景", max_length=32, choices=ScenarioEnum.get_choices())
    frequency = models.JSONField(verbose_name="发送频率", default=dict)
    content_config = models.JSONField(verbose_name="内容配置", default=dict)
    scenario_config = models.JSONField(verbose_name="场景配置", default=dict)
    start_time = models.IntegerField(verbose_name="开始时间")
    end_time = models.IntegerField(verbose_name="结束时间")
    last_send_record_ids = models.JSONField(verbose_name="最近一次发送记录ID", null=True, default=list)
    is_manager_created = models.BooleanField(verbose_name="是否管理员创建", default=False)

    class Meta:
        verbose_name = "邮件订阅"
        verbose_name_plural = "邮件订阅"
        db_table = "email_subscription"

    @property
    def send_mode(self):
        if self.frequency["type"] != 1:
            return SendModeEnum.PERIODIC
        return SendModeEnum.ONE_TIME

    @property
    def is_invaild(self):
        now_timestamp = arrow.now().timestamp
        if now_timestamp > self.end_time or now_timestamp < self.start_time:
            return True
        if self.frequency["type"] == 1:
            return True
        return False

    def is_self_subscribed(self):
        channels = SubscriptionChannel.objects.filter(channel_name=ChannelEnum.USER, subscription_id=self.id)
        if channels.exist():
            subscriber_ids = [subscriber.id for subscriber in channels.first().subscribers]
            return self.create_user in subscriber_ids

    def get_failed_subscribers(self):
        send_results = list(self.last_send_records.values())
        failed_subscribers = []
        for result in send_results:
            if result["send_status"] != "success":
                for send_result in result["send_result"]:
                    if send_result["result"]:
                        continue
                    failed_subscribers.append(send_result["id"])
        return failed_subscribers


class SubscriptionSendRecord(Model):
    """
    订阅发送记录
    """

    subscription_id = models.IntegerField(verbose_name="订阅ID", db_index=True)
    channel_name = models.CharField(verbose_name="渠道名称", max_length=32, choices=ChannelEnum.get_choices())
    send_results = models.JSONField(verbose_name="发送结果详情", default=list)
    send_status = models.CharField(verbose_name="发送状态", max_length=32, choices=SendStatusEnum.get_choices())
    send_time = models.DateTimeField(verbose_name="发送时间", null=True)

    class Meta:
        verbose_name = "订阅发送记录"
        verbose_name_plural = "订阅发送记录"
        db_table = "subscription_send_record"


class SubscriptionApplyRecord(AbstractRecordModel):
    """
    订阅审批记录
    """

    subscription_id = models.IntegerField(verbose_name="订阅ID", db_index=True)
    bk_biz_id = models.IntegerField(verbose_name="业务ID", db_index=True)
    approvers = models.JSONField("审批人列表", default=list)
    expire_time = models.DateTimeField("过期时间", null=True, default=None)
    approval_step = models.CharField("审批步骤", max_length=32, choices=APPORVAL_STEP_CHOICES, default="no_status")
    approval_sn = models.CharField("审批单号", max_length=128, default="", null=True, blank=True)
    approval_url = models.CharField("审批地址", default="", max_length=1024, null=True, blank=True)
    status = models.CharField("审批状态", max_length=32, choices=STATUS_CHOICES, default="no_status")

    class Meta:
        verbose_name = "订阅审批记录"
        verbose_name_plural = "订阅审批记录"
        db_table = "subscription_apply_record"
