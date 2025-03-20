from abc import abstractmethod

import pandas as pd

from vajra._native.metrics_store import Metric, PlotType, unit_type_to_string

from ..datastores.base_datastore import BaseDataStore
from ..plotter import Plotter


class BaseCDFDataStore(BaseDataStore):
    def __init__(
        self,
        metric: Metric,
        plot_dir: str,
        store_png: bool = False,
    ) -> None:
        super().__init__(metric, plot_dir, store_png)
        assert (
            metric.plot_type == PlotType.CDF or metric.plot_type == PlotType.HISTOGRAM
        )

        self.value_multiplier: float = 1.0

    def set_value_multiplier(self, value_multiplier: float) -> None:
        self.value_multiplier = value_multiplier

    @abstractmethod
    def to_series(self) -> pd.Series:
        pass

    @abstractmethod
    def put(self, label: str, value: float) -> None:
        pass

    def plot(self) -> None:
        data_series = self.to_series()

        Plotter.print_stats(data_series, self.metric.name)

        if self.metric.plot_type == PlotType.CDF:
            Plotter.plot_cdf(
                data_series,
                metric_name=self.metric.name,
                metric_unit=unit_type_to_string(self.metric.unit),
                plot_dir=self.plot_dir,
                store_png=self.store_png,
            )
        else:
            Plotter.plot_histogram(
                data_series,
                metric_name=self.metric.name,
                metric_unit=unit_type_to_string(self.metric.unit),
                plot_dir=self.plot_dir,
                store_png=self.store_png,
            )
