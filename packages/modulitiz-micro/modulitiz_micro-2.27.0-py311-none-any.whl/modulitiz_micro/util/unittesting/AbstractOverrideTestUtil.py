from abc import ABC


class AbstractOverrideTestUtil(ABC):
	"""
	Solo le funzioni statiche devono essere revertate
	"""
	
	def __init__(self):
		super().__init__()
		self._cache={}
	
	def __enter__(self):
		self._cache.clear()
		return self
	
	def __exit__(self,*args,**kwargs):
		self._cache.clear()
