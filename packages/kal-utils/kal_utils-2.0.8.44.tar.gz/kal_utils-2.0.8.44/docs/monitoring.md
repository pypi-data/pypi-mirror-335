# Monitoring Module

This module provides interfaces and prebuilt monitoring configuration and integration tools.

## Classes

### ConfigManager

::: kal_utils.monitoring.core.config_managers.ConfigManager

### EnvConfigManager

::: kal_utils.monitoring.core.config_managers.EnvConfigManager

### AWSConfigManager

::: kal_utils.monitoring.core.config_managers.AWSConfigManager

### PrometheusMetricsDecorator

::: kal_utils.monitoring.prometheus.prometheus_base.PrometheusMetricsDecorator

### LocationRequestCounter

::: kal_utils.monitoring.prometheus.locationRequestCounter.LocationRequestCounter

### RequestCounter

::: kal_utils.monitoring.prometheus.requestMetrics.RequestCounter

### ServerErrorMetrics

::: kal_utils.monitoring.prometheus.requestMetrics.ServerErrorMetrics

### RequestHist

::: kal_utils.monitoring.prometheus.requestMetrics.RequestHist

### CpuUsageMonitor

::: kal_utils.monitoring.prometheus.systemMetrics.CpuUsageMonitor

### MemoryUsageMonitor

::: kal_utils.monitoring.prometheus.systemMetrics.MemoryUsageMonitor

### DiskUsageMonitor

::: kal_utils.monitoring.prometheus.systemMetrics.DiskUsageMonitor

### NetworkUsageMonitor

::: kal_utils.monitoring.prometheus.systemMetrics.NetworkUsageMonitor

###TracingConfig

::: kal_utils.monitoring.tempo.tracing_manager.TracingConfig

###OTLPTracingConfig

::: kal_utils.monitoring.tempo.tracing_manager.OTLPTracingConfig

###JaegerTracingConfig

::: kal_utils.monitoring.tempo.tracing_manager.JaegerTracingConfig

## Functions
###span_with_attributes

::: kal_utils.monitoring.tempo.context_manager.span_with_attributes

###span_with_event

::: kal_utils.monitoring.tempo.context_manager.span_with_event

###add_span_attributes

::: kal_utils.monitoring.tempo.decorator_manager.add_span_attributes

###add_span_event

::: kal_utils.monitoring.tempo.decorator_manager.add_span_event

### configure_monitor

::: kal_utils.monitoring.core.config_metrics.configure_monitor

### get_enabled_metrics

::: kal_utils.monitoring.core.metrics.get_enabled_metrics

### get_metrics_classes

::: kal_utils.monitoring.core.metrics.get_metrics_classes

### create_unified_metrics_class

::: kal_utils.monitoring.prometheus.unifiedMetrics.create_unified_metrics_class

### authenticate

::: kal_utils.monitoring.utils.basic_authentication.authenticate

### add_parent_directory_to_sys_path

::: kal_utils.monitoring.utils.relative_imports.add_parent_directory_to_sys_path