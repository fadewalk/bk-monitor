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
import logging

from django.utils.translation import ugettext as _
from rest_framework import serializers

from bkmonitor.models import MetricListCache
from constants.data_source import DataSourceLabel, DataTypeLabel
from core.drf_resource import CacheResource, Resource
from fta_web.alert.handlers.alert import AlertQueryHandler

logger = logging.getLogger(__name__)


class GetDataSourceConfigResource(Resource):
    """
    获取数据源配置信息
    """

    class RequestSerializer(serializers.Serializer):
        bk_biz_id = serializers.IntegerField(label="业务ID")
        data_source_label = serializers.CharField(label="数据来源")
        data_type_label = serializers.CharField(label="数据类型")

    def perform_request(self, params):
        data_source_label = params["data_source_label"]
        data_type_label = params["data_type_label"]
        metrics = MetricListCache.objects.filter(
            bk_biz_id__in=[0, params["bk_biz_id"]], data_source_label=data_source_label, data_type_label=data_type_label
        ).only(
            "result_table_id",
            "result_table_name",
            "related_name",
            "extend_fields",
            "dimensions",
            "metric_field",
            "metric_field_name",
        )

        metric_dict = {}
        for metric in metrics:
            if metric.result_table_id not in metric_dict:
                name = bk_data_id = ""
                table_id = metric.result_table_id
                if (data_source_label, data_type_label) == (DataSourceLabel.BK_MONITOR_COLLECTOR, DataTypeLabel.LOG):
                    name = metric.related_name
                    bk_data_id = metric.result_table_id.split("_", -1)[-1]
                elif (data_source_label, data_type_label) == (DataSourceLabel.CUSTOM, DataTypeLabel.EVENT):
                    name = metric.result_table_name
                    bk_data_id = metric.extend_fields.get("bk_data_id", "")

                if metric.result_table_id not in metric_dict:
                    metric_dict[metric.result_table_id] = {
                        "id": table_id,
                        "bk_data_id": bk_data_id,
                        "name": name,
                        "metrics": [],
                        "dimensions": metric.dimensions,
                        "time_field": "time",
                    }
                else:
                    # 补全所有字段
                    exists_dimension_fields = {
                        dimension["id"] for dimension in metric_dict[metric.result_table_id]["dimensions"]
                    }
                    for dimension in metric.dimensions:
                        if dimension["id"] in exists_dimension_fields:
                            continue
                        metric_dict[metric.result_table_id]["dimensions"].append(dimension)

            metric_dict[metric.result_table_id]["metrics"].append(
                {"id": metric.metric_field, "name": metric.metric_field_name}
            )
        return list(metric_dict.values())


class GetAlarmEventField(CacheResource):
    """
    获取告警事件字段
    """

    def perform_request(self, params):
        return [
            {"id": "severity", "name": _("告警级别"), "is_dimension": True},
            {"id": "status", "name": _("告警状态"), "is_dimension": True},
            {"id": "alert_name", "name": _("告警名称"), "is_dimension": True},
            {"id": "strategy_id", "name": _("策略ID"), "is_dimension": True},
        ]


class GetAlarmEventDimensionValue(CacheResource):
    """
    获取告警事件维度值
    """

    class RequestSerializer(serializers.Serializer):
        bk_biz_id = serializers.IntegerField(label="业务ID")
        field = serializers.CharField(label="维度字段")

    def perform_request(self, params):
        return []


class QueryAlarmEventGraph(Resource):
    """
    查询告警事件图表
    """

    class RequestSerializer(serializers.Serializer):
        bk_biz_id = serializers.IntegerField(label="业务ID")
        where = serializers.ListField(label="查询条件", default=[])
        group_by = serializers.ListField(label="维度")
        start_time = serializers.IntegerField(label="开始时间")
        end_time = serializers.IntegerField(label="结束时间")
        interval = serializers.CharField(label="时间间隔", default="auto")

    def perform_request(self, params):
        handler = AlertQueryHandler(
            bk_biz_ids=[params["bk_biz_id"]],
            conditions=params["where"],
            start_time=params["start_time"],
            end_time=params["end_time"],
        )

        data = handler.date_histogram(params["interval"], params["group_by"])

        series = []
        for dimension_tuple, status_mapping in data.items():
            dimensions = dict(dimension_tuple)
            for status, value in status_mapping.items():
                datapoints = [[count, timestamp] for timestamp, count in value.items()]
                if "status" in params["group_by"]:
                    new_dimensions = {"status": status, **dimensions}
                else:
                    new_dimensions = dimensions
                series.append(
                    {
                        "datapoints": datapoints,
                        "dimensions": new_dimensions,
                        "target": "|".join([f"{k}:{v}" for k, v in {**dimensions, "status": status}.items()]),
                    }
                )
        return {"series": series}
