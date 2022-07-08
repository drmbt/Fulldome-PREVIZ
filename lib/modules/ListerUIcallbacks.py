"""
All callbacks for this lister go in this DAT. For a list of available callbacks,
see:

https://docs.derivative.ca/Palette:lister#Custom_Callbacks
"""

import string
import os
import TDFunctions as TDF

#_______ General selection callbacks ________#

table = op(op(parent().dock).par.Inputtabledat)



def invalidDialog():
	op.TDResources.op('popDialog').Open(
	text='Table edits disabled while Autosync inactive',
	title='Delete',
	buttons=['OK'],
	textEntry=False,
	escButton=2,
	enterButton=1,
	escOnClickAway=True)

def generalSelection(info):
	selection = info['item']
	destructiveList = [	'Clear Row(s)',
						'Delete Row(s)',
						'Add Row',
						'Insert Row',
						'Duplicate',
						'Clear Table',
						'Remove Missing',
						'Import Table',
						'Append Table']
	if selection == 'Export Table':
		parent.ListerUI.Exporttable()
	elif selection == 'Network':
		parent.ListerUI.Opennetwork()	
	if iop.lister.par.Autosyncinputtable.eval():
		if selection == 'Clear Row(s)':
			parent.ListerUI.Clearselectedrows()
		elif selection == 'Delete Row(s)':
			parent.ListerUI.Deleteselectedrows()
		elif selection == 'Add Row':
			parent.ListerUI.Addrow()
		elif selection == 'Insert Row':
			parent.ListerUI.Insertrow()
		elif selection == 'Duplicate':
			parent.ListerUI.Duplicate()
		elif selection == 'Clear Table':
			parent.ListerUI.Cleartable()
		elif selection == 'Remove Missing':
			parent.ListerUI.RemoveMissing()	
		elif selection == 'Import Table':
			parent.ListerUI.Importtable()	
		elif selection == 'Append Table':
			parent.ListerUI.Appendtable()	
	
	elif selection in destructiveList:
		invalidDialog()
		
	return	

#_________ General methods ___________


def onClick(info):
	selectedCell = [info['row'], info['colName']]
	parent.ListerUI.SelectedCell = selectedCell
	if info['ownerComp'].panel.alt:
		menuItems = ['Clear Row(s)', 'Delete Row(s)', 'Add Row', 'Insert Row', 
					'Duplicate', 'Clear Table', 'Remove Missing', 'Export Table', 
					'Import Table', 'Append Table', 'Network']
		op.TDResources.op('popMenu').Open(
		items=menuItems,
		callback=generalSelection,
		callbackDetails=info['row'],
		disabledItems=[],
		dividersAfterItems=['Delete Row(s)', 'Insert Row', 'Clear Table', 
							'Remove Missing', 'Append Table'],
		checkedItems=[],
		subMenuItems=[],
		autoClose=True)


def PopMenu(info=None):
	if iop.lister.par.Autosyncinputtable.eval():
		ext.PopMenuExt.PopTableMenu(info=info)

def onClickRight(info):  
	selectedCell = [info['row'], info['colName']]
	parent.ListerUI.SelectedCell = selectedCell


	if iop.lister.SelectedRows == []:
		iop.lister.SelectRow(info['row'])
	if parent.ListerUI.par.Rightclickmenu.eval():
		PopMenu(info)


def Refresh():	
	iop.lister.Refresh

def updateTable(row, col, cellText):
	table[row, col] = cellText
	Refresh()



#_______ Per cell callbacks ________#



def onDataChanged(info):
#	debug(info)
	return

def onEditEnd(info):

	prevText	= info['prevText']
	cellText	= info['cellText']
	row			= info['row']
	if not parent.ListerUI.par['Prependindex'].eval():
		col			= info['col']
	else:
		col			= info['col']-1
	colName		= info['colName']


	if iop.lister.par.Autosyncinputtable.eval():
		updateTable(row, col, cellText)
	else:
		invalidDialog()
		debug('edits de-activated while Sorting is engaged')
		updateTable(row, col, prevText)	
		iop.lister.Refresh()
	return
#_________ Sort methods _________ 
# def onSort(info):

#_________ Per cell methods _________#

def onClickDelete(info):
	if iop.lister.par.Autosyncinputtable.eval():
		parent.ListerUI.DeleteRows(info['row'])

#_________ Toggle methods _________ 

def onClickInvert(info):
	if table[info['row'], 'Invert'] == 1:
		table[info['row'], 'Invert'] = 0
	else:
		table[info['row'], 'Invert'] = 1

def onClickToggle(info):
	if table[info['row'], 'Toggle'] == 1:
		table[info['row'], 'Toggle'] = 0
	else:
		table[info['row'], 'Toggle'] = 1

def onClickActive(info):
	if table[info['row'], 'Active'] == 1:
		table[info['row'], 'Active'] = 0
	else:
		table[info['row'], 'Active'] = 1
def onClickMissing(info):
	debug('Missing')
	if table[info['row'], 'Missing'] == 1:
		table[info['row'], 'Missing'] = 0
	else:
		table[info['row'], 'Missing'] = 1

def onkeyPress(info):
	return

# dragdrop

def onDropHover(info):
	debug(info)
	return True

def onDrop(info):
	print('!!!DROP')
	debug(info)
	print('DROP!!!')
 