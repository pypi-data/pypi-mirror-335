import git


class ModuloGit(object):
	def __init__(self, repoPath:str):
		self.inner=git.Repo(repoPath)
	
	def getWorkingCopyRevision(self)->str:
		return self.inner.head.object.hexsha
	
	def getRemoteRevision(self)->str:
		return self.inner.remotes[0].fetch()[0].ref.object.hexsha
	
	def update(self)->str:
		return self.inner.remotes[0].pull()[0].ref.object.hexsha
