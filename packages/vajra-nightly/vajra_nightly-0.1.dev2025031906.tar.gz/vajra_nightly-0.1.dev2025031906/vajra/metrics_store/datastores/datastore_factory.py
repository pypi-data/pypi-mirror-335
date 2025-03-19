from vajra._native.metrics_store import Metric, PlotType

from ..datastores.base_datastore import BaseDataStore
from ..datastores.labeled_cdf_datastore import LabeledCDFDataStore
from ..datastores.time_series_datastore import TimeSeriesDataStore
from ..datastores.unlabeled_cdf_datastore import UnlabeledCDFDataStore


class DataStoreFactory:
    @staticmethod
    def get_datastore(
        metric: Metric, plot_dir: str, store_png: bool = False
    ) -> BaseDataStore:
        if metric.plot_type == PlotType.CDF or metric.plot_type == PlotType.HISTOGRAM:
            if metric.requires_label:
                return LabeledCDFDataStore(metric, plot_dir, store_png)
            else:
                return UnlabeledCDFDataStore(metric, plot_dir, store_png)
        elif metric.plot_type == PlotType.TIME_SERIES:
            return TimeSeriesDataStore(metric, plot_dir, store_png)
        else:
            raise ValueError(f"Unsupported metric type: {metric.plot_type}")
