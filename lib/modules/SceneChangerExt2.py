log = op.LOGGER
class SceneChangerExt:
	"""
	SceneChangerExt is the extension for the SceneChanger custom component
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.scenesComp = self.ownerComp.par.Scenescomp.eval()
		self.sceneSelectComp = self.ownerComp.op('sceneSelect')
		self.sceneTogglePar = self.sceneSelectComp.par.Toggleabba
		self.sceneOrderDat = self.ownerComp.op('scenes')
		self.ab = ['a', 'b']
		

	@property
	def MenuTable(self):
		return self.ownerComp.op('selectMenu')

	@property
	def ScenesList(self):
		return [c.val for c in self.MenuTable.col('name')[1:]]

	@property
	def Current(self):
		return op(self.ownerComp.par.Scenescomp.eval()).op(self.ownerComp.par.Currentscenename.eval())

	def Firescene(self):
		"""
		Handles the Firescene pulse parameter. Renamed from FireScene for parexec catchall
		"""
		try: 
			self.SceneChange(int(self.ownerComp.par.Nextscene.eval()), fadeTime = self.ownerComp.par.Fadetime.eval())
		except:
			self.SceneChange(self.NameToIndex(self.ownerComp.par.Nextscene.eval()), fadeTime = self.ownerComp.par.Fadetime.eval())



	def Firelastscene(self):
		self.ownerComp.par.Scene = self.ownerComp.par.Lastscenename.eval()
	# def FireScene(self):
	# 	"""
	# 	Handles the Firescene pulse parameter
	# 	"""
	# 	self.SceneChange(int(self.ownerComp.par.Nextscene), 
	# 							fadeTime = self.ownerComp.par.Fadetime.eval())
	def Firenextsceneindex(self):
		ownerComp = self.ownerComp
		ownerComp.par.Scene.val = \
				self.IndexToName((int(ownerComp.par.Scene) +1)%ownerComp.op('sceneIndex').numRows)
	def Fireprevsceneindex(self):
		ownerComp = self.ownerComp
		ownerComp.par.Scene.val = \
				self.IndexToName((int(ownerComp.par.Scene) -1)%ownerComp.op('sceneIndex').numRows)

	def Firerandomscene(self):
		ownerComp = self.ownerComp
		val = int(tdu.remap(tdu.rand(absTime.frame%10000 * ownerComp.par.Scene), \
					0, 1, 0, len(ownerComp.par.Scene.menuNames)-1))
		if val == self.ownerComp.par.Currentscene.eval():
			val = val +1
		self.ownerComp.par.Scene = self.IndexToName(val)

	def SceneChange(self, sceneIndexOrName, fadeTime=None, init=False):
		"""
		Changes scene based on index or scene component name
		"""
		
		if isinstance(sceneIndexOrName, int) and \
					self.ownerComp.par.Currentscene.eval() != sceneIndexOrName:
			#self.ownerComp.par.Scene = sceneIndexOrName
			self.SwitchToScene(sceneIndexOrName, fadeTime=fadeTime)
			index = sceneIndexOrName

		elif isinstance(sceneIndexOrName, int) and \
					self.ownerComp.par.Currentscene.eval() == sceneIndexOrName:
			index = None
			if hasattr(self.Current.par, 'Start'):
				self.Current.par.Start.pulse()
			pass
		else:
			if sceneIndexOrName in self.ScenesList:
				row = self.sceneOrderDat.row(sceneIndexOrName)
				if row:
					index = row[0].row-1
					#self.ownerComp.par.Scene = index
					self.SwitchToScene(index, fadeTime=fadeTime, init=init)
					if index == self.ownerComp.par.Currentscene.eval():
						if hasattr(self.Current.par, 'Start'):
							self.Current.par.Start.pulse()
				else:
					index = None
			else:
				debug(f"FAILED: invalid scene for call to SceneChange('{sceneIndexOrName}')")
				index = None
				pass
		return index



	def SwitchToScene(self, index, fadeTime=None, init=None):
		"""
		Controls scene change with fade 
		"""
		self.ownerComp.par.Lastscene = self.ownerComp.par.Currentscene.eval()
		self.ownerComp.par.Lastscenename = self.IndexToName(self.ownerComp.par.Currentscene.eval())
		toggleState = self.sceneTogglePar.eval()
		nextId = self.ab[1-toggleState]
		curId = self.ab[toggleState]
		nGateComp = self.ownerComp.op('./sceneGate'+str(index))
		cGateComp = getattr(self.sceneSelectComp.par, 'Scene'+curId).eval()
		if isinstance(nGateComp, COMP):
			try:
				nSceneComp = nGateComp.par.Scenecomp.eval()
				cSceneComp = cGateComp.par.Scenecomp.eval()
				getattr(self.sceneSelectComp.par,
										'Scene'+nextId).val = './' + nGateComp.name
				
				if fadeTime is None and hasattr(nSceneComp.par, 'Fadeintime'):
					nGateComp.par.Fadetime = nSceneComp.par.Fadeintime.eval()
				elif fadeTime != None:
					nGateComp.par.Fadetime = float(fadeTime)
				else:
					log.Error(nSceneComp.path + ' may not be a valid scene component. Please check compliance')
				if fadeTime is None and hasattr(cSceneComp.par, 'Fadeouttime'):
					cGateComp.par.Fadetime = cSceneComp.par.Fadeouttime.eval()
				else:
					cGateComp.par.Fadetime = fadeTime
				self.sceneTogglePar.val = 1-toggleState
				self.ownerComp.par.Currentscene = index
				self.ownerComp.par.Currentscenename = self.IndexToName(index)
				# drmbt callbacks method for init and start on scenes
				if init: op(self.ownerComp.par.Scenescomp).op(self.IndexToName(index)).par.Init.pulse()
				
				if self.ownerComp.par.Logdebug.eval():
					log.Info(f"SceneChanger | SwitchToScene(index={index}, fadeTime={fadeTime}): '{self.IndexToName(index)}'")
				try:
					op(self.ownerComp.par.Scenescomp).op(self.IndexToName(self.ownerComp.par.Lastscene.eval())).par.Exit.pulse()				
				except: pass
			except:
				log.Error(f"SceneChanger | FAILED: SwitchToScene(index={index}, fadeTime={fadeTime}): '{self.IndexToName(index)}'")
			
	def gateActivateOn(self, gateComp):
		"""
		Activates the gate and pulses the scene start 
		"""
		sceneComp = gateComp.par.Scenecomp.eval()
		if isinstance(sceneComp, COMP):
			if hasattr(sceneComp.par, 'Start'):
				sceneComp.par.Start.pulse()
				sceneComp.par.Play = True
	def gateActivateOff(self, gateComp):
		sceneComp = gateComp.par.Scenecomp.eval()
		if isinstance(sceneComp, COMP):
			if hasattr(sceneComp.par, 'Init'):
				sceneComp.par.Init.pulse()
				sceneComp.par.Play = False

	def GenerateUI(self):
		"""
		Generates a basic UI as a starting point to drive the scene changer system
		"""
		sceneChangerUi = self.ownerComp.parent().copy(self.ownerComp.op('sceneChangerUi'), name='sceneChangerUi', includeDocked=True)
		sceneChangerUi.allowCooking = sceneChangerUi.display = sceneChangerUi.par.display = True
		sceneChangerUi.par.Scenechanger = self.ownerComp
	
	def GenerateSceneTemplate(self):
		"""
		Generates a scene component that can be copied to the specified scenes component
		"""
		newScene = op(self.ownerComp.par.Scenescomp).copy(self.ownerComp.op('sceneTemplate'), name='sceneTemplate', includeDocked=False)
		newScene.tags = ['TDScene']
	def Reset(self):
		"""
		Resets the scene componoent
		"""
		# self.ownerComp.par.Resolutionw = 1920
		# self.ownerComp.par.Resolutionh = 1080
		self.ownerComp.par.Scenescomp.expr = "op.SCENES"
		
		self.ownerComp.par.Nextscene = 0
		self.ownerComp.par.Currentscene = 0

		self.ownerComp.par.Scenea = './sceneGate1'
		self.ownerComp.par.Sceneb = './sceneGate0'


	#drmbt methods
	def Updatemenu(self):
		updateList = ['Nextscene', 'Scene']
		namesList = self.ScenesList
		for par in updateList:
			try:
				self.ownerComp.par[par].menuNames = namesList
				self.ownerComp.par[par].menuLabels = namesList
			except:
				pass
	def NameToIndex(self, name):
		'''conversion method from name to sceneIndex'''
		if name in self.ScenesList:
			return self.ScenesList.index(name)

	def IndexToName(self, index):
		'''conversion method from sceneIndex to name'''
		if len(self.ScenesList) >= index:
			return self.ScenesList[index]