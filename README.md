# Fulldome-PREVIZ 
![](/lib/samples/UI.png)
## Version 1.0*

built and tested in stable Build TouchDesigner 25370. 

Whilst a commercial TouchDesigner license is necessary for full resolution content, it is designed to scale automatically to the limits of a non-commercial TouchDesigner license, and should work with the stable release of TouchDesigner specified above after installing the executable found at [derivative.ca](https://www.derivative.ca)	

currently only tested in Windows, with issues likely in macOS.

Copyright (c) 2022 [Drmbt](https://github.com/drmbt)
[Vincent Naples](mailto:vincent@drmbt.com)
[drmbt.com](https://www.drmbt.com)	

This project is copyright DreamBait INC, but shared freely for use by artists WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
____________
### About
This is a previz environment for a half sphere Fulldome environment. It is meant as an aid to visualize how Fisheye 180 degree content will read in a dome
_______
### Quickstart
Scenes can be fired by pressing the fire or tween scene button in the SCENE LISTER on the upper left hand of the UI. New Scenes can be created by pressing the + button beneath the list, or right clicking on the list and selecting new scene. Scenes may be deleted by clicking the X icon, or right clicking and selecting Delete Scene(s)

By default this system expects 1:1 aspect content at 4096x4096, but will scale lower res content at the correct aspect ratio to work properly, and should adapt to the limited resolution of a non-commercial TD license.

______

## Additional Features
This UI is a part of @drmbt's HIVE media server template built in TouchDesigner, and has a number of public and hidden features. Those relevant to this build include:
- a Timer UI and Mappable SceneChanger interface along the top bar
- a video and still image capture button indicated in top dock
- master settings accessed via ctrl., or the upper right gear icon
- the ability to toggle off realtime processing by clicking the framerate icon
- layer reference and a color coded UV map along the bottom
- a 3d navigation camera window

## Camera Controls
- rotate (r.click)
- pan (l.click)
- zoom (m.click or wheel)
- home view (h)
- top view (t)
- left view (l)
- right view (r)
- bottom view (b)

## Known Issues
- file path issues likely if macOS use is attempted
- if the currently playing scene is deleted, the SceneChanger may break until the project is re-launched, or SceneChanger is refreshed via a right click on the SCENE LISTER menu, selecting 'Reset SceneChanger'