import threading
from abc import ABC

from modulitiz_micro.ModuloStringhe import ModuloStringhe


class AbstractSql(ABC):
	def __init__(self):
		self.connDb=None
		self.lock=threading.Lock()
	
	def commit(self):
		with self.lock:
			self.commitNoLock()
	
	def commitNoLock(self):
		"""
		Da usare solo se il lock viene fatto esternamente
		"""
		self.connDb.commit()
	
	def rollback(self):
		with self.lock:
			self.connDb.rollback()
	
	def initCursore(self):
		with self.lock:
			cursoreDb=self.connDb.cursor()
		return cursoreDb
	
	def count(self,cursoreDb)->int:
		with cursoreDb:
			with self.lock:
				result=cursoreDb.fetchone()
		if not result:
			return 0
		return result[0]
	
	def close(self):
		with self.lock:
			if self.connDb is not None:
				self.connDb.close()
				self.connDb=None
	
	@staticmethod
	def ifEmptyThenNull(testo:str|None)->str|None:
		if ModuloStringhe.isEmpty(testo) or testo=="NULL":
			return None
		return testo
