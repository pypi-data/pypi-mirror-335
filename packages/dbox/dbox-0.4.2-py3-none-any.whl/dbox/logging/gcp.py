import logging
from typing import Optional, Type

from google.cloud.logging import Client
from google.cloud.logging_v2.handlers.transports import BackgroundThreadTransport, Transport
from google.cloud.logging_v2.resource import Resource

from dbox.ctx import use_key

from .context import current_log_labels

GLOBAL_RESOURCE = Resource(type="global", labels={})
DEFAULT_LOGGER_NAME = "python"


class _CloudLoggingFilter(logging.Filter):
    def __init__(self, project=None, default_labels=None):
        self.project = project
        self.default_labels = default_labels if default_labels else {}

    @staticmethod
    def _infer_source_location(record: logging.LogRecord):
        name_map = [
            ("line", "lineno"),
            ("file", "pathname"),
            ("function", "funcName"),
        ]
        output = {}
        for gcp_name, std_lib_name in name_map:
            value = getattr(record, std_lib_name, None)
            if value is not None:
                output[gcp_name] = value
        return output if output else None

    def filter(self, record: logging.LogRecord):
        """
        Add new Cloud Logging data to each LogRecord as it comes in
        """
        user_labels = getattr(record, "labels", {}) or current_log_labels()

        # set new record values
        record._resource = getattr(record, "resource", None)
        record._http_request = getattr(record, "http_request", None) or use_key("http_request", None)
        record._source_location = self._infer_source_location(record)
        # add logger name as a label if possible
        record._labels = {"python_logger": record.name or "missing", **self.default_labels, **user_labels}
        return True


class CloudLoggingHandler(logging.StreamHandler):
    def __init__(
        self,
        client: Client,
        *,
        name: str = DEFAULT_LOGGER_NAME,
        transport: Type[Transport] = BackgroundThreadTransport,
        resource=GLOBAL_RESOURCE,
        global_labels: Optional[dict] = None,
        **kwargs,
    ):
        """Note that global resource type doesn't allow to specify arbitrary labels"""
        super().__init__(stream=None)
        self.name = name
        self.client = client
        self.transport = transport(client, name, resource=resource)
        self.project_id = client.project
        if not isinstance(resource, Resource):
            assert isinstance(resource, dict), "Resource must be a dictionary or an instance of Resource"
            resource = Resource(**resource)
        self.resource = resource
        self.labels = global_labels
        # add extra keys to log record
        log_filter = _CloudLoggingFilter(project=self.project_id, default_labels=global_labels)
        self.addFilter(log_filter)
        self.formatter = logging.Formatter(fmt="%(message)s")

    def emit(self, record: logging.LogRecord):
        message = self.format(record)
        record._resource = record._resource or self.resource
        # send off request
        self.transport.send(
            record,
            message,
            resource=record._resource,
            labels=record._labels,
            http_request=record._http_request,
            source_location=record._source_location,
        )
