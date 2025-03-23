import os
import shutil

from modulitiz_micro.ModuloColorText import ModuloColorText
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.files.ModuloFiles import ModuloFiles
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem
from modulitiz_micro.util.wheel.ModuloToml import ModuloToml
from modulitiz_micro.files.git.ModuloGit import ModuloGit


class ModuloBuildWheel(object):
	CMD_PYTHON="python"
	PATTERN_NOMEFILE_WHEEL="{}-{}-{}-none-any.whl"
	MAX_VERSION_TO_KEEP=10
	
	def __init__(self,nomeModulo:str,percorsoFileMain:str):
		self.nomeModulo=nomeModulo
		self.nomeModuloNormalizzato=nomeModulo.replace("_","-")
		
		self.percorsoCartellaSource=os.path.dirname(percorsoFileMain)
		self.percorsoCartellaRoot=os.path.dirname(self.percorsoCartellaSource)
		self.git=ModuloGit(os.path.dirname(self.percorsoCartellaRoot))
		self.skipUnitTest=False
		
		self.moduloToml=ModuloToml("pyproject.toml")
		self.versionOld=None
		self.versionNew=None
		self.nomefileWheel=None
	
	def doWork(self):
		self.versionOld=self.moduloToml.retrieveVersion()
		self.skipUnitTest=input("Skip unit test? y, n (default = n):")=='y'
		# chiedo quale versione aumentare (major, minor, bug fix)
		tipoVersione=input("Which version increment? 1=major, 2=minor, 3=bug fix (default = 2):")
		if tipoVersione=="":
			tipoVersione=2
		else:
			tipoVersione=int(tipoVersione)
		# calcolo la prossima versione
		self.__computeVersionNew(tipoVersione)
		# stampo info
		msg=f"Build {self.nomeModulo} {self.versionNew}"
		ModuloSystem.setTitoloFinestra(msg)
		print("""{}
		============================================================
				{} (from version {})
		============================================================
		{}""".format(ModuloColorText.GRASSETTO,msg,self.versionOld,ModuloColorText.DEFAULT))
		# cambio cartella
		os.chdir(self.percorsoCartellaSource)
		if self.__doUnitTests() is True:
			return
		# aggiorno versione
		self.moduloToml.updateVersion(self.versionNew)
		# costruisco wheel
		ModuloSystem.systemCallPrintOutput(f'{self.CMD_PYTHON} -m pip install --upgrade build',None)
		print()
		percorsoCartellaOut=os.path.dirname(self.percorsoCartellaRoot)
		percorsoCartellaOut=ModuloFiles.pathJoin(ModuloFiles.pathJoin(percorsoCartellaOut,"wheels"),self.nomeModuloNormalizzato)
		cmd='{} -m build --wheel --outdir "{}"'.format(self.CMD_PYTHON,percorsoCartellaOut)
		ModuloSystem.systemCallPrintOutput(cmd,None)
		print()
		# cancello cartelle temporanee
		shutil.rmtree(ModuloFiles.pathJoin(self.percorsoCartellaSource,"build"))
		shutil.rmtree(ModuloFiles.pathJoin(self.percorsoCartellaSource,self.nomeModulo+".egg-info"))
		# installo wheel
		self.nomefileWheel=self.PATTERN_NOMEFILE_WHEEL.format(self.nomeModulo,self.versionNew,self.moduloToml.retrieveMinPyVersion())
		percorsoWheel=ModuloFiles.pathJoin(percorsoCartellaOut,self.nomefileWheel)
		cmd='{} -m pip install -U "{}"'.format(self.CMD_PYTHON,percorsoWheel)
		ModuloSystem.systemCallPrintOutput(cmd,None)
		print()
		# aggiungo il file al repo
		self.git.inner.index.add(percorsoWheel)
		# se presenti, cancello le versioni troppo vecchie
		print()
		oldFilenames=ModuloListe.humanOrder(os.listdir(percorsoCartellaOut))[:-self.MAX_VERSION_TO_KEEP]
		if len(oldFilenames)==0:
			return
		print("Cancello le versioni troppo vecchie:")
		for file in oldFilenames:
			deletedFilename=self.git.inner.index.remove(ModuloFiles.pathJoin(percorsoCartellaOut,file),working_tree=True)
			print("\n".join(deletedFilename))
	
	def __doUnitTests(self) -> bool:
		if self.skipUnitTest is True:
			return False
		nomefileTest=ModuloFiles.pathJoin(self.percorsoCartellaSource,"test/TestMain.py")
		print("Inizio test...")
		cmd='%s "%s"'%(self.CMD_PYTHON,nomefileTest)
		righe=[]
		for riga in ModuloSystem.systemCallYieldOutput(cmd,None):
			print("%s>>>%s %s"%(ModuloColorText.BLU,ModuloColorText.DEFAULT,riga))
			righe.append(riga)
		righe=reversed(righe[-10:])
		righe=[x.strip() for x in righe]
		righe=[x if x!="" and x!=ModuloColorText.DEFAULT else None for x in righe]
		righe=ModuloListe.eliminaElementiVuoti(righe)
		ultimaRiga=righe[0]
		PATTERN_TO_PRINT="""{}
	==================================================
			{}
	==================================================
	"""+ModuloColorText.DEFAULT
		if ultimaRiga!="OK":
			print(PATTERN_TO_PRINT.format(ModuloColorText.ROSSO,"ERRORE nei test"))
			return True
		print(PATTERN_TO_PRINT.format(ModuloColorText.VERDE,"test completati con successo"))
		return False
	
	def __computeVersionNew(self,tipoVersione:int):
		arr=[int(x) for x in self.versionOld.split(".")]
		arr[tipoVersione-1]+=1
		if tipoVersione!=len(arr):
			for i in range(tipoVersione,len(arr)):
				arr[i]=0
		arr=[str(x) for x in arr]
		self.versionNew=".".join(arr)
