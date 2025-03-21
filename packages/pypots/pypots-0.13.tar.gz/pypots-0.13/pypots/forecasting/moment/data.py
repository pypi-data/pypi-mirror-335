"""
Dataset class for the forecasting model MOMENT.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from typing import Union

from ...data.dataset import BaseDataset


class DatasetForMOMENT(BaseDataset):
    """Dataset for MOMENT forecasting model."""

    def __init__(
        self,
        data: Union[dict, str],
        return_X_pred=True,
        file_type: str = "hdf5",
    ):
        super().__init__(
            data=data,
            return_X_ori=False,
            return_X_pred=return_X_pred,
            return_y=False,
            file_type=file_type,
        )
