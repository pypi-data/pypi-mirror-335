from typing import List
from collections import defaultdict
import numpy as np
import torch

from model_wrapper.utils import is_float


class ListTensorCollator:
    """可以有多列数据
    配合ListDataset使用
    返回的是Tuple[Tensor]
    """

    def __init__(self, *dtypes: torch.dtype):
        if dtypes:
            self.dtypes = (
                dtypes[0]
                if len(dtypes) == 1 and isinstance(dtypes[0], (tuple, list))
                else dtypes
            )
        else:
            self.dtypes = None

    def __call__(self, batch):
        batch = (x for x in zip(*batch))
        if self.dtypes:
            return tuple(
                torch.tensor(x, dtype=self.dtypes[i]) for i, x in enumerate(batch)
            )

        return tuple(
            torch.tensor(
                x if isinstance(x, np.ndarray) else np.array(x),
                dtype=torch.float if is_float(x[0]) else torch.long,
            )
            for x in batch
        )


class DictTensorCollator:
    """出入的是List[Dict], 返回的是Dict[str, Tensor]"""

    def __call__(self, batch: List[dict]):
        keys = batch[0].keys()
        result = defaultdict(list)
        for data in batch:
            for k in keys:
                result[k].append(data[k])

        return {
            k: torch.tensor(
                np.array(v), dtype=torch.float if is_float(v[0]) else torch.long
            )
            for k, v in result.items()
        }


if __name__ == "__main__":
    # 示例数据
    batch = [
        {"a": 1.0, "b": 2, "c": 3},
        {"a": 4, "b": 5, "c": 6},
        {"a": 7, "b": 8, "c": 9},
    ]
    collator = DictTensorCollator()
    result = collator(batch)
    print(result)
