log = op.LOGGER

def onInit(info):
	if parent.Scene.par.Oninit.eval():
		#op('MovieFile').par.Initinfo.pulse()
		if parent().par.Logdebug:
			log.Debug(f'onInit | Scene: {parent().name}')	
		return
		
def onStart(info):
	if parent.Scene.par.Onstart.eval():
		op('switch1').par.index = 1
		for c in parent.Scene.findChildren(type=moviefileinTOP):
			c.par.cuepulse.pulse()
		
		#if op('MovieFile'):
		#	op('MovieFile').par.Active = True
		#parent.Scene.par.Active = True
		#if hasattr(parent.Scene.par.Reset): parent.Scene.par.Reset.pulse()
		
		if parent().par.Logdebug:
			log.Debug(f'onStart | Scene: {parent().name}')	
		return
def onDone(info):
	if parent.Scene.par.Ondone.eval():
		if parent().par.Logdebug:
			log.Debug(f'onDone | Scene: {parent().name}')	
		return
def onExit(info):
	
	if parent.Scene.par.Onexit.eval():
		if parent.Scene.name != op.SCENECHANGER.par.Currentscenename:
			delay = (parent.Scene.par.Fadeouttime * project.cookRate)
			scriptDataGate = "op('switch1').par.index = 0"
			scriptInitData = "parent.Scene.Initdatatable()"
			run(scriptInitData, delayFrames = delay-1)
			run(scriptDataGate, delayFrames = delay+1)
			r = op('render1')
			#r.par.camera = ""
			#r.par.geometry = ""
			#r.par.lights = ""
			#op('renderpass1').par.geometry = ''
			#op('SpaceCameraRig').par.Refrender = ''
			if parent().par.Logdebug:
				log.Debug(f'onExit | Scene: {parent().name}')	
			return 