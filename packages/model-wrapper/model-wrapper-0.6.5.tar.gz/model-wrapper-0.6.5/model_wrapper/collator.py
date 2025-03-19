import torch
import numpy as np

from model_wrapper.utils import is_float


class ListTensorCollator:
	""" 可以有多列数据 
	配合ListDataset使用
	"""
	
	def __init__(self, *dtypes: torch.dtype):
		if dtypes:
			self.dtypes = dtypes[0] if len(dtypes) == 1 and isinstance(dtypes[0], (tuple, list)) else dtypes
		else:
			self.dtypes = None
	
	def __call__(self, batch):
		batch = (x for x in zip(*batch))
		if self.dtypes:
			return tuple(torch.tensor(x, dtype=self.dtypes[i]) for i, x in enumerate(batch))
		
		return tuple(torch.tensor(x if isinstance(x, np.ndarray) else np.array(x), dtype=torch.float if is_float(x[0]) else torch.long) for x in batch)
