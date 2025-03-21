from typing import Union, List, Dict

from PIL.Image import Image
from langchain_voyageai import VoyageAIEmbeddings


class EnhancedVoyageAIEmbeddings(VoyageAIEmbeddings):
	def embed_multimodal_documents(
		self,
		inputs: Union[List[Dict], List[List[Union[str, Image]]]]
	) -> List[List[float]]:
		"""Embed query text and image"""
		embeddings: List[List[float]] = []

		_iter = self._get_batch_iterator(inputs)
		for i in _iter:
			embeddings.extend(
				self._client.multimodal_embed(
					inputs=inputs[i:i+self.batch_size],
					model=self.model,
					input_type='document',
					truncation=True
				).embeddings
			)

		return embeddings

	def embed_multimodal_queries(
		self,
		inputs: Union[List[Dict], List[List[Union[str, Image]]]]
	) -> List[List[float]]:
		return self._client.multimodal_embed(
			inputs=inputs,
			model=self.model,
			input_type='query',
			truncation=True
		).embeddings