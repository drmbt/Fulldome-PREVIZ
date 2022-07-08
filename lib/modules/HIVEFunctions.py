"""
This is my attempt at a TDFunctions style global module. It can be called
via op.MOD.mod.HF, or if it lives in local/modules, simply mod.HF 
and is meant to house generic functions I find myself coming back to again and again
"""

from collections import OrderedDict
import TDJSON
import os 
import subprocess
import TDFunctions as TDF
from datetime import datetime
log = op.LOGGER

@property
def NumberTypes():
	return ['Float', 'Int', 'RGB', 'RGBA', 'XY', 'XYZ', 'UV', 'UVW', 'WH' ]



#	parameter methods

def ParSet(Op, Print=False, Debug=False, **kwargs):
	"""
	Generic kwargs setter for an arbitrary number of parameters.
	Print will log the arguments, Debug will log missing parameters
	"""
	if Print: print(Op, Debug, kwargs)
	for arg, val in kwargs.items():
		try:
			Op.par[arg] = val
		except:
			if Debug: debug(f'{arg} parameter not found in {Op}')
			pass
			
def ParGet(Op, *args):
	"""Generic kwargs par getter returning a list of ordered dict items"""
	Print = 'Print' in args
	Debug = 'Debug' in args
	parDict = {}#OrderedDict()
	if Print: print(*args)
	for arg in args:
		try:
			parDict[arg] = Op.par[arg].eval()
		except:
			if Debug: debug(f'{arg} parameter not found in {Op}')
			pass
	if Print: print(parDict)
	return parDict#list(parDict.items())

def Open(Op, Print=False, Debug=False, **kwargs):
	"""
	Opens the target Op's viewer, calling ParSet to arbitrarily set target Op's parameters
	if Print: log kwargs
	if Debug: debug missing parameters
	kwargs can be any parameters of the target Op	
	"""
	ParSet(Op, Print, Debug, **kwargs)
	Op.openViewer()


def OpenParameters(Op):
	"""use PARPOPUP component to open a floating viewer if you've got it"""
	try:
		op.PARPOPUP.Open(Op= Op.path, 
						Label=Op.name, 
						Header=False, 
						Height=750,
						Width=600,
						Pagenames = True,
						Builtin = True,
						Viewer=True)
	except:
		Op.openParameters()

def DestroyPages(comp, pages=None):
	"""Destroy customPar pages based on stringName. if no list of pages is specified, all customPages will be destroyed"""
	pageList = [customPage.name for customPage in comp.customPages]
	if pages == None:
		pages = pageList
	for p in reversed(pages):
		if p in pageList:
			n = pageList.index(p)
			comp.customPages[n].destroy()
			debug(f'customPage: {p} destroyed from op: {comp}')		
	
def SetParMode(targetOp, pageScope: list=None, parScope: list =None, mode='constant'):
	"""Change the par mode for a list of pages and or parameters"""
	lookup = {
		'constant'		: ParMode.CONSTANT,
		'CONSTANT'		: ParMode.CONSTANT,
		'expression'	: ParMode.EXPRESSION,
		'expr'			: ParMode.EXPRESSION,
		'EXPRESSION'	: ParMode.EXPRESSION,
		'bind'			: ParMode.BIND,
		'BIND'			: ParMode.BIND
	}
	mode = lookup[mode]
	pageList = [customPage.name for customPage in targetOp.customPages]
	parList = targetOp.customPars
	if pageScope == None or pageScope == '*':	pageScope = pageList
	if parScope == None or parScope == '*':	parScope = parList
	for p in parList:
		if p.page in pageScope:
			if p.page in pageList:
				if p.name in [p.name for p in parScope]:
					try:
						op(targetOp).par[p.name].mode = mode
						debug()
					except Exception as e:
						debug(e)
						#debug(f"SetParMode to {mode }failed for {op(targetOp)}[{p.name}]")


def CopyPars(fromOp, toOp, pageScope: list=None, parScope: list =None, default=False, reference=False, bind=False, dataRef=False, bindRef=False, dataBind=False, bindParent=False, readOnly=False):
	"""
	Copy customPars from one COMP to another. a list of pages and or parameters 
	can be specified, and a number of flags can be set to bind or reference pars from the 
	target op to the receiving op, or to its parent
	"""
	pageList = [customPage.name for customPage in fromOp.customPages]
	parList = fromOp.customPars
	if pageScope == None or pageScope == '*':	pageScope = pageList
	if parScope == None or parScope == '*':	parScope = [p.name for p in parList]
	debug(pageScope, parScope)
	for p in parList:
		if p.page in pageScope:
			if p.page in pageList:
				if p.name in parScope:
					
					try:
						jsonDict = TDJSON.parameterToJSONPar(p, extraAttrs=['val', 'readOnly', 'help'], forceAttrLists=False)
						TDJSON.addParameterFromJSONDict(toOp, jsonDict, replace=True, setValues=False, ignoreAttrErrors=False, fixParNames=True)						
						if bind:
							for par in p.tuplet:
								op(toOp).par[par.name].bindExpr =TDF.getShortcutPath(toOp, fromOp, toParName=par.name)

						elif bindRef:
							for par in p.tuplet:
								op(fromOp).par[par.name].bindExpr = TDF.getShortcutPath(fromOp, toOp, toParName=par.name)
						elif bindParent:
							for par in p.tuplet:
								op(fromOp).par[par.name].bindExpr = f"parent().par['{par.name}']"
						elif reference:
							for par in p.tuplet:
								op(toOp).par[par.name].expr = f"op('{fromOp}').par['{par.name}']"					
						elif dataRef:
							for par in p.tuplet:
								op(fromOp).par[par.name].expr = f"op('null_data')['{par.name}']"	
						elif dataBind:
							for par in p.tuplet:
								op(fromOp).par[par.name].bindExpr = f"op('bind_data')['{par.name}']"	
						for par in p.tuplet:
							op(toOp).par[par.name].readOnly = readOnly
						for par in p.tuplet:
							op(toOp).par[par.name] = op(fromOp).par[par.name].val

					except Exception as e:
						debug(e)


def Customize(comp):
	"""open CustomPar dialog editor for argued comp"""
	if not comp.isCOMP:
		comp = comp.parent()
	op.TDDialogs.op('CompEditor').EditComp(comp)

def SetDefaultFromValue(comp, pageScope: list=None, parScope: list =None):
	"""
	set the specified operator's parameters' or pages of parameters' defaults 
	from their current values
	"""
	pageList = [customPage.name for customPage in comp.customPages]
	parList = comp.customPars
	if pageScope == None or pageScope == '*':	pageScope = pageList
	if parScope == None or parScope == '*':	parScope = parList
	for p in parList:
		if p.page in pageScope:
			if p.page in pageList:
				if p.name in [p.name for p in parScope]:
					try:
						p.default = p.val
						log.Debug("f update {p.owner}['{p.name}']: {p.val}, {p.normMin}, {p.normMax}, {p.style}")
						if p.style in ['Float', 'Int', 'RGB', 'RGBA', 'XY', 'XYZ', 'UV', 'UVW', 'WH' ]:
							if p.val >= p.normMax:
								p.normMax = p.val
							if p.val <= p.normMin:
								p.normMin = p.val		
					except Exception as e:
						debug(e)
#						print(f"SetDefaultFromValues() failed for {comp}['{p.name}']")



def OpenNetwork(comp, showParameters=True, inside=False, floating=True):
	"""helper method to open a floating or inherited network at the supplied comp position"""
	if floating:
		pane = TDF.showInPane(comp, inside=inside)
		pane.showParameters = showParameters
	else:
		ui.panes[0].owner = comp



def Explorer(path):
	FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
	path = os.path.normpath(path)
	debug(FILEBROWSER_PATH)
	if os.path.isdir(path):
		subprocess.run([FILEBROWSER_PATH, path])
	elif os.path.isfile(path):
		subprocess.run([FILEBROWSER_PATH, '/select,', path])
# def Winopen(self):
# 	self.ownerComp.op('window').par.winopen.pulse()

def DocstringsToHelp(targetOp):
	"""method for writing docstrings to customPar help attribute
	TO DO: update methods to work with multi-dimensional tuplets
	"""
	for p in targetOp.customPars:
		debug(p)
		help = p.help	
		debug(help)		
		if hasattr(targetOp, p.name):
			debug(hasattr(targetOp, p.name))
			docstring = f"op('{targetOp.path}').{p.name}.__doc__"
			debug(eval(docstring))
			if len(targetOp.extensions) > 0:		
				if p.help and p.help!= 'Help not available.':
					help += f"; __docs__:  {eval(docstring)}"
				else:
					help = eval(docstring)
				if help != None and help != '':		
					try:
						debug(help)
						targetOp.par[p.name].help = help
					except Exception as e:
						help = ''
				
# sting functionality
def CollapseSting(targetComp):
	"""sting target Op with a Header per customPage named expand for UberGUI"""
	Op = targetComp
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

def Test(string='Test'):
	debug(string)


def Timestamp(format="%Y.%m.%d.%H.%M.%S%f"):
	now = datetime.now()
	current_time = now.strftime(format)
	return current_time	

def AddAboutPage(COMP, drmbt=False):
	newPage = COMP.appendCustomPage('About')
	version = newPage.appendStr('Version')
	commitdate = newPage.appendStr('Commitdate', label='Commit Date')
	contact = newPage.appendStr('Contact')
	instagramurl = newPage.appendStr('Instagramurl', label='Instagram URL')
	giturl = newPage.appendStr('Giturl', label= 'Git URL')
	supporturl = newPage.appendStr('Supporturl', label='Support URL')
	helpurl = newPage.appendStr('Helpurl', label='Help URL')
	
	git = newPage.appendPulse('Git')
	support = newPage.appendPulse('Support')
	help = newPage.appendPulse('Help')
	readme = newPage.appendPulse('Readme')

	AboutSting(COMP)
	ReadmeSting(COMP)

	if drmbt==True:
		COMP.par.Version = '1.0'
		COMP.par.Version.readOnly = True
		COMP.par.Commitdate= Timestamp('%Y.%m.%d')
		COMP.par.Commitdate.readOnly = True
		COMP.par.Contact = 'Vincent@drmbt.com'
		COMP.par.Contact.readOnly = True
		COMP.par.Instagramurl = 'instagram.com/drmbt'
		COMP.par.Instagramurl.readOnly = True
		COMP.par.Giturl = 'github.com/drmbt'
		COMP.par.Supporturl = 'https://drmbt.com/projects/about/'
		COMP.par.Supporturl.readOnly = True

def AboutSting(path):
	target = op(path)
#	debug(target.findChildren(depth=1, name='AboutExt'))
	if target.findChildren(depth=1, name='AboutExt') == []:

		aSting = target.copy(op.MOD.op('AboutExt'))
		aSting.nodeX = TDF.findNetworkEdges(target)['positions']['left'] -150
		aSting.nodeY = 150
		aExec = target.copy(op.MOD.op('extensionParExecHelp'))
		aExec.nodeX = TDF.findNetworkEdges(target)['positions']['left'] -150
		aExec.nodeY = 150

		extsLen = target.par.extension1.sequence.numBlocks
		if target.par.extension1.eval() =='' and extsLen == 1:
			extNum = 1
			target.par.extension1.sequence.numBlocks = extsLen + 1
		else:
			extNum = extsLen + 1
			target.par.extension1.sequence.numBlocks = extsLen + 2
		
		ext1Script = f"op('{target}').par.extension{extNum} = \"op('./AboutExt').module.AboutExt(me)\""
		name1Script = f"op('{target}').par.extname{extNum} = 'AboutExt'"
		promote1Script = f"op('{target}').par.promoteextension{extNum} = True"


		run(ext1Script)
		run(name1Script)
		run(promote1Script)

def ReadmeSting(COMPpath):
	target = op(COMPpath)
	if not target.op('readme'):
		readme = target.create(textDAT, 'readme')
		readme.nodeX = TDF.findNetworkEdges(target)['positions']['left'] -150
		readme.nodeY = 150
		readme.text = f'"""\nreadme for {target.name}\n"""'

def LogdebugSting(COMPpath):
	"""add Logdebug parameter to debug page of supplied path"""
	if not hasattr(op(COMPpath).par, 'Logdebug'):
		try:
			sting = op(COMPpath).appendCustomPage('Debug').appendToggle('Logdebug')
			op(COMPpath).par.Logdebug.default = True
			op(COMPpath).par.Logdebug.help = 'Enable LOGGER messages'
			log.Debug(f"HIVEFunctions | LogdebugSting({COMPpath})")
		except:
			log.Error(f"HIVEFunctions | FAILED: LogdebugSting({COMPpath})")


def Vscript(string='Test Vscript', fromOP=''):
	if fromOP =='': fromOP = parent()
	mod.VscriptExt.VscriptExt.ParseString(fromOP, string)
	return string  