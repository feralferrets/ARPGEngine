#level.py
#
# Current level loader appears to be very ineffiecent...
# Caching things like object images and level backgrounds would probably be a good idea.

import json
import pygame

from graphics import GraphicObject,Animation,AnimationFrame,loadAnimation
from game import GameObject,Pushable,maskFromSurface
from npc import NPC,Dialog
import triggers
import errors

def loadXML(xmlPath,level,GameEngine,GraphicEngine):
	errors.getLogger().info("Loading level: "+level)

	try:
		filer = open(xmlPath,"r")
	except IOError:
		errors.getLogger().critical("Level file not found.")
		exit()
	
	lines = filer.readlines()
	
	started=False
	
	levelData = []
	
	for i in range(len(lines)):	#Strip Tabs and New Lines
		lines[i] = lines[i].lstrip("\t").rstrip("\n")
	
	for line in lines:	#Extract Level Data
		if not started:
			if line == "<Level "+level+">":
				started=True
			continue
		if line == "</Level>":
			break
		levelData.append(line)
	
	Name=None
	BG = None
	Mask=None
	Enemies=None
	BattleBG=None
	BattleFBG=None
	Triggers = []
	GameObjects = []
	NPCs = []
	i = 0
	
	while i < len(levelData):	#Isolate Triggers, NPCs, and GameObjects (GraphicObjects must be dealt with immediately because they are contained within GameObjects)
		temp = {}
		if levelData[i].startswith("<LevelName>"):
			Name=levelData[i].lstrip("<LevelName").lstrip(">").rstrip("/LevelName>").rstrip("<")
		elif levelData[i].startswith("<Background>"):
			BG=levelData[i].lstrip("<Background").lstrip(">").rstrip("/Background>").rstrip("<")
		elif levelData[i].startswith("<Mask>"):
			Mask=levelData[i].lstrip("<Mask").lstrip(">").rstrip("/Mask>").rstrip("<")
		elif levelData[i].startswith("<Enemies>"):
			Enemies = json.loads(levelData[i].lstrip("<Enemies").lstrip(">").rstrip("/Enemies>").rstrip("<"))
		elif levelData[i].startswith("<BattleBG>"):
			BattleBG = json.loads(levelData[i].lstrip("<BattleBG").lstrip(">").rstrip("/BattleBG>").rstrip("<"))
		elif levelData[i]=="<Trigger>":
			n=1
			while levelData[i+n]!="</Trigger>":
				key = levelData[i+n][1:levelData[i+n].find(">")]
				value = levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].find("<",levelData[i+n].find(">"))]
				temp[key]=json.loads(value)
				n+=1
			Triggers.append(temp)
			i+=n
		elif levelData[i].startswith("<GameObject"):
			path = levelData[i].lstrip("<GameObject").rstrip(">").lstrip(" ").split(" ")[0]
			if len(levelData[i].lstrip("<GameObject").rstrip(">").lstrip(" ").split(" "))>1:
				objectName = levelData[i].lstrip("<GameObject").rstrip(">").lstrip(" ").split(" ")[1]
			if path != "":
				tempFiler = file(path,"r")
				lines = tempFiler.readlines()
				started=False
				for j in range(len(lines)):	#Strip Tabs and New Lines
					lines[j] = lines[j].lstrip("\t").rstrip("\n")
				j=1
				for line in lines:	#Extract Level Data
					if not started:
						if line == "<GameObject "+objectName+">":
							started=True
						continue
					if line == "</GameObject>":
						break
					levelData.insert(i+j,line)
					j+=1
					
				#for line in levelData:
				#	print line
				
			temp["graphicObject"] = {}
			n=1
			while levelData[i+n]!="</GameObject>":
				key = levelData[i+n][1:levelData[i+n].find(">")]
				if key == "Mask":
					n+=1
					temp["mask"] = {}
					while levelData[i+n]!="</Mask>":
						state = levelData[i+n][7:levelData[i+n].find(">")]
						temp["mask"][state] = json.loads(levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].rfind("<")])
						n+=1
					n+=1
				elif key == "GraphicObject":
					if "animations" not in temp["graphicObject"]:
						temp["graphicObject"]["animations"] = {}
					n+=1
					while levelData[i+n]!="</GraphicObject>":
						if levelData[i+n].startswith("<State"):
							state = levelData[i+n][7:levelData[i+n].find(">")]
							temp["graphicObject"]["animations"][state] = [None,None,None,None]
							n+=1
							while levelData[i+n]!="</State>":
								#Retrieve Direction
								dire = int(levelData[i+n][11:levelData[i+n].find(">")])
								xml = levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].rfind("<")]
								if dire == 0:
									temp["graphicObject"]["animations"][state][dire] = loadAnimation(xml,state+"N")
								elif dire == 1:
									temp["graphicObject"]["animations"][state][dire] = loadAnimation(xml,state+"E")
								elif dire == 2:
									temp["graphicObject"]["animations"][state][dire] = loadAnimation(xml,state+"S")
								elif dire == 3:
									temp["graphicObject"]["animations"][state][dire] = loadAnimation(xml,state+"W")
								n+=1
							n+=1
						else:
							key = levelData[i+n][levelData[i+n].find("<")+1:levelData[i+n].find(">")]
							value = levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].rfind("<")]
							temp["graphicObject"][key] = json.loads(value)
							n+=1
					n+=1
				else:
					value = levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].find("<",levelData[i+n].find(">"))]
					temp[key[0].lower()+key[1:]]=json.loads(value)
					n+=1
			GameObjects.append(temp)
			i+=n
		elif levelData[i].startswith("<NPC"):
			path = levelData[i].lstrip("<NPC").rstrip(">").lstrip(" ").split(" ")[0]
			if len(levelData[i].lstrip("<NPC").rstrip(">").lstrip(" ").split(" "))>1:
				objectName = levelData[i].lstrip("<GameObject").rstrip(">").lstrip(" ").split(" ")[1]
			if path != "":
				tempFiler = file(path,"r")
				lines = tempFiler.readlines()
				started=False
				for j in range(len(lines)):	#Strip Tabs and New Lines
					lines[j] = lines[j].lstrip("\t").rstrip("\n")
				j=1
				for line in lines:	#Extract Level Data
					if not started:
						if line == "<NPC "+objectName+">":
							started=True
						continue
					if line == "</NPC>":
						break
					levelData.insert(i+j,line)
					j+=1
				
			n=1
			while levelData[i+n]!="</NPC>":
				key = levelData[i+n][1:levelData[i+n].find(">")]
				value = levelData[i+n][levelData[i+n].find(">")+1:levelData[i+n].find("<",levelData[i+n].find(">"))]
				if key == "Dialog":
					dialog=open(value,"r")
					lines=dialog.readlines()
					dialog=""
					for line in lines:
						dialog+=line.rstrip("\n")
					dialog.replace("\t","")
					temp["Dialog"]=json.loads(dialog)
				elif key == "Icon":
					if value=="null":
						temp["Icon"]=None
					else:
						temp["Icon"]=value
				else:
					temp[key]=json.loads(value)
				n+=1
			NPCs.append(temp)
			i+=1
		i+=1
	if Name == None:
		errors.getLogger().warning("Level has no Name attribute.")
		Name = "Unknown Area"
	GraphicEngine.setLevelName(Name)
	if BG == None:
		errors.getLogger().error("Level has no Background attribute.")
	else:
		GraphicEngine.setBackground(pygame.image.load(BG).convert())
	if Mask == None:
		errors.getLogger().info("Level has no Mask attribute.")
	else:
		GameEngine.setMask(pygame.image.load(Mask).convert())
	if Enemies != None and len(Enemies)>0:
		if BattleBG == None or len(BattleBG) == 0:
			errors.getLogger.error("No battle backgrounds specified for this level.")
		else:
			for i in xrange(len(BattleBG)):
				for j in range(len(BattleBG[i])):
					if BattleBG[i][j] != None:
						try:
							BattleBG[i][j] = pygame.image.load(BattleBG[i][j]).convert_alpha()
						except pygame.error:
							errors.getLogger().error("Unable to load battle background for this level.")
							BattleBG[i][j] = None
			GameEngine.setBattleBG(BattleBG)
	
	for trigger in Triggers:
		errors.getLogger().debug("Adding "+trigger["Effect"]+" trigger.")
		if "Area" in trigger.keys() and trigger["Area"]!=None:
			trigger["Area"] = pygame.rect.Rect(trigger["Area"])
		if trigger["Effect"]=="State Set":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.StateSetTrigger(**trigger))
		elif trigger["Effect"]=="State Toggle":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.StateToggleTrigger(**trigger))
		elif trigger["Effect"]=="Area Change":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.AreaChangeTrigger(**trigger))
		elif trigger["Effect"]=="SBSC":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.SBSCTrigger(**trigger))
		elif trigger["Effect"]=="TBSC":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.TBSCTrigger(**trigger))
		elif trigger["Effect"]=="Battle":
			del trigger["Effect"]
			GameEngine.addTrigger(triggers.BattleTrigger(**trigger))
		else:
			errors.getLogger().error("Undefined Trigger Effect")
	
	for obj in GameObjects:
		
		errors.getLogger().debug("Adding "+obj["id"])
		#print str(obj["id"])+":"
		#for key in obj.keys():
		#	print key,obj[key]
		#for key in obj["graphicObject"].keys():
		#	print key,obj["graphicObject"][key]
		#for key in obj["graphicObject"]["animations"].keys():
		#	for i in range(0,4):
		#		if obj["graphicObject"]["animations"][key][i] != None:
		#			print key+str(i),len(obj["graphicObject"]["animations"][key][i].getFrames())
		#		else:
		#			print key+str(i),None
		#print "\n"
		
		for state in obj["mask"].keys():
			if obj["mask"][state] != None:
				img = pygame.image.load(str(obj["mask"][state]))
				obj["mask"][state] = maskFromSurface(img)
		if obj["graphicObject"].keys().__contains__("flipX"):
			for state in obj["graphicObject"]["animations"].keys():
				i=0
				if obj["graphicObject"]["animations"][state][1].getNextAnimation() != None:
					nextAnimation = obj["graphicObject"]["animations"][state][1].getNextAnimation()[:-1]+"W"
				else:
					nextAnimation = None
				obj["graphicObject"]["animations"][state][3] = Animation(None,nextAnimation,state+"W")
				for frame in obj["graphicObject"]["animations"][state][1].getFrames():
					i+=1
					obj["graphicObject"]["animations"][state][3].addFrame(AnimationFrame(pygame.transform.flip(frame.image,True,False),frame.delay,None,i-1))
			del obj["graphicObject"]["flipX"]
		
		#Animation Linker:
		for state in obj["graphicObject"]["animations"].keys():
			for dire in range(0,4):
				if obj["graphicObject"]["animations"][state][dire] == None:
					continue
				nextState = obj["graphicObject"]["animations"][state][dire].getNextAnimation()
				if nextState == None or type(nextState)==Animation:
					continue
				if obj["graphicObject"]["animations"][nextState.rstrip("NESW")][dire].getName()==nextState:
					obj["graphicObject"]["animations"][state][dire].nextAnimation = obj["graphicObject"]["animations"][nextState.rstrip("NESW")][dire]
				else:
					errors.getLogger().error("Animation linker is officially insufficient. \n(It was already unofficially insufficient, but now things just got worse)\n((Troublemaker: "+state+" -> "+nextState+"))")
		
		obj["graphicObject"] = GraphicObject(**obj["graphicObject"])
		GraphicEngine.addObject(obj["graphicObject"])
		if obj.keys().__contains__("pushable") and obj["pushable"]==True:
			del obj["pushable"]
			if obj["area"]!=None:
				obj["area"] = pygame.rect.Rect(obj["area"])
			GameEngine.addActor(Pushable(**obj))
		else:
			GameEngine.addActor(GameObject(**obj))
	
	for npc in NPCs:
		errors.getLogger().debug("Adding NPC: "+npc["Name"])
		if npc["Icon"]!=None:
			npc["Icon"]=pygame.image.load(npc["Icon"]).convert()
		npc["Dialog"]=loadDialog(npc["Dialog"])
		#print npc["Dialog"]
		temp = NPC(**npc)
		GameEngine.addNPC(temp)
		GraphicEngine.addObject(temp.getGraphicObject())
	
	filer.close()
	

def loadDialog(data):
	if data==None:
		return None
	elif data=="$BUY":
		return "$BUY"
	elif data=="$SELL":
		return "$SELL"
	elif data=="$SLEEP":
		return "$SLEEP"
	links=[]
	for link in data["Links"]:
		links.append(loadDialog(link))
	dialog=Dialog(data["Text"],data["Options"],links)
	return dialog

def load(xmlpath,level,GameEngine,GraphicEngine):
	loadXML(xmlpath,level,GameEngine,GraphicEngine)
	GameEngine.loadLevel(level)
	#GraphicEngine.loadLevel(level)
