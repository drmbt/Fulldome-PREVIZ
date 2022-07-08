
from TDStoreTools import StorageManager
import TDFunctions as TDF
import os
from os import path
log = op.LOGGER
class ScenesExt:
	"""
	ScenesExt provides public methods for managing a pool of scenes based on 
	Jarrett's SceneChanger palette COMP. It is a part of the HIVE family of
	components and modules by [Vincent Naples](instagram.com/drmbt)
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
	@property
	def ScenesTable(self):
		return self.ownerComp.op('scenes')

	@property
	def ScenesList(self):
		return [c.val for c in self.ScenesTable.col('name')[1:]]


	def NameToIndex(self, name):
		'''conversion method from name to sceneIndex'''
		if name in self.ScenesList:
			return self.ScenesList.index(name)

	def IndexToName(self, index):
		'''conversion method from sceneIndex to name'''
		if len(self.ScenesList) >= index:
			return self.ScenesList[index]

	def Newscene(self, name=None):
		ownerComp = self.ownerComp
		if not name:
			def onSelect(info):
				"""A button has been pressed"""
				if info['button'] != "OK":
					return
				else:
					self.NewScene(name= info['enteredText'])

			op.TDTox.op('popDialog').Open(
				text = f'Create new scene:',
				title = 'Create TDSCene',
				buttons = ['OK', 'Cancel'],
				textEntry = True,
				callback = onSelect,)

	def NewScene(self, name):
		
		new = self.ownerComp.copy(self.ownerComp.op('sceneTemplate'))
		new.name=tdu.legalName(name)
		new.allowCooking = True
		new.tags = ['TDScene']
		if new.op('PresetSting'):
			new.op('PresetSting').tags = ['PresetSting']
		if new.op('FxSting'):
			new.op('FxSting').tags = ['FxSting']
		if new.op('IconSting'):
			new.op('IconSting').tags = ['IconSting']
			new.op('icon').tags = ['Icon']
		index = len(self.ownerComp.findChildren(depth=1, tags=['TDScene']))
		new.nodeY = index * -150
		if self.ownerComp.par.Logdebug:
			log.Info(f'SCENES | New Scene: "{new}" successfully created!')



	def DeleteScene(self, scenes):
		for scene in list(scenes):	
			if scene in self.ownerComp.op('scenes').col('name'):
				if self.ownerComp.op(scene):
					self.ownerComp.op(scene).destroy()
					self.ownerComp.op('scenes').deleteRow(scene)
					if self.ownerComp.par.Logdebug:
						log.Info(f'SCENES | Delete scene: "{scene}"')

	def DeleteAllScenes(self):
		confirm = ui.messageBox('Delete Confirmation',
				f'Are you sure you want to delete all scenes?',
				buttons=['OK', 'Cancel'])
		if confirm == 0:	
			ui.undo.startBlock('undo DeleteAllScenes()')
			for scene in self.ScenesList:
				self.ownerComp.op(scene).destroy()
			ui.undo.endBlock
			if self.ownerComp.par.Logdebug:
				log.Info(f'SCENES | Delete All Scenes')
		return

	def DuplicateScenes(self, scenes:list):
		for scene in scenes:
			new = self.ownerComp.copy(self.ownerComp.op(f'{scene}'))
			new.allowCooking = True
			index = len(self.ownerComp.findChildren(depth=1, tags=['TDScene']))
			new.nodeY = index * -150
			if self.ownerComp.par.Logdebug:
				log.Info(f'SCENES | Duplicated scene: "{scene}"')
	
	def Importscene(self):
		self.ImportScene()

	def ImportScene(self):
		filepath = ui.chooseFile(load=True, start='local/scenes', fileTypes=['tox'], title='Load TDScene .tox', asExpression=False)
		importTox = self.ownerComp.loadTox(filepath, unwired=True, pattern=None, password=None)
		importTox.allowCooking = True
		index = len(self.ownerComp.findChildren(depth=1, tags=['TDScene']))
		iomportTox.nodeY = index * -150
		
	def Exportallscenes(self):
		
		filePath = self.ownerComp.par.Scenesfolder.eval()
		scenes = self.ScenesList
		self.ExportScenes(scenes, filePath)
		return

	def ExportScenes(self, scenes:list=None, filePath=None):
		
		if not scenes: scenes = self.ScenesList
		if not filePath: filePath = self.ownerComp.par.Scenesfolder.eval()
		if filePath == '':
			filePath == 'local/scenes'
		for scene in scenes:
			if scene in self.ownerComp.op('scenes').col('name'):
				if self.ownerComp.op(scene):

					path = f"{filePath}/{scene}.tox"
					debug(scene, path)
					self.ownerComp.op(scene).save(path, createFolders=True)
					if self.ownerComp.par.Logdebug.eval():
						log.Info(f"Scenes | ExportScenes(): '{scene}' to {path}")

	def Initscenemenu(self):
		self.ScenesTable.clear(keepFirstRow=True)
		for scene in self.ownerComp.findChildren(depth=1, type=COMP, tags=['TDScene']):
			if scene.name not in ['sceneTemplate']:
				self.ScenesTable.appendRow([scene.name, scene.path])
				debug(scene)

	def Initscenes(self):
		"""method for playing all scenes once to load any assets required to play properly.
		can be set to happen on session start"""
		cur = op.SCENECHANGER.Current

		for r in range(1, self.ScenesTable.numRows):
			script =f"op('{op.SCENECHANGER}').SceneChange('{self.ScenesTable[r,0].val}', fadeTime=0)"
			run(script, delayFrames=r)

		script2 =f"op('{op.SCENECHANGER}').SceneChange('{cur}', fadeTime=0)"
		run(script2, delayFrames=self.ScenesTable.numRows+1)

	def Removemissing(self):
		ScenesList = [s.name for s in self.ownerComp.findChildren(depth=1, type=COMP, tags=['TDScene']) if s.name != 'sceneTemplate']
		for r in reversed(range(1, self.ScenesTable.numRows)):
			if not op(self.ScenesTable[r, 'name']):

			# if op(self.ScenesTable[r, 'name'].val).name not in ScenesList:
				self.ScenesTable.deleteRow(r)

	def Updatemenu(self):
		for scene in self.ownerComp.findChildren(depth=1, type=COMP, tags=['TDScene']):
			if scene.name not in ['sceneTemplate'] and scene.name not in self.ScenesTable.col('name')[1:]:
				self.ScenesTable.appendRow([scene.name, scene.path])
		self.Removemissing()

	def Collapsesting(self, Op=None):
		'''sting target Op with a Header per customPage named expand for UberGUI'''
		if not Op:	Op = self.ownerComp.par.Op.eval()
		pageList = [p for p in Op.customPages]
		for n in pageList:
			legalName = tdu.legalName(n.name)
			legalName = legalName.replace('_', '')
			n.name = legalName
		newPageList = [p for p in Op.customPages]
		for n in newPageList:
			pName = n.name
			pCap = pName.capitalize() + 'expand'
			label = pName + '>'
			page = Op.appendCustomPage(pName)

			newTuplet = page.appendHeader(pCap, label=label, order=-1)
		if self.ownerComp.par.Logdebug:
			log.Info(f'SCENES | Collapsesting: {Op}')
	def Collapsestingall(self):
		for scene in self.ScenesList:
			self.Collapsesting(self.ownerComp.op(scene))
			if self.ownerComp.par.Logdebug:
				log.Info('SCENES | Collapsestingall()')

	def Iconstingall(self):

		i = 1
		for scene in self.ScenesList:
			i = i+120
			run("project.realTime=False", delayFrames=i)
			run(f"op.SCENECHANGER.SceneChange('{scene}', fadeTime={float(0.1)}, init=True, start=True)",delayFrames=i+1)
			run(f"op.ICONSTINGER.Sting(op('{self.ownerComp.op(scene)}'))", delayFrames = i+60)
			run("project.realTime=False", delayFrames=i + (i-1))
	def Iconunstingall(self):
		i = 1
		for scene in self.ScenesList:
			i = i
			try:
				#debug(f"op('{self.ownerComp.op(scene)}').op('IconSting').par.Unsting.pulse()")
				if self.ownerComp.op(scene).op('IconSting'):
					run(f"op('{self.ownerComp.op(scene)}').op('IconSting').par.Unsting.pulse()", delayFrames = i)
			except:
				pass 