# Copyright 2019 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
`cloud_monitoring.py`
Cloud Monitoring exporter class.
"""
import logging

import google.api_core.exceptions
from google.api import metric_pb2 as ga_metric
from google.cloud import monitoring_v3

from .base import MetricsExporter

LOGGER = logging.getLogger(__name__)


class CloudMonitoringSpecificExporter(MetricsExporter):
    """Cloud Monitoring exporter class."""
    METRIC_PREFIX = "custom.googleapis.com/slo_generator/"
    REQUIRED_FIELDS = ['project_id']

    def __init__(self):
        self.client = monitoring_v3.MetricServiceClient()

    def export_metric(self, data):
        """Export metric to Cloud Monitoring. Create metric descriptor if
        it doesn't exist.

        Args:
            data (dict): Data to send to Cloud Monitoring.
            project_id (str): Cloud Monitoring project id.

        Returns:
            object: Cloud Monitoring API result.
        """
        if not self.get_metric_descriptor(data):
            self.create_metric_descriptor(data)
        self.create_timeseries(data)

    def create_timeseries(self, data):
        """Create Cloud Monitoring timeseries.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor.
        """
        labels = data['labels']
        series = monitoring_v3.types.TimeSeries()
        series.metric.type = data['name']
        for key, value in labels.items():
            if key == "slo_name" or key == "product_name" or key == "slo_type" or key == "env" or key == "product_id"  or key == "service_name" or key == "platform" or key == "client_coverage" or key == "slo_statement" or key == "feature_name" or key == "module_id" or key == "community" or key == "domain" or key == "error_budget_policy_step_name" or key == "entity":
                series.metric.labels[key] = value
        series.resource.type = 'global'

        # Create a new data point.
        #point = series.points.add()

        # Define end point timestamp.
        timestamp = data['timestamp']
        seconds = int(timestamp)
        nanos = int((timestamp - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval({
            "end_time": {
                "seconds": seconds,
                "nanos": nanos
            }
        })

        # Create a new data point and set the metric value.
        point = monitoring_v3.Point({
            "interval": interval,
            "value": {
                "double_value": data['value']
            }
        })
        series.points = [point]

        
        """
        point.interval.end_time.seconds = int(timestamp)
        point.interval.end_time.nanos = int(
            (timestamp - point.interval.end_time.seconds) * 10**9)

        # Set the metric value.
        point.value.double_value = data['value'] 

        # Record the timeseries to Cloud Monitoring.
        project = self.client.project_path(data['project_id'])
        self.client.create_time_series(project, [series])
        """
        # Record the timeseries to Cloud Monitoring.
        project = self.client.common_project_path(data['project_id'])
        self.client.create_time_series(name=project, time_series=[series])
        # pylint: disable=E1101
        labels = series.metric.labels
        LOGGER.debug(
            f"timestamp: {timestamp} value: {point.value.double_value}"
            f"{labels['service_name']}-{labels['feature_name']}-"
            f"{labels['slo_name']}-{labels['error_budget_policy_step_name']}")

    

    """
    def get_metric_descriptor(self, data):
        Get Cloud Monitoring metric descriptor.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor (or None if not found).
        
        descriptor = self.client.metric_descriptor_path(data['project_id'],
                                                        data['name'])
        try:
            return self.client.get_metric_descriptor(descriptor)
        except google.api_core.exceptions.NotFound:
            return None
    """

    def get_metric_descriptor(self, data):
        """Get Cloud Monitoring metric descriptor.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor (or None if not found).
        """
        project_id = data['project_id']
        metric_id = data['name']
        request = monitoring_v3.GetMetricDescriptorRequest(
            name=f"projects/{project_id}/metricDescriptors/{metric_id}")
        try:
            return self.client.get_metric_descriptor(request)
        except google.api_core.exceptions.NotFound:
            return None

    """
    def create_metric_descriptor(self, data):
        Create Cloud Monitoring metric descriptor.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor.
        
        project = self.client.project_path(data['project_id'])
        descriptor = monitoring_v3.types.MetricDescriptor()
        descriptor.type = data['name']
        descriptor.metric_kind = (
            monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
        descriptor.value_type = (
            monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
        descriptor.description = data['description']
        self.client.create_metric_descriptor(project, descriptor)
        return descriptor
    """
    
    def create_metric_descriptor(self, data):
        """Create Cloud Monitoring metric descriptor.

        Args:
            data (dict): Metric data.

        Returns:
            object: Metric descriptor.
        """
        project = self.client.common_project_path(data['project_id'])
        descriptor = ga_metric.MetricDescriptor()
        descriptor.type = data['name']
        # pylint: disable=E1101
        descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE
        descriptor.value_type = ga_metric.MetricDescriptor.ValueType.DOUBLE
        # pylint: enable=E1101
        descriptor.description = data['description']
        descriptor = self.client.create_metric_descriptor(
            name=project, metric_descriptor=descriptor)
        return descriptor
