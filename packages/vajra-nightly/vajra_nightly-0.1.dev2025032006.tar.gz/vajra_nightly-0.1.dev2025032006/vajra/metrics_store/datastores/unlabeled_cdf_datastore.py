import numpy as np
import pandas as pd

from vajra._native.metrics_store import (
    Metric,
)
from vajra._native.metrics_store import (
    UnlabeledCdfDataStore as NativeUnlabeledCdfDataStore,
)

from ..datastores.base_cdf_datastore import BaseCDFDataStore
from ..datastores.base_datastore import BaseDataStore

SKETCH_RELATIVE_ACCURACY = 0.001
SKETCH_NUM_QUANTILES_IN_DF = 101


class UnlabeledCDFDataStore(BaseCDFDataStore):

    def __init__(
        self,
        metric: Metric,
        plot_dir: str,
        store_png: bool = False,
    ) -> None:
        super().__init__(metric, plot_dir, store_png)

        assert not metric.requires_label

        # Use the native C++ implementation
        self.sketch = NativeUnlabeledCdfDataStore(
            relative_accuracy=SKETCH_RELATIVE_ACCURACY
        )

    def sum(self) -> float:
        return self.sketch.sum()

    def __len__(self):
        return int(self.sketch.count())

    def merge(self, other: BaseDataStore) -> None:
        assert isinstance(other, UnlabeledCDFDataStore)
        assert self == other

        self.sketch.merge(other.sketch)

    def put(self, label: str, value: float) -> None:
        self.sketch.put(value)

    def to_series(self) -> pd.Series:
        # Check if sketch is empty
        if self.sketch.count() == 0:
            # Return an empty series to avoid potential issues
            return pd.Series(name=self.metric.name)

        # get quantiles at 1% intervals
        quantiles = np.linspace(0, 1, num=SKETCH_NUM_QUANTILES_IN_DF)
        # get quantile values
        quantile_values = [self.sketch.get_quantile_value(q) for q in quantiles]
        # create dataframe
        series = pd.Series(quantile_values, name=self.metric.name)

        series *= self.value_multiplier

        return series

    def to_df(self) -> pd.DataFrame:
        return self.to_series().to_frame()
