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

	def Scene(self, par, val, prev):
		self.SceneChange(par, fadeTime = self.ownerComp.par.Fadetime.eval())

	def Viewsceneindex(self):
		self.ownerComp.op('sceneIndex').openViewer()

	def Generateui(self):
		self.GenerateUI()	

	def Generatescenetemplate(self):
		self.GenerateSceneTemplate()

	def Firescene(self):
		self.ownerComp.par.Scene = self.ownerComp.par.Nextscene

	def Firelastscene(self):
		self.ownerComp.par.Scene = self.ownerComp.par.Lastscene.eval()
	# def FireScene(self):
	# 	"""
	# 	Handles the Firescene pulse parameter
	# 	"""
	# 	self.SceneChange(int(self.ownerComp.par.Nextscene), 
	# 							fadeTime = self.ownerComp.par.Fadetime.eval())
	def Firenextsceneindex(self):
		ownerComp = self.ownerComp
		ownerComp.par.Scene.val = \
				(int(ownerComp.par.Scene) +1)%ownerComp.op('sceneIndex').numRows
	def Fireprevsceneindex(self):
		ownerComp = self.ownerComp
		ownerComp.par.Scene.val = \
				(int(ownerComp.par.Scene)-1)%op('sceneIndex').numRows

	def Firerandomscene(self):
		ownerComp = self.ownerComp
		val = int(tdu.remap(tdu.rand(absTime.frame%10000 * ownerComp.par.Scene), \
					0, 1, 0, len(ownerComp.par.Scene.menuNames)))
		if ownerComp.par.Scene.val == val:
			ownerComp.par.Scene.val = (ownerComp.par.Scene.val +2)%len(ownerComp.par.Scene.menuNames)
		else:
			ownerComp.par.Scene.val == ownerComp.par.Scene.menuNames[val]

	def Currentscene(self, par, val, prev):
		debug('currentscene')
		self.ownerComp.par.Scene.val = 	par.val		

	def SceneChange(self, sceneIndexOrName, fadeTime=None):
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
			pass
		else:
			row = self.sceneOrderDat.row(sceneIndexOrName)
			if row:
				index = row[0].row
				#self.ownerComp.par.Scene = index
				self.SwitchToScene(index, fadeTime=fadeTime)
			else:
				index = None
		return index

	def SwitchToScene(self, index, fadeTime=None):
		"""
		Controls scene change with fade 
		"""
		toggleState = self.sceneTogglePar.eval()
		nextId = self.ab[1-toggleState]
		curId = self.ab[toggleState]
		nGateComp = self.ownerComp.op('./sceneGate'+str(index))
		cGateComp = getattr(self.sceneSelectComp.par, 'Scene'+curId).eval()
		if isinstance(nGateComp, COMP):
			nSceneComp = nGateComp.par.Scenecomp.eval()
			cSceneComp = cGateComp.par.Scenecomp.eval()
			getattr(self.sceneSelectComp.par,
									'Scene'+nextId).val = './' + nGateComp.name
			
			if fadeTime is None and hasattr(nSceneComp.par, 'Fadeintime'):
				nGateComp.par.Fadetime = nSceneComp.par.Fadeintime.eval()
			elif fadeTime:
				nGateComp.par.Fadetime = fadeTime
			else:
				debug(nSceneComp.path + ' may not be a valid scene component. Please check compliance')
			if fadeTime is None and hasattr(cSceneComp.par, 'Fadeouttime'):
				cGateComp.par.Fadetime = cSceneComp.par.Fadeouttime.eval()
			else:
				 cGateComp.par.Fadetime = fadeTime
			self.sceneTogglePar.val = 1-toggleState
			self.ownerComp.par.Lastscene = self.ownerComp.par.Currentscene 
			self.ownerComp.par.Currentscene = index
			
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
		self.ownerComp.parent().copy(self.ownerComp.op('sceneTemplate'), name='sceneTemplate', includeDocked=True)

	def Reset(self):
		"""
		Resets the scene componoent
		"""
		self.ownerComp.par.Resolutionw = 1280
		self.ownerComp.par.Resolutionh = 720
		self.ownerComp.par.Scenescomp = ''
		
		self.ownerComp.par.Nextscene = 0
		self.ownerComp.par.Currentscene = 0

		self.ownerComp.par.Scenea = './sceneGate1'
		self.ownerComp.par.Sceneb = './sceneGate0'



		