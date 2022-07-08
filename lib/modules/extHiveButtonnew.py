"""
	HIVE Button
	===========
	

	This file started as extTDMorphButton, a part of TDMorph. I then bloated it
	beyond all recognition, with a bunch of features no one wants but me. 
	
	Check out Darien's version for a cleaner implementation

	info@darienbrito.com
	https://www.darienbrito.com	

    Additional enhancements from the TDMorph element include global
    MIDI, OSC and KEY mapping, an editable Macro table for pushing scaled
    values to an arbitrary number of parameters mapped via drag and drop, 
    and a number of configurable interactions

    interactions:

    drop par on panel = append parameter to macrosTable, exporting scaled values to
    an arbitrary number of project parameters #table can be cleared/edited from ctrl.rclick menu
    
	key commands: 
	
	rselect = reset element to default value #can be disabled via Page: Custom<Rightclickdefault>
    shift.select = activates field for manual entry of value #can be disabled via Page: Custom<Ignoreinteraction>
    ctrl.rselect = opens popup menu for further customization of knob

    TDMorph is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TDMorph is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TDMorph. If not, see <https://www.gnu.org/licenses/>.

	This button is compd and built upon the "yfxButton" kindly contributed 
	by Roy Gerritsen from y=f(x) lab: https://www.yfxlab.com/ 
	
"""

from TDStoreTools import StorageManager
import TDFunctions as TDF
import TDJSON as TDJ

class extHiveButton:
	"""
	extHiveButton description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		#ownerComp.par.Value=0
		#self.Radioexclusive()

	
	@property
	def Name(self):
		return self.ownerComp.name

	@property
	def Value(self):
		return self.ownerComp.par.Value.eval()
		
	@Value.setter
	def Value(self, v):
		self.ownerComp.par.Value = v

	@property
	def Range(self):
		minMax = (0, 1)
		return minMax
	@property
	def NumSiblings(self):
		return max((len(self.ownerComp.parent().findChildren(depth=1, type=PanelCOMP))-1), 1)

	def FieldActive(self, val=0):
		op(self.ownerComp.par.Field).par.clickthrough = val
		
	@property
	def Siblings(self):
		return self.ownerComp.parent().findChildren(depth=1, type=PanelCOMP)
	

	def GradientValue(self, start='Bgcoloron', color='r'):
		ownerComp = self.ownerComp
		startVal	= op(ownerComp).par[str(f'{start}{color}')].eval()
		endVal		= op(ownerComp).par[str(f'{start}end{color}')].eval()
		numSibs		= self.NumSiblings
		if ownerComp.par.Gradientblend == False or numSibs <2:
			gVal = startVal
		else:
			#gVal = endVal
			if ownerComp.digits == None:
				gVal = (endVal - startVal)/(numSibs-1) - \
					(endVal - startVal)/(numSibs-1) + startVal
			else:
				gVal = ((endVal - startVal)/(numSibs-1)*max(ownerComp.digits,1)) - \
					(endVal - startVal)/(numSibs-1) + startVal
		return gVal

##	radio button methods

	def RadioExclusive(self):
		#print('radio method')
		self.ownerComp.par.Value = 1
		for button in self.ownerComp.parent().findChildren(depth=1, type=PanelCOMP):
			if hasattr(button.par, 'Type'):
				if button.par.Type == 'Radio' and button.name != self.ownerComp.name:
						button.par.Value = 0
						
### Selection methods for Widget parent

	def Select(self):
		ownerComp = self.ownerComp
		if hasattr(ownerComp.parent(), 'Selected'):
			if ownerComp.path in ownerComp.parent().Selected:
				self.Deselect()
			else:
				ownerComp.parent().Selected.append(ownerComp.path)
	
	def Deselect(self):
		ownerComp = self.ownerComp
		if hasattr(ownerComp.parent(), 'Selected'):
			if ownerComp.path in ownerComp.parent().Selected:
				ownerComp.parent().Selected.remove(ownerComp.path)
	
	def SelectAll(self):
		ownerComp = self.ownerComp
		if hasattr(ownerComp.parent(), 'Selected'):	
			ownerComp.parent().Selected.clear()
			for op in self.ownerComp.parent().findChildren(depth=1, type=PanelCOMP):
				ownerComp.parent().Selected.append(op.path)
	
	def ClearSelected(self):
		ownerComp = self.ownerComp
		if hasattr(ownerComp.parent(), 'Selected'):	
			ownerComp.parent().Selected.clear()

##  Macros

	def Editmacros(self):
		ownerComp = self.ownerComp
		table =ownerComp.op('code/macrosTable')
		if hasattr(op, 'TABLEPOPUP'):
			op.TABLEPOPUP.Open(table, 
							Label=self.Name + ' MACROS TABLE', 
							dragdrop=ownerComp.par.dragdropcallbacks)
		else:
			ownerComp.op('code/macrosTable').openViewer()
	
	def Clearmacros(self):
		ownerComp = self.ownerComp
		table = ownerComp.op('code/macrosTable')
		table.clear(keepFirstRow=True)
		# if hasattr(ownerComp.par, 'Widgetlabel'):
		# 	ownerComp.par.Widgetlabel = ownerComp.par.Widgetlabel.default
		# elif hasattr(ownerComp.par, 'Labelon'):
		# 	ownerComp.par.Labelon = ownerComp.par.Labelon.default
		# 	ownerComp.par.Labeloff = ownerComp.par.Labeloff.default

#	add methods for using Range attribute to remap
	def SetMacro(self, par):
		ownerComp = self.ownerComp
		if ownerComp.par.Macrosactive:
			default = par.default
			min 	= par.normMin
			max 	= par.normMax
			label 	= par.name
			path 	= op(par.owner).path
			table	= op(ownerComp.par.Macrostable)

    # two methods for naming discrepancy, clean up later
			if hasattr(ownerComp.par, 'Labelon'):
				ownerComp.par.Labelon = label
				ownerComp.par.Labeloff = label
				ownerComp.par.Labeldisplay = True
			if hasattr(ownerComp.par, 'Widgetlabel'):	
				ownerComp.par.Widgetlabel = label
				ownerComp.par.Labeldisplay = True

			table.appendRow([path, label, default, min, max, 0])

	def parseMacros(self, val):
		table	= op(self.ownerComp.par.Macrostable)

		for i in range(1, table.numRows):
			if table[i, 'Missing'] == 1:
				if op(table[i, 'path']):
					table[i, 'Missing'] = 0
			if op(table[i, 'path']):
				if table[i, 'Invert'] == 0:
					op(table[i, 'path']).par[table[i, 'parameter']] = \
					val * (table[i, 'max'] - table[i, 'min']) + table[i, 'min']
				elif table[i, 'Invert'] == 1:
					op(table[i, 'path']).par[table[i, 'parameter']] = \
					val * (table[i, 'min'] - table[i, 'max']) + table[i, 'max']
			else:
				table[i, 'Missing'] = 1
				pass

	## Pop Menu functionality 



	def PopMenu(self):
		if self.ownerComp.par.Altclickmenu == True:
			op.TDResources.op('popMenu').Open(
							items=[	f'{self.Name} Parameters', 
									f'{self.ownerComp.parent().name} Config', 
									'Viewer', 
									'Network', 
									'Customize Component', 
									'Clear Selected',
									'Edit Macros', 
									'Clear Macros', 
									],
							dividersAfterItems=[
									f'{self.ownerComp.parent().name} Config', 
									'Customize Component', 
									'Clear Selected',
									'Clear Macros'
									],
							callback=self.onPopMenu
							)

	def onPopMenu(self, info):
		ownerComp = self.ownerComp
		if info['item'] == f'{self.Name} Parameters':
			self.OpenParameters()
		elif info['item'] == f'{self.ownerComp.parent().name} Config':
			self.OpenParameters(ownerComp.parent())
		elif info['item'] == 'Viewer':
			self.OpenViewer()
		elif info['item'] == 'Network':
			self.OpenNetwork()
		elif info['item'] == 'Customize Component':
			self.CustomizeParameters()
		elif info['item'] == 'Clear Selected':
			self.ClearSelected()
		elif info['item'] == 'Edit Macros':
			self.Editmacros()
		elif info['item'] == 'Clear Macros':
			self.Clearmacros()
			
##  Pane / Op / Dialogs

	def OpenParameters(self, comp=''):
		if not comp:
			comp = self.ownerComp
		if hasattr(op, 'PARPOPUP'):
			op.PARPOPUP.Open(Op= comp.path, 
							Label=comp.name, 
							Header=False, 
							h=750)
		else:
			comp.openParameters()
	def OpenNetwork(self, comp=None):
		if not comp: comp = self.ownerComp
		debug(comp)
		if hasattr(op, 'INSPECTORGADGET'):
			op.INSPECTORGADGET.Opennetwork(comp)
		else:
			pane = TDF.showInPane(op(comp))
			pane.showParameters = True

	def OpenViewer(self, comp=''):
		if not comp:
			comp = self.ownerComp
		comp.openViewer()

	def CustomizeParameters(self, comp=''):
		if not comp:
			comp = self.ownerComp
		op.TDDialogs.op('CompEditor').EditComp(comp)

	def Readme(self):
		self.OpenViewer(op(self.ownerComp.par.Readmefile))

	def Helpgit(self):
		ui.viewFile(self.ownerComp.par.Helpurl)



### PARMORPH methods

	def DefaultJump(self):
		self.Value = self.ownerComp.par.Value.default

	def DefaultMorph(self):
		if hasattr(op, 'PARMORPH'):
			op.PARMORPH.PanelDefaultMorph(self.ownerComp.par.Value)
		else:
			self.DefaultJump()	
	def RandomMorph(self):
		if hasattr(op, 'PARMORPH'):
			op.PARMORPH.PanelRandomMorph(self.ownerComp.par.Value)
		else:
			self.RandomJump()
	def RandomJump(self):
		ownerComp = self.ownerComp
		self.Value = tdu.remap(
			tdu.rand(absTime.frame), 0, 1,	ownerComp.par.Value.normMin, 
											ownerComp.par.Value.normMax)
	def PasteMorph(self):
		if hasattr(op, 'PARMORPH'):
			op.PARMORPH.PanelPasteMorph(self.ownerComp.par.Value)
		else:
			self.PasteValue()

##  Copy/Paste methods

	def CopyValue(self):
		ui.clipboard = self.ownerComp.par.Value

	def PasteValue(self):
		clipboard = ui.clipboard
		ownerComp = self.ownerComp
		ownerComp.par.Value = clipboard

##  INSPECTOR GADGET   
	# def setRolloverPanel(self, panel):
	# 	if hasattr(op, 'INSPECTORGADGET'):
	# 		op.INSPECTORGADGET.SetRolloverPanel(panel)
			
	def CopyAttributes(self):
		if hasattr(op, 'INSPECTORGADGET'):
			op.INSPECTORGADGET.Copy(self.ownerComp)
	def PasteAttributes(self):
		# Add Methods for copying to a loop of Selected ops
		if hasattr(op, 'INSPECTORGADGET'):
			copy = op(op.INSPECTORGADGET.par.Copy)
			jsonOp = TDJ.opToJSONOp(copy, 
									extraAttrs='*', 
									forceAttrLists=True, 
									includeCustomPages=True, 
									includeBuiltInPages=False)
			TDJ.addParametersFromJSONOp(self.ownerComp, 
									jsonOp, 
									replace=True, 
									setValues=True, 
									destroyOthers=False, 
									newAtEnd=True, 
									fixParNames=True)

### region callbacks

##	panelexec_passThru   

	def onPanelEvent(self, event, panelValue):
		
		ownerComp = self.ownerComp
		name = panelValue.name
		owner = panelValue.owner
		

##  Local Keyboard Shortcuts / Hotkeys 	                
		if hasattr(op, 'KEYSMAPPER'):
			ctrl 	= op.KEYSMAPPER.par.Ctrl
			shift	= op.KEYSMAPPER.par.Shift
			alt 	= op.KEYSMAPPER.par.Alt
		else:
			ctrl	= owner.panel.ctrl
			shift	= owner.panel.shift
			alt 	= owner.panel.alt

		if event == 'valueChange':
			if ownerComp.panel.inside and not shift: 
				if name == 'lselect' and not ctrl:
					if ownerComp.par.Uiscriptrunson.eval() == 'Value change':
						ownerComp.UIScript()
					# ownerComp.OnValueChange()

			# if name == 'inside':
			# 	if panelValue == 1:
			# 		self.setRolloverPanel(owner)
			# 	elif panelValue == 1:
			# 		self.setRolloverPanel('None')

		if event == 'onToOff':
			if ownerComp.panel.inside and not shift:
				if name == 'lselect' and not ctrl:	
					if ownerComp.par.Uiscriptrunson.eval() == 'On to off':
						ownerComp.UIScript()
					# ownerComp.OnToOff()
			
		if event == 'offToOn':	
			if ownerComp.panel.inside and not shift:
				if name == 'lselect' and not ctrl:	
					if ownerComp.par.Uiscriptrunson.eval() == 'Off to on':
						ownerComp.UIScript()
					# ownerComp.OffToOn()
				# if name == 'mselect' and hasattr(op, 'VALUELADDER'):
				# 	op.VALUELADDER.Open(self.ownerComp, 'Value', \
				# 		self.ownerComp.name, autoClose=True, \
				# 			closeOnClickRelease=False)
			if alt:
				if panelValue == 100:		# lcase d
					self.DefaultJump()
				if panelValue == 114:		# lcase r
					self.RandomJump()
				if panelValue == 118:		# alt.V
					self.PasteAttributes()
				if name == 'rselect' or name == 'lselect':
					self.PopMenu()
			if ctrl == 1 and alt == 0:
				if name == 'rselect' or name == 'lselect':
					self.ownerComp.PopTableMenu()
				if panelValue == 110:		# lcase n
					self.OpenNetwork()
				if panelValue == 112:		# lcase p
					self.OpenParameters()
				if panelValue == 116:		# lcase t
					self.Editmacros()
				if panelValue == 119:		# lcase w
					self.OpenViewer()
				if panelValue == 117:		# lcase u	
					self.CustomizeParameters()
				if panelValue == 97:		# lcase a
					self.SelectAll()
				if panelValue == 99:		# lcase c
					self.CopyValue()
				if panelValue == 118:		# lcase v	
					self.PasteValue()

			if ctrl and alt:
				if panelValue == 99:		# ctrl.alt.C
					self.CopyAttributes()	
				
			
			if ctrl == 0 and shift == 1:
				if name == 'lselect':
					self.Select()
				if name == 'rselect':
					if hasattr(ownerComp.parent(), 'Selected'):
						self.ClearSelected()
				if panelValue == 68:		# Shift D
					self.DefaultMorph()
				if panelValue == 82:		# Shift R
					self.RandomMorph()
				if panelValue == 86:		# Shift V
					self.PasteMorph()	
			
			if name == 'rselect' and ownerComp.par.Rightclickdefault == True:
			# set default value with right click if par option is Enabled
				if not shift and not ctrl:
					self.DefaultJump()

##	parexec_passThru callbacks

	def onParValueChange(self, par, prev):
		ownerComp = self.ownerComp
		name = par.name
		# selected value update
		if hasattr(ownerComp.parent(), 'Selected'):
				if ownerComp.path in ownerComp.parent().Selected:
					ownerComp.parent().SelectedValueUpdate(par)
			
		if name == 'Value':
			if ownerComp.par.Macrosactive == True:
				if op(ownerComp.par.Macrostable).numRows>1:
					self.parseMacros(par.val)

##	Set UI script behaviors					
		if name == 'Type':
			if par.val == 'Momentary':
				ownerComp.par.Uiscript = 'me.par.Value = not me.par.Value'
				ownerComp.par.Uiscriptrunson = 'Value change'
			elif par.val == 'Toggle':
				ownerComp.par.Uiscript = 'me.par.Value = not me.par.Value'
				ownerComp.par.Uiscriptrunson = 'Off to on'
			elif par.val == 'Radio':
				ownerComp.par.Uiscript = 'me.RadioExclusive()'
				ownerComp.par.Uiscriptrunson = 'Off to on'

	def onParPulse(self, par):
		ownerComp = self.ownerComp
		if par.name == 'Test':
			print('test')
		else: 
			try:
				getattr(ownerComp, par.name)()
			except Exception as e:
				debug(e)
	
##	chopExec_passThru callbacks

	def OffToOn(self):
		cmd = self.ownerComp.par.Offtoonscript.eval()
		if cmd != '':
			run(cmd, fromOP=self.ownerComp)
		if self.ownerComp.par.Type =='Radio':
			#print('radio')
			self.RadioExclusive()
		return

	def OnToOff(self):
		cmd = self.ownerComp.par.Ontooffscript.eval()
		if cmd != '':		
			run(cmd, fromOP=self.ownerComp)
		
		return

	def OnValueChange(self):
		cmd = self.ownerComp.par.Valuechangescript.eval()
		ownerComp = self.ownerComp
		if cmd != '':		
			run(cmd, fromOP=self.ownerComp)
		
		return
		
	def UIScript(self):
		cmd = self.ownerComp.par.Uiscript.eval()
		if cmd != '':		
			run(cmd, fromOP=self.ownerComp)
		return		

## dragdrop_passThru callbacks

	def OnHoverStartGetAccept(self, comp, info): 
		#debug('\nonHoverStartGetAccept comp:', comp.path, '- info:\n', info)
		return True
	def OnHoverEnd(self, comp, info):
		#debug('\nonHoverEnd comp:', comp.path, '- info:\n', info)
		return 
	def OnDropGetResults(self, comp, info):
		#debug('\nonDropGetResults comp:', comp.path, '- info:\n', info)
		try:
			source = info['dragItems'][0]
		except:
			return

		if isinstance(source, Par):
			par = source.owner.par[source.name]
			#debug(par)
			self.SetMacro(par)

		return {'droppedOn': comp}
	def OnDragStartGetItems(self, comp, info):
		#debug('\nonDragStartGetItems comp:', comp.path, '- info:\n', info)
		if comp.par.parentshortcut != 'Widget':
			try:
				dragItems = [op(comp.parent.Widget)] 
			except:
				pass
		else:
			dragItems = [comp]

		return dragItems
	def OnDragEnd(self, comp, info):	
		#debug('\nonDragEnd comp:', comp.path, '- info:\n', info)
		try:
			if isinstance(info['dropResults']['droppedOn'], Par):
				Op = op(info['dragItems'][0])
				info['dropResults']['droppedOn'].expr = f'op(\'{Op}\').par.Value * (me.curPar.normMax - me.curPar.normMin)'
		except Exception as e:
			pass

		return

#	end region callbacks

