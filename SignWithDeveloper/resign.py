# -*- coding: utf8 -*-

# This script is used to resign ipa with default project's provision file

import os,sys,shutil
import subprocess


# ===== Config =====#


def parentFolder(path):
    return os.path.dirname(path)

def currentFolder():
	return os.path.dirname(os.path.abspath(__file__))

def projectFolder():
	return parentFolder(currentFolder())

def ipaFolder():
	return os.path.join(projectFolder(),"Put_iPA_Here")

def executeShell(cmd,stdinstr = ''):
	print(cmd)
	p=subprocess.Popen(cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdoutdata, stderrdata = p.communicate(stdinstr)
	return p.returncode, stdoutdata, stderrdata


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        
def makeDirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# look for config of specified key in codesign -d output
def codesignConfigOfKey(config,key):
	for line in config.split('\n'):
		keyp = key + "="
		if line.startswith(keyp):
			return line[len(keyp):]


def getInputAppPath(inFolder):
	path = inFolder
	for fileName in os.listdir(path):  
		filePath = os.path.join(path, fileName) 
		if fileName.endswith(".app") or fileName.endswith(".ipa"):
			return filePath


def codesign(appPath,identity,entitlements):
	os.system('codesign -s "%s" --entitlements "%s" -f "%s" ' % (identity,entitlements,appPath))
	frameworkPath = os.path.join(appPath,"Frameworks")
	for fileName in os.listdir(frameworkPath):  
		filePath = os.path.join(frameworkPath, fileName) 
		if fileName.endswith(".framework") or fileName.endswith(".dylib"):
			os.system('codesign -s "%s" --entitlements "%s" -f "%s" ' % (identity,entitlements,filePath))



def start(dummyAppPath):

	print(dummyAppPath)


	# ============ Check ============ #

	provisionFile = os.path.join(dummyAppPath,"embedded.mobileprovision")

	if not os.path.exists(provisionFile):
		print("Provision file not found, please open xcode project, plugin your iphone, and wait xcode automatic sign")
		# return

	

	# ============ Clean ============ #

	tmpDir = os.path.join(currentFolder(),"tmp")
	if os.path.exists(tmpDir):
		shutil.rmtree(tmpDir)

	makeDir(tmpDir)


	# ============ Process Input iPA/App ============ #

	inputAppPath = getInputAppPath(ipaFolder())
	if not inputAppPath:
		print("Please put ipa file under 'Put_iPA_Here' folder")
		return
		

	if inputAppPath.endswith(".ipa"):
		unzipDir = os.path.join(tmpDir,"UnzipedApp")
		os.system('unzip -q "%s" -d "%s"' % (inputAppPath,unzipDir))
		inputAppPath = getInputAppPath(os.path.join(unzipDir,"Payload"))

	print("InputApp: %s" % inputAppPath)

	# ============ Get Info ============ #

	#get certificate used in dummy project
	resCode,dummyCodesignOverview,err = executeShell('codesign -d -vv "%s" ' % (dummyAppPath))

	if resCode != 0:
		print(err)
		return

	# overviewFile = os.path.join(tmpDir,"overview.txt")
	print("====")
	print(dummyCodesignOverview)

	codesignIdentity = codesignConfigOfKey(dummyCodesignOverview,'Authority')
	print(codesignIdentity)
	bundleId = codesignConfigOfKey(dummyCodesignOverview,'Identifier')
	print(bundleId)


	# ============ Copy provision ============ #
	print("Copy provision file")
	provisionPath = os.path.join(dummyAppPath,"embedded.mobileprovision")
	os.system('cp "%s" "%s"' % (provisionPath,inputAppPath))


	# ============ Modify Info.plist ============ #

	#somebody may not have installed plistbuddy
	infoPath = os.path.join(inputAppPath,"Info.plist")
	infoToReplace = ''
	with open(infoPath,'r') as f:
		content = f.read()
		lines = content.split('\n')
		for i in range(0,len(lines)-1):
			line = lines[i]
			# print line
			if line.strip(' \t') == "<key>CFBundleIdentifier</key>":
				print("match info")
				lines[i+1] = "	<string>%s</string>" % bundleId

		infoToReplace = "\n".join(lines)

	with open(infoPath,'w') as f:
		f.write(infoToReplace)

	# ============ Remove plugins ============ #
	pluginDir = os.path.join(inputAppPath,"PlugIns")
	if os.path.exists(pluginDir):
		shutil.rmtree(pluginDir)

	# ============ Export entitlements ============ #
	entitlementsPath = os.path.join(tmpDir,"entitlement.xml")
	if os.path.exists(entitlementsPath):
		os.system('rm %s' % entitlementsPath)
	resCode,dummyCodesignOverview,err = executeShell('codesign -d --entitlements "%s" "%s" ' % (entitlementsPath,dummyAppPath))

	# ============ Resign ============ #
	codesign(inputAppPath,codesignIdentity,entitlementsPath)


	#copy file
	shutil.rmtree(dummyAppPath)
	os.system('cp -r "%s" "%s"' % (inputAppPath,dummyAppPath))



start(sys.argv[1])




