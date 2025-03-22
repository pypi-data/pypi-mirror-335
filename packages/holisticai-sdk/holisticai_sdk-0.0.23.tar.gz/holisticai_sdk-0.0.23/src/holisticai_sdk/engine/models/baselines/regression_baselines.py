from __future__ import annotations

from typing import TYPE_CHECKING

from sklearn.linear_model import LinearRegression, Ridge

from holisticai_sdk.engine.definitions import HAIModel, HAIRegression


if TYPE_CHECKING:
    import pandas as pd
    from numpy.typing import ArrayLike


def linear_regression_baseline(x: pd.DataFrame, y: ArrayLike):
    lr = LinearRegression()

    lr.fit(X=x, y=y)

    return HAIRegression(predict=lr.predict, name="Linear Regression")



def ridge_baseline(x: pd.DataFrame, y: ArrayLike):
    ridge = Ridge()
    ridge.fit(X=x, y=y)

    return HAIRegression(predict=ridge.predict, name="Ridge")



def get_regression_baselines(x: pd.DataFrame, y: ArrayLike) -> list[HAIModel[HAIRegression]]:
    baselines = [linear_regression_baseline, ridge_baseline]


    return [baseline(x=x, y=y) for baseline in baselines]
