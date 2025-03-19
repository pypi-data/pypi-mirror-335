import torch
import numpy as np
from typing import Tuple, Mapping, List
from torch.utils.data import Dataset

class BertDataset(Dataset):
	""" 配合BertCollator使用 """

	def __init__(self, tokenizies: Mapping[str, torch.Tensor], labels: np.ndarray):
		super().__init__()
		self.tokenizies = tokenizies
		self.labels = labels

	def __getitem__(self, index: int) -> Tuple[Mapping[str, torch.Tensor], torch.Tensor]:
		return {k: v[index] for k, v in self.tokenizies.items()}, self.labels[index]

	def __len__(self):
		return len(self.labels)
	

class HuggingFaceDataset(Dataset):
	""" 配合HuggingFace的Dataset使用 """

	def __init__(self, dataset, feature_names: List[str], label_name: str):
		"""
		return_type: auto, tuple, dict
		"""
		super().__init__()
		self.dataset = dataset
		self.feature_names = feature_names
		self.label_name = label_name

	def __getitem__(self, index: int):
		data = self.dataset[index]
		return [data[k] for k in self.feature_names], data[self.label_name]
		
	def __len__(self):
		return len(self.dataset)
		