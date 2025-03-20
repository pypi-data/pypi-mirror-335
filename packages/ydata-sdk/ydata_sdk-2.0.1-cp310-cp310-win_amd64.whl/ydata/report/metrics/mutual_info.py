import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import expit
from seaborn import heatmap
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

from ydata.report.metrics import MetricType
from ydata.report.metrics.base_metric import BaseMetric
from ydata.report.metrics.utils import get_categorical_vars, get_numerical_vars
from ydata.report.style_guide import FIG_SIZE, TITLE_FONT_NOTEBOOK, YDATA_HEATMAP_CMAP
from ydata.report.styles import StyleHTML


class MutualInformationMatrix(BaseMetric):
    def __init__(self, formatter=StyleHTML, include_plots: bool = True) -> None:
        super().__init__(formatter)
        self._include_plots = include_plots
        self._NUMBER_COLUMNS_TO_KEEP = 5

    @property
    def name(self) -> str:
        return "Mutual Information"

    @property
    def type(self) -> MetricType:
        return MetricType.VISUAL

    @staticmethod
    def _get_description(formatter):
        return f"{formatter.bold('MUTUAL INFORMATION (MI)')} measures how much information \
            can be obtained about one feature by observing another. This metric calculates \
            the similarity between real and synthetic MI values for each pair of features. \
            It returns values between [0, 1], where closer to 1 is desirable (i.e., equal MI)."

    @staticmethod
    def get_heatmap(df, title=None):
        mask = np.triu(np.ones_like(df, dtype=bool), k=1)
        fig1, ax1 = plt.subplots(figsize=FIG_SIZE)
        heatmap(
            data=df,
            vmin=0,
            vmax=1,
            annot=True,
            mask=mask,
            fmt=".2f",
            cmap=YDATA_HEATMAP_CMAP,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.5},
            annot_kws={"size": 20},
            ax=ax1,
        )
        if title is not None:
            ax1.set_title(title, **TITLE_FONT_NOTEBOOK)
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=-45)
        ax1.set_yticklabels(ax1.get_yticklabels(), rotation=45)
        return fig1.axes[0]

    @staticmethod
    def _get_top_k_columns(values, k):
        top_k_columns = []
        for col in values:
            if col not in top_k_columns:
                top_k_columns.append(col)
                if len(top_k_columns) == k:
                    return top_k_columns
        return top_k_columns

    @staticmethod
    def _ensure_data_has_same_shape(source: pd.DataFrame, synthetic: pd.DataFrame):
        if source.shape[0] != synthetic.shape[0]:
            min_rows = min(source.shape[0], synthetic.shape[0])
            if synthetic.shape[0] > min_rows:
                synthetic = synthetic.sample(n=min_rows)
            else:
                source = source.sample(n=min_rows)

        return source, synthetic

    @staticmethod
    def _calculate_mi_matrix(source: pd.DataFrame, synthetic: pd.DataFrame,
                             numerical_vars: list, categorical_vars: list):
        columns = numerical_vars + categorical_vars
        mi_matrix = pd.DataFrame()

        for ix1 in range(len(columns)):
            col1 = columns[ix1]
            mi_vals = {}
            for ix2 in range(ix1):
                col2 = columns[ix2]
                mi_vals[col2] = mi_matrix.loc[col2, col1]

            for ix2 in range(ix1, len(columns)):
                col2 = columns[ix2]
                compare_mi_vals = []
                for datasource in [source, synthetic]:
                    col1_data = datasource[col1].values
                    col2_data = datasource[col2].values
                    cardinality_col1 = datasource[col1].nunique()
                    cardinality_col2 = datasource[col2].nunique()
                    if (col1 in categorical_vars and cardinality_col1 == col1_data.shape[0]) \
                            or (col2 in categorical_vars and cardinality_col2 == col2_data.shape[0]):
                        # If a categorical feature has only unique values, the MI is 0.
                        mi = [0.0]
                    else:
                        try:
                            if col1 in categorical_vars and col2 in categorical_vars:
                                mi = mutual_info_classif(col1_data.reshape(-1, 1),
                                                         col2_data, discrete_features=[True])
                            elif col1 in numerical_vars and col2 in categorical_vars:
                                mi = mutual_info_classif(col1_data.reshape(-1, 1),
                                                         col2_data, discrete_features=[False])
                            elif col1 in categorical_vars and col2 in numerical_vars:
                                mi = mutual_info_classif(col2_data.reshape(-1, 1),
                                                         col1_data, discrete_features=[False])
                            elif col1 in numerical_vars and col2 in numerical_vars:
                                mi = mutual_info_regression(col1_data.reshape(-1, 1),
                                                            col2_data, discrete_features=[False])
                        except ValueError:  # Raise by sklearn when there is not enough neighbors
                            mi = [0.0]
                    # Since all MI values have a [0, +Inf] domain, the Sigmoid
                    # output domain is always [0.5, 1]. Therefore, this domain
                    # must be changed to [0, 1].
                    compare_mi_vals.append((expit(mi[0]) - 0.5) / 0.5)
                mi_vals[col2] = np.abs(compare_mi_vals[0] - compare_mi_vals[1])
            mi_matrix = pd.concat(
                [mi_matrix, pd.Series(mi_vals, name=col1).to_frame().T])

        return 1.0 - mi_matrix

    def _evaluate(self, source: pd.DataFrame, synthetic: pd.DataFrame, **kwargs):
        categorical_vars = get_categorical_vars(source, kwargs["metadata"])
        numerical_vars = get_numerical_vars(source, kwargs["metadata"])
        source_proc = source.copy()
        synthetic_proc = synthetic.copy()

        source_proc, synthetic_proc = \
            self._ensure_data_has_same_shape(
                source=source_proc, synthetic=synthetic_proc)

        mi_matrix = self._calculate_mi_matrix(source=source_proc, synthetic=synthetic_proc,
                                              numerical_vars=numerical_vars, categorical_vars=categorical_vars)

        ordered_mi_columns = [col for pair_cols
                              in list(mi_matrix.stack().sort_values(ascending=False).index)
                              for col in pair_cols]
        top_k_columns = self._get_top_k_columns(
            ordered_mi_columns, self._NUMBER_COLUMNS_TO_KEEP)
        bottom_k_columns = self._get_top_k_columns(
            reversed(ordered_mi_columns), self._NUMBER_COLUMNS_TO_KEEP)
        top_k_mi_matrix = mi_matrix[mi_matrix.index.isin(
            top_k_columns)][sorted(top_k_columns)].sort_index()
        bottom_k_mi_matrix = mi_matrix[mi_matrix.index.isin(
            bottom_k_columns)][sorted(bottom_k_columns)].sort_index()

        results = {
            "mean": mi_matrix.stack().mean(),
            "matrix_top_k_cols": top_k_mi_matrix,
            "matrix_bottom_k_cols": bottom_k_mi_matrix
        }

        if self._include_plots:
            results["chart_top_k_cols"] = self.get_heatmap(
                top_k_mi_matrix, title="Mutual Information - Highest Values")
            results["chart_bottom_k_cols"] = self.get_heatmap(
                bottom_k_mi_matrix, title="Mutual Information - Lowest Values")
            results["title"] = self.name
            results["description"] = self._description

        return results
