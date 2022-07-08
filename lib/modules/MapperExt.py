"""
	HIVE
	========
	
	Copyright (c) 2021 [Drmbt](https://github.com/drmbt)
	[Vincent Naples](mailto:vincent@drmbt.com)
	[drmbt.com](https://www.drmbt.com)	

	This file is part of HIVE.

	HIVE is a family of global components and ui elements that become
	more powerful when they interface together. HIVE is powerful, dangerous, 
	and	quite possibly full of bugs.

    As this primarily exists as a personal tool and study of TouchDesigner, git,
	Python, and general UI/UX design, it is in this form being distributed in
	hope that others may find it useful, but WITHOUT ANY WARRANTY; without even 
	the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

	I'm releasing it in this form under the [MIT license](https://www.mit.edu/~amini/LICENSE.md)
	in hopes that it might find some use in the TouchDesigner community.

	Version: 001.2021.001.11Apr
"""

from TDStoreTools import StorageManager
import TDFunctions as TDF
import string

class Mapper:
	"""
	MapperExt description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp 			= ownerComp
		self.ownerComp.op('importProxy').clear(keepFirstRow=True)
	@property
	def Name(self):
		return self.ownerComp.name

	@property
	def Table(self):
		return op('MappingsTable')
	@property
	def Learnmode(self):
		return self.ownerComp.par.Learnmode.eval()

	@property
	def Learn(self):
		return self.ownerComp.par.Learn.eval()
	
	@Learn.setter
	def Learn(self, v):
		self.ownerComp.par.Learn = v


	
	def Learn(self, val):
		cr = self.ownerComp.par.Learnparbgcolorr.val
		cg = self.ownerComp.par.Learnparbgcolorg.val
		cb = self.ownerComp.par.Learnparbgcolorb.val

		self.ownerComp.op('activeMarker').bypass = not val

		if val:
			ui.colors['parms.dialog.bg'] = [cr, cg, cb]

		else:
			ui.colors['parms.dialog.bg'] = [.25, .25, .25]
			self.ClearLearnTarget()

		return

	def Parse(self, chanName, val):
		controller		= self.Table.col('controller')
		if chanName in controller:
			for r in self.Table.rows(chanName):

				row 	= r[0].row
				missing	= self.Table[row, 'Missing']
				target 	= self.Table[row, 'path'].val
				Par		= self.Table[row, 'parameter'].val
				minmax	= (float(self.Table[row, 'min']), float(self.Table[row, 'max']))
				toggle	= self.Table[row, 'Toggle']

				if self.Table[row, 'Invert']:
					minmax = minmax[::-1]

				v		= tdu.remap(float(val), 0, 1, minmax[0], minmax[1])

				if op(target):
					self.Table[row, 'Missing'] = 0
					try:
						if not toggle:
							op(target).par[Par] = v

						elif toggle and val == 1:
							if op(target).par[Par] == minmax[0]:
								op(target).par[Par] = minmax[1]
							else:
								op(target).par[Par] = minmax[0]
						if op(target).par[Par].style == 'Pulse' and val == 1:
							op(target).par[Par].pulse()
							debug('pulse')
					except:
						pass
				else:
					self.Table[row, 'Missing'] = 1
					pass

	def Map(self, chanName=''):
		"""
		Map a CHOP channel to current Learn Parameter
		"""
		
		ownerComp	= self.ownerComp
		p			= ownerComp.par	
		if chanName:
			p.Learncontroller = chanName
		controller	= p.Learncontroller
		if self.Learnmode == 'Mappings Table':
			if controller and p.Learnparameter and p.Learnpath:
				try:
					debug(p.Learnparameter.style)
					op(self.Table).appendRow([
						controller,										# controller
						p.Learnparameter,								# parameter
						op(p.Learnpath).name,							# name
						p.Learnpath,									# path
						op(p.Learnpath).par[p.Learnparameter].normMin,	# min
						op(p.Learnpath).par[p.Learnparameter].normMax if op(p.Learnpath).par[p.Learnparameter].style not in ['Menu', 'StrMenu'] else len(op(p.Learnpath).par[p.Learnparameter].menuNames),	# max
						0,												# Invert
						0												# Toggle
											])
					debug(f'"{controller}" assigned to {p.Learnpath}[{p.Learnparameter}]')
					self.ClearLearnTarget()
					ui.colors['parms.dialog.bg'] = [.8, .8, .8]
					op('uiScript').run(delayFrames=10)
					
				except Exception as e:
					debug(e)
			else:
				print(f'Mapper Controller, Parameter or Path argument missing')
	
		elif self.Learnmode == 'Reference':
			try:
				refPath = op(self.ownerComp.op('nullMapper')).path
				op(p.Learnpath).par[p.Learnparameter].expr = \
				f'op("{refPath}")["{p.Learncontroller}"]'
				debug(f'"{controller}" assigned to {p.Learnpath}[{p.Learnparameter}]')
				self.ClearLearnTarget()
				ui.colors['parms.dialog.bg'] = [.8, .8, .8]
				op('uiScript').run(delayFrames=10)
				
			except Exception as e:
				debug(e)
		
		elif self.Learnmode == 'normReference':
			try:
				refPath = op(self.ownerComp.op('nullMapper')).path
				if op(p.Learnpath).par[p.Learnparameter].style not in ['Menu', 'StrMenu']:
					min = op(p.Learnpath).par[p.Learnparameter].normMin
					max = op(p.Learnpath).par[p.Learnparameter].normMax
				else:
					min = 0
					max = len(op(p.Learnpath).par[p.Learnparameter].menuNames)
				op(p.Learnpath).par[p.Learnparameter].expr = \
				f'tdu.remap(op("{refPath}")["{p.Learncontroller}"], 0, 1, {min}, {max})'
				debug(f'{self.Name} channel "{controller}" normRef assigned to {p.Learnpath}[{p.Learnparameter}]')
				self.ClearLearnTarget()
				ui.colors['parms.dialog.bg'] = [.8, .8, .8]
				op('uiScript').run(delayFrames=10)
				
			except Exception as e:
				debug(e)
		elif self.Learnmode == 'Bind':
			try:
				refPath = op(self.ownerComp.op('bindMapper')).path
				op(p.Learnpath).par[p.Learnparameter].bindExpr = \
				f'op("{refPath}")["{p.Learncontroller}"]'
				debug(f'{p.Learnpath}[{p.Learnparameter}] bound to {self.Name}"{controller}"')
				self.ClearLearnTarget()
				ui.colors['parms.dialog.bg'] = [.8, .8, .8]
				op('uiScript').run(delayFrames=10)
				
			except Exception as e:
				debug(e)

#	Mappings Management	
	

	def Exportmappings(self):
		table = self.ownerComp.op('MappingsTable')
		fileName = ui.chooseFile(load=False, start='local/mappings', 
								fileTypes=['py'], title='Save mappings as:')
		if fileName:
			table.save(fileName)
			print('Mappings successfully saved as ' + fileName)

	def Importmappings(self, comp=''):
		if not comp:
			comp = self.Table
		fileName = ui.chooseFile(load=True, start='local/mappings ', 
								fileTypes=['py'], title='Load table:')
		importProxy = op('importProxy')
		
		ui.undo.startBlock(f'undo {comp} import from {fileName}')
		importProxy.par.file = tdu.collapsePath(fileName)
		comp.copy(importProxy)
		ui.undo.endBlock()
		debug(f'{comp} successfully imported from {fileName}')

	def Editmappings(self):	
		ownerComp = self.ownerComp
		table = self.Table
		if hasattr(op, 'TABLEPOPUP'):
			op.TABLEPOPUP.Open(Table=table, 
						Label= f'{self.Name} {table.name}',
						Quickcolorr = ownerComp.par['Learnparbgcolorr'].eval(),
						Quickcolorg = ownerComp.par['Learnparbgcolorg'].eval(),
						Quickcolorb = ownerComp.par['Learnparbgcolorb'].eval(),
						)
		else:
			table.openViewer()

	def Clearallmappings(self):
		self.clearAllDialog()

	def ClearAllMappings(self, info):
		"""
		Delete all existing presets from MappingsTable
		"""
		if info['buttons'] == 'OK':
			table = self.Table
			table.clear(keepFirstRow=True)
			self.UpdateNumberOfMappings()

	def clearAllDialog(self):
		rowList	= [r[0].row for r in self.Table.rows()]
		debug(rowList)
		op.TDResources.op('popDialog').Open(
			text				= f'Clear all {self.Name} mappings?',
			title				= 'Clear Mappings Table',
			buttons				= ['OK', 'Cancel'],
			callback			= self.DeleteMappings,
			details				= rowList,
			textEntry			= False,
			escButton			= 2,
			enterButton			= 1,
			escOnClickAway		= True)

	def Deletemapping(self, Par='', path=''): #, controller=''):
		ownerComp 	= self.ownerComp
		p			= ownerComp.par
		lm	= self.Learnmode
		if lm == 'Mappings Table':
			if not Par:
				Par	= p.Learnparameter
			if not path:
				path = self.ownerComp.par.Learnpath
			# if not controller:
			# 	controller = self.ownerComp.par.Learncontroller

			if path and Par:
				if Par.val in self.Table.col('parameter'):
					rowList	= [	c.row for c in op('MappingsTable').findCells(Par)
								if self.Table[c.row, 'path'] == path]

			elif path and not Par:
				if path.val in self.Table.col('path'):	
					rowList	= [	c.row for c in op('MappingsTable').findCells(path)]

			elif not path and Par:
				if Par.val in self.Table.col('parameter'):
					rowList	= [	c.row for c in op('MappingsTable').findCells(Par)]
			
			else:
				pass
			try:
				self.clearDialog(rowList)
			except Exception as e:
				debug(e)
		elif lm == 'Reference' or lm == 'normReference':
			parList = [c.name for c in op(p.Learnpath).customPars]
			refPath = self.ownerComp.op('nullMapper').path
			for item in parList:
				if op(p.Learnpath).par[item].mode == ParMode.EXPRESSION:
					if str(op(p.Learnpath).par[item].expr).find(refPath):
						debug(f'references to {self.Name} in {p.Learnpath} cleared')
						op(p.Learnpath).par[item] = op(p.Learnpath).par[item].eval()
		elif lm == 'Bind':
			parList = [c.name for c in op(p.Learnpath).customPars]
			refPath = self.ownerComp.op('nullMapper').path
			for item in parList:
				if op(p.Learnpath).par[item].mode == ParMode.BIND:
					if str(op(p.Learnpath).par[item].bindExpr).find(refPath):
						v = []
						v.append(op(p.Learnpath).par[item].eval())
						debug(f'bindings to {self.Name} in {p.Learnpath} cleared')
						op(p.Learnpath).par[item].mode = ParMode.CONSTANT
						op(p.Learnpath).par[item].val = v[0]

	def DeleteMappings(self, info):
		"""Takes a list of row indices and deletes them from the table"""
		if info['button'] == 'OK':
			rowList = info['details']
			ui.undo.startBlock(f'undo DeleteMappings from {self.Name}')
			self.Table.deleteRows(rowList)
			self.UpdateNumberOfMappings()
			ui.undo.endBlock()
	def clearDialog(self, info):
		rowList	= info
		parList	= [self.Table[r, 'parameter'].val for r in rowList 
					if self.Table[r, 'path'].val == self.ownerComp.par.Learnpath]

		target 	= self.ownerComp.par.Learnpath
		Par			= self.ownerComp.par.Learnparameter

		cList	= [self.Table[r, 'controller'].val for r in rowList]

		string = f'Delete \n{cList}\n mappings to:\n\n{target}\n\n{parList}\n\
				\nfrom {self.Name}'
		op.TDResources.op('popDialog').Open(
			text			= string,
			title			= 'Delete',
			buttons			= ['OK', 'Cancel'],
			callback		= self.DeleteMappings,
			details			= rowList,
			textEntry		= False,
			escButton		= 2,
			enterButton		= 1,
			escOnClickAway	= True)

	def UpdateNumberOfMappings(self):
		"""
		Reset the mappings count to current.
		"""
		self.ownerComp.par.Numberofmappings = op('remove_empty').numRows-1


	def ClearLearnTarget(self):
		ownerComp			= self.ownerComp
		p					= ownerComp.par
		p.Learnpath			= ''
		p.Learnparameter	= ''
		p.Learncontroller	= ''

	def SetRolloverPar(self):
		if ui.rolloverPar != None:
			if ui.rolloverPar.owner != self.ownerComp:
				print(ui.rolloverPar)
				ui.colors['parms.dialog.bg'] = [.8, .8, .8]
				op('uiScript').run(delayFrames=10)
				self.SetLearnParameter(ui.rolloverPar.name)
				self.SetLearnPath(ui.rolloverPar.owner.path)
						

	def SetLearnParameter(self, val):
		self.ownerComp.par.Learnparameter = val
	def SetLearnPath(self, val):
		self.ownerComp.par.Learnpath = val

#Region Callbacks

##	parexec_passThru callbacks

	def onParValueChange(self, par, prev):
		ownerComp = self.ownerComp
		name = par.name
		if name == 'Learn':
			self.Learn(par.val)
		# if name == 'Learnparameter':
		# 	self.Learnparameter()

	def onParPulse(self, par):
		ownerComp = self.ownerComp
		if par.name == 'Test':
			print('test')
		else: 
			try:
				getattr(ownerComp, par.name)()
			except Exception as e:
				debug(e)

## chopexec_passThru
	def onOfftoOn(self, channel, sampleIndex, val, prev):
		name = channel.name 
		if name == 'lselect':
			self.SetRolloverPar()
			
		elif name == 'rselect':
			self.SetLearnParameter('')

		


## datexec_passThru callbacks

	def onCellChange(self, dat, cells, prev):
		self.UpdateNumberOfMappings()
	def onSizeChange(self, dat):
		self.UpdateNumberOfMappings()
