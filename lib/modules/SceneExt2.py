"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
import TDFunctions as TDF
import sys
import inspect
log = op.LOGGER
class SceneExt:
	"""
	SceneExt description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.Init()
	#	self.Initdatatable()
		
		
		# properties
		TDF.createProperty(self, 'MyProperty', value=0, dependable=True,
					   readOnly=False)
	
		# attributes:
		self.a = 0 # attribute
		self.B = 1 # promoted attribute

		# stored items (persistent across saves and re-initialization):
		storedItems = [
			# Only 'name' is required...
			{'name': 'StoredProperty', 'default': None, 'readOnly': False,
			 						'property': True, 'dependable': True},
		]
		# Uncomment the line below to store StoredProperty. To clear stored
		# 	items, use the Storage section of the Component Editor
		
		# self.stored = StorageManager(self, ownerComp, storedItems)
	@property
	def Active(self):
		return self.ownerComp.par.Active.eval()

	@Active.setter
	def Active(self, val):
		me.par.Active = val

	@property
	def DataTable(self):
		return self.ownerComp.op('table_data')

# callbacks passthru
	def Init(self):
		mod.callbacks.onInit(None)
		return

	def Start(self):
		script = f"ext.CallbacksExt.DoCallback('onStart', None)"
		run(script)
		return
	
	def Exit(self):
		script = f"ext.CallbacksExt.DoCallback('onExit', None)"
		run(script)
		return
		
	def Done(self):
		script = f"ext.CallbacksExt.DoCallback('onDone', None)"
		run(script)
		return

	def Play(self):
	#	self.ownerComp.op('switch1').par.index = self.ownerComp.par.Play.eval()
	# 	if not self.ownerComp.par.Play.eval():
	# 		script = self.Exit()
	# 	else:
	# 		script = self.Start()
	# 	run(script)

		return

	def Editcallbacks(self):
		op(self.ownerComp.par.Callbackdat).par.edit.pulse()

# utility
	def Initdatatable(self):

		table = self.DataTable
		table.clear(keepFirstRow=True)
		table.appendRow(['Play', 0])
		chop = self.ownerComp.op('null_data')
		for r in range(chop.numChans):
			if chop[r].name != 'Play':
				table.appendRow([chop[r].name, chop[r]])
		if self.ownerComp.par.Logdebug.eval():
			log.Debug(f"SceneExt	| Initdatatable()	'{self.ownerComp}'")
		return

	def File(self, par, val, prev):
		self.ownerComp.par.Initinfo.pulse()

# sting functionality
	def Collapsesting(self):
		'''sting target Op with a Header per customPage named expand for UberGUI'''
		Op = self.ownerComp
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

	def Fxsting(self):
		if hasattr(op, 'FXSTINGER'): op.FXSTINGER.Sting(self.ownerComp)
	def Presetsting(self):
		if hasattr(op, 'PRESETSTINGER'):
			op.PRESETSTINGER.Sting(self.ownerComp)
	def Iconsting(self):
		if hasattr(op, 'ICONSTINGER'):
			op.ICONSTINGER.Sting(self.ownerComp, self.ownerComp)


# parexec_passThru callbacks
	def onParValueChange(self, par=None, val=None, prev=None):
		"""panelexec_passThru value change callbacks to condense logic to ext"""
		if hasattr(self, par.name):
			try:
				getattr(self, par.name)()
			except Exception as e:
				pass
	def onParPulse(self, par=None, val=None):
		"""panelexec_passThru pulse callbacks to condense logic to ext"""
		ownerComp = self.ownerComp
		if par.name == 'Help':
			print(help(self))
		if hasattr(self, par.name):
			try:
				getattr(ownerComp, par.name)()
			except Exception as e:
				pass
# end region
	def Test(self, str='Test'):
		debug(str) 