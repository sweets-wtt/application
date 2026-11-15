"""依赖装配"""

import os

from app.log import configure

from server.core.settings import settings


def _instrument() -> None:
    """接线 OpenTelemetry - 提供方与 FastAPI 埋点"""

    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # 资源 - 服务名取 OTEL_SERVICE_NAME
    resource = Resource.create()

    # 追踪提供方 - OTLP 批处理导出
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # 指标提供方 - OTLP 周期导出
    metrics.set_meter_provider(
        MeterProvider(
            resource=resource,
            metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
        )
    )

    # FastAPI 埋点 - 须在应用实例化前替换类
    FastAPIInstrumentor().instrument()


def setup() -> None:
    """装配应用依赖"""

    # 日志环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()

    # 存在 OTLP 端点才接线遥测 - 测试离线安全
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        _instrument()
