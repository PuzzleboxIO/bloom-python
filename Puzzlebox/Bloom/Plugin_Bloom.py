#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Jigsaw - Plug-in - Bloom
#
# Copyright Puzzlebox Productions, LLC (2013-2015)

__changelog__ = """\
Last Update: 2015.03.25
"""

__todo__ = """
"""

import os, string, sys, time

import Puzzlebox.Bloom.Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		from PySide import QtCore, QtGui, QtNetwork
		#if configuration.DEFAULT_BLOOM_AUDIO_FRAMEWORK == 'Phonon':
			#try:
				#from PySide.phonon import Phonon
			#except Exception, e:
				#print "ERROR: [Plugin:Bloom] Exception importing Phonon:",
				#print e
				#configuration.DEFAULT_BLOOM_AUDIO_FRAMEWORK = 'QSound'
	except Exception, e:
		print "ERROR: [Plugin:Bloom] Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Plugin:Bloom] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Plugin:Bloom] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork
	#if configuration.DEFAULT_BLOOM_AUDIO_FRAMEWORK == 'Phonon':
		#try:
			#from PyQt4.phonon import Phonon
		#except Exception, e:
			#print "ERROR: [Plugin:Bloom] Exception importing Phonon:",
			#print e
			#configuration.DEFAULT_BLOOM_AUDIO_FRAMEWORK = 'QSound'


try:
	from Puzzlebox.Jigsaw.Interface_Plot import *
	MATPLOTLIB_AVAILABLE = True
except Exception, e:
	print "ERROR: Exception importing Puzzlebox.Jigsaw.Interface_Plot:",
	print e
	MATPLOTLIB_AVAILABLE = False

#MATPLOTLIB_AVAILABLE = False

if (sys.platform == 'win32'):
	DEFAULT_IMAGE_PATH = 'images'
elif (sys.platform == 'darwin'):
	DEFAULT_IMAGE_PATH = 'images'
else:
	DEFAULT_IMAGE_PATH = '/usr/share/puzzlebox_bloom/images'


try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s


from Puzzlebox.Bloom.Design_Plugin_Bloom import Ui_Form as Design

import Puzzlebox.Bloom.Protocol_Bloom as protocol_bloom
#import puzzlebox_logger


#####################################################################
# Globals
#####################################################################

DEBUG = 1

THINKGEAR_POWER_THRESHOLDS = { \
	
	'concentration': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 0, \
		50: 0, \
		60: 0, \
		70: 0, \
		71: 0, \
		72: 60, \
		73: 62, \
		74: 64, \
		75: 66, \
		76: 68, \
		77: 70, \
		78: 72, \
		79: 74, \
		80: 76, \
		81: 78, \
		82: 80, \
		83: 82, \
		84: 84, \
		85: 86, \
		86: 88, \
		87: 90, \
		88: 90, \
		89: 90, \
		90: 100, \
		100: 100, \
		}, \
	
	'relaxation': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 0, \
		50: 0, \
		60: 0, \
		70: 0, \
		80: 0, \
		90: 0, \
		100: 0, \
		}, \
	
} # THINKGEAR_POWER_THRESHOLDS

BLOOM_LABEL_TITLE = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Sans'; font-size:10pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="http://puzzlebox.io/bloom"><span style=" font-size:11pt; font-weight:600; text-decoration: none; color:#000000;">Puzzlebox<br />Bloom</span></a></p></body></html>
'''

BLOOM_LABEL_HELP_WEB_ADDRESS = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Sans'; font-size:10pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="http://puzzlebox.io/bloom"><span style="text-decoration: none; color:#000000;; color:#0000ff;">http://puzzlebox.io/bloom</span></a></p></body></html>
'''

#####################################################################
# Classes
#####################################################################

class puzzlebox_jigsaw_plugin_bloom(QtGui.QWidget, Design):
	
	def __init__(self, log, tabIndex=None, DEBUG=DEBUG, parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent = parent
		self.tabIndex = tabIndex
		
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		
		self.configuration = configuration
		self.thresholds = THINKGEAR_POWER_THRESHOLDS
		
		self.configureSettings()
		self.connectWidgets()
		
		self.mediaState = None
		
		#if self.configuration.DEFAULT_BLOOM_AUDIO_FRAMEWORK == 'Phonon':
			#self.initializeAudioPhonon()
		#else:
			#self.initializeAudio()
		
		self.name = "Jigsaw-Plugin-Bloom"
		self.baseWidget = self.horizontalLayoutWidget
		self.tabTitle = _fromUtf8("Bloom")
		
		if self.tabIndex == None:
			self.parent.tabWidget.addTab(self.baseWidget, self.tabTitle)
		else:
			self.parent.tabWidget.insertTab(self.tabIndex, self.baseWidget, self.tabTitle)
		
		self.warnings = []
		
		self.customDataHeaders = []
		self.protocolSupport = ['EEG']
		
		self.current_power = 0
		
		self.red = 0
		self.green = 0
		self.blue = 0
		
		self.position = 0
		
		self.protocol = None
		
		#self.updateBloomColor()
	
	
	##################################################################
	
	def configureSettings(self):
		
		self.parent.setProgressBarColor( \
			self.progressBarBloomConcentration, 'FF0000') # Red
		self.parent.setProgressBarColor( \
			self.progressBarBloomRelaxation, '0000FF') # Blue
		self.parent.setProgressBarColor( \
			self.progressBarBloomConnectionLevel, '00FF00') # Green
		self.parent.setProgressBarColor( \
			self.progressBarBloomPower, 'FCFF00') # Yellow
		
		
		self.progressBarBloomConcentration.setValue(0)
		self.progressBarBloomRelaxation.setValue(0)
		self.progressBarBloomConnectionLevel.setValue(0)
		self.progressBarBloomPower.setValue(0)
		#self.dialBloomPower.setValue(0)
		
		#self.pushButtonBloomOn.setChecked(False)
		#self.pushButtonBloomOff.setChecked(True)
		
		# Tweak UI Elements
		#self.pushButtonBloomOn.setVisible(False)
		#self.pushButtonBloomOff.setVisible(False)
		# Following command removed due to causing a segfault
		#self.verticalLayout_5.removeItem(self.horizontalLayout_3)
		
		
		#self.dialBloomPower.setEnabled(False)
		
		
		self.pushButtonBloomConcentrationEnable.setVisible(False)
		self.pushButtonBloomRelaxationEnable.setVisible(False)
		
		self.comboBoxBloomPortSelect.setVisible(False)
		#self.pushButtonBloomSearch.setEnabled(False)
		
		self.pushButtonBloomConnect.setVisible(False)
		self.pushButtonBloomSearch.setVisible(False)
		
		#self.textLabelBloomStatus.setText('Status: Unknown')
		self.textLabelBloomStatus.setVisible(False)
		
		
		#self.searchBloomDevices()
		self.updateBloomDeviceList()
		
		#index = string.uppercase.index(configuration.DEFAULT_BLOOM_HOUSE_CODE)
		#self.comboBoxBloomHouseCode.setCurrentIndex(index)
		#self.comboBoxBloomDeviceNumber.setCurrentIndex(configuration.DEFAULT_BLOOM_DEVICE - 1)
		
		
		if MATPLOTLIB_AVAILABLE:
			
			windowBackgroundRGB =  (self.palette().window().color().red() / 255.0, \
			                        self.palette().window().color().green() / 255.0, \
			                        self.palette().window().color().blue() / 255.0)
			
			self.rawEEGMatplot = rawEEGMatplotlibCanvas( \
			                        parent=self.widgetPlotRawEEG, \
			                        width=self.widgetPlotRawEEG.width(), \
			                        height=self.widgetPlotRawEEG.height(), \
			                        title=None, \
			                        axes_top_text='1.0s', \
			                        axes_bottom_text='0.5s', \
			                        facecolor=windowBackgroundRGB)
			
			
			self.historyEEGMatplot = historyEEGMatplotlibCanvas( \
			                            parent=self.widgetPlotHistory, \
			                            width=self.widgetPlotHistory.width(), \
			                            height=self.widgetPlotHistory.height(), \
			                            title=None, \
			                            axes_right_text='percent', \
			                            facecolor=windowBackgroundRGB)
		
		
		# Help
		#url = self.configuration.DEFAULT_BLOOM_HELP_URL
		url = self.parent.configuration.DEFAULT_BLOOM_HELP_URL
		if (url.startswith('path://')):
			url = "file://" + os.path.join( os.getcwd(), url.split('path://')[1] )
		if (sys.platform == 'win32'):
			url = url.replace('file://', '')
		
		if self.DEBUG:
			print "[Jigsaw:Plugin_Bloom] loadWebURL:",
			print url
		
		self.webViewBloom.load( QtCore.QUrl(url) )
	
	
	##################################################################

	def connectWidgets(self):
		
		self.connect(self.comboBoxBloomModelName, \
		             QtCore.SIGNAL("activated(int)"), \
		             self.updateBloomDeviceList)
		
		self.connect(self.pushButtonBloomSearch, \
		             QtCore.SIGNAL("clicked()"), \
		             self.searchBloomDevices)
		
		self.connect(self.pushButtonBloomConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.connectBloomDevice)
		
		self.connect(self.horizontalSliderBloomConcentration, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderConcentration)
		
		self.connect(self.horizontalSliderBloomRelaxation, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderRelaxation)
		
		
		self.connect(self.pushButtonBloomClose, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomClose)
		
		self.connect(self.pushButtonBloomOpen, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomOpen)
		
		self.connect(self.pushButtonBloomCycle, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomCycle)
		
		self.connect(self.pushButtonBloomDemo, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomDemo)
		
		self.connect(self.horizontalSliderBloomPosition, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderPosition)
		
		self.connect(self.horizontalSliderBloomRed, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderRed)
		
		self.connect(self.horizontalSliderBloomGreen, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderGreen)
		
		self.connect(self.horizontalSliderBloomBlue, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateSliderBlue)
	
	
	##################################################################
	
	def updateBloomInterface(self):
		
		# Interface
		self.parent.setWindowTitle("Puzzlebox Bloom")
		self.parent.tabWidget.setTabText(0, "Puzzlebox")
		
		# Session
		self.parent.plugin_session.textLabelTitlePuzzleboxJigsaw.setText(BLOOM_LABEL_TITLE)
		
		self.parent.plugin_session.labelSessionPluginAPI.hide()
		self.parent.plugin_session.checkBoxServiceEnableJSON.setCheckable(False)
		self.parent.plugin_session.checkBoxServiceEnableJSON.hide()
		self.parent.plugin_session.lineSessionPluginAPI.hide()
		
		sessionGraphicFile = os.path.join( \
			os.getcwd(), \
			'images', \
			self.configuration.DEFAULT_BLOOM_SESSION_GRAPHIC)
		
		try:
			self.parent.plugin_session.labelSessionGraphic.setPixmap(QtGui.QPixmap(sessionGraphicFile))
		except Exception, e:
			if self.DEBUG:
				print "ERROR [Plugin:Bloom] Exception:",
				print e

		# EEG
		self.parent.plugin_eeg.checkBoxControlEmulateThinkGear.setVisible(False)
		
		# Help
		self.parent.plugin_help.textLabelTitlePuzzleboxJigsaw.setText(BLOOM_LABEL_TITLE)
		self.parent.plugin_help.labelWebsiteAddress.setText(BLOOM_LABEL_HELP_WEB_ADDRESS)
		self.parent.plugin_help.loadWebURL(self.parent.configuration.DEFAULT_HELP_URL)
	
	
	##################################################################
	
	def connectBloomDevice(self):
		
		self.comboBoxBloomModelName.setEnabled(False)
		self.comboBoxBloomPortSelect.setEnabled(False)
		self.pushButtonBloomSearch.setEnabled(False)
		
		self.disconnect(self.pushButtonBloomConnect, \
		                QtCore.SIGNAL("clicked()"), \
		                self.connectBloomDevice)
		
		self.connect(self.pushButtonBloomConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disconnectBloomDevice)
		
		self.pushButtonBloomConnect.setText('Disconnect')
		
		bloomDevice = str(self.comboBoxBloomModelName.currentText())
		serial_device = str(self.comboBoxBloomPortSelect.currentText())
		
		#if bloomDevice == 'Puzzlebox Pyramid':
			#mode = 'pyramid'
		#elif bloomDevice == 'Arduino Infrared Circuit':
			#mode = 'arduino'
		#if bloomDevice == 'Mindfulness, Inc. Lotus':
			#mode = 'pyramid'
		if bloomDevice == 'Puzzlebox Bloom':
			mode = 'bloom'
		
		self.protocol = protocol_bloom.puzzlebox_jigsaw_protocol_bloom( \
		                   log=self.log, \
		                   serial_port=serial_device, \
		                   mode=mode, \
		                   command='land', \
		                   DEBUG=self.DEBUG, \
		                   parent=self)
		
		self.protocol.start()
		
		
		# Set color on connect
		if self.parent.configuration.BLOOM_SET_COLOR_CONNECT != None:
			self.setBloomColor(self.parent.configuration.BLOOM_SET_COLOR_CONNECT[0],
			                   self.parent.configuration.BLOOM_SET_COLOR_CONNECT[1], 
			                   self.parent.configuration.BLOOM_SET_COLOR_CONNECT[2])
	
	
	##################################################################
	
	def disconnectBloomDevice(self):
		
		# Set color on disconnect
		if self.parent.configuration.BLOOM_SET_COLOR_DISCONNECT != None:
			self.setBloomColor(self.parent.configuration.BLOOM_SET_COLOR_DISCONNECT[0],
			                   self.parent.configuration.BLOOM_SET_COLOR_DISCONNECT[1], 
			                   self.parent.configuration.BLOOM_SET_COLOR_DISCONNECT[2])
		
		self.comboBoxBloomModelName.setEnabled(True)
		self.comboBoxBloomPortSelect.setEnabled(True)
		self.pushButtonBloomSearch.setEnabled(True)
		
		self.disconnect(self.pushButtonBloomConnect, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disconnectBloomDevice)
		
		self.connect(self.pushButtonBloomConnect, \
		             QtCore.SIGNAL("clicked()"), \
		             self.connectBloomDevice)
		
		self.pushButtonBloomConnect.setText('Connect')
		
		
		if self.protocol != None:
			self.protocol.stop()
		
		self.protocol = None
	
	
	##################################################################
	
	def updateBloomDeviceList(self, index=None):
		
		selection = str(self.comboBoxBloomModelName.currentText())
		
		#if selection == 'Puzzlebox Pyramid':
			
			#self.comboBoxBloomPortSelect.setVisible(True)
			#self.pushButtonBloomConnect.setVisible(True)
			##self.pushButtonBloomSearch.setEnabled(True)
			#self.pushButtonBloomSearch.setVisible(True)
		
		
		if selection == 'Puzzlebox Bloom':
			
			self.comboBoxBloomPortSelect.setVisible(True)
			self.pushButtonBloomConnect.setVisible(True)
			#self.pushButtonBloomSearch.setEnabled(True)
			self.pushButtonBloomSearch.setVisible(True)
		
		
		#elif selection == 'Audio Infrared Dongle':
			
			#self.comboBoxBloomPortSelect.setVisible(False)
			#self.pushButtonBloomConnect.setVisible(False)
			##self.pushButtonBloomSearch.setEnabled(False)
			#self.pushButtonBloomSearch.setVisible(False)
			
			#error_message = 'Warning: Differences between audio hardware produce variations in signal output. Audio IR control for the Bloom does not work on all computers.'
			
			#if ('audio_infrared_dongle' not in self.warnings):
				#QtGui.QMessageBox.information(self, \
				                             #'Warning', \
				                              #error_message)
			#self.warnings.append('audio_infrared_dongle')
		
		
		#elif selection == 'Arduino Infrared Circuit':
			
			#self.comboBoxBloomPortSelect.setVisible(True)
			#self.pushButtonBloomConnect.setVisible(True)
			##self.pushButtonBloomSearch.setEnabled(True)
			#self.pushButtonBloomSearch.setVisible(True)
		
		
		self.searchBloomDevices()
	
	
	##################################################################
	
	def searchBloomDevices(self):
		
		self.comboBoxBloomPortSelect.clear() # doesn't seem to work under OS X
		
		devices = self.searchForSerialDevices()
		
		if devices == []:
			devices = ['No Devices Found']
			self.comboBoxBloomPortSelect.setEnabled(False)
			self.pushButtonBloomConnect.setEnabled(False)
		else:
			self.comboBoxBloomPortSelect.setEnabled(True)
			self.pushButtonBloomConnect.setEnabled(True)
		
		for device in devices:
			self.comboBoxBloomPortSelect.addItem(device)
	
	
	##################################################################
	
	def searchForSerialDevices(self, devices=[]):
		
		if (sys.platform == 'win32'):
			
			for portname in self.parent.plugin_eeg.enumerateSerialPorts():
				
				if portname not in devices:
					#portname = self.fullPortName(portname)
					devices.append(portname)
		
		else:
			
			if os.path.exists('/dev/ttyUSB0'):
				devices.append('/dev/ttyUSB0')
			if os.path.exists('/dev/ttyUSB1'):
				devices.append('/dev/ttyUSB1')
			if os.path.exists('/dev/ttyUSB2'):
				devices.append('/dev/ttyUSB2')
			if os.path.exists('/dev/ttyUSB3'):
				devices.append('/dev/ttyUSB3')
			if os.path.exists('/dev/ttyUSB4'):
				devices.append('/dev/ttyUSB4')
			if os.path.exists('/dev/ttyUSB5'):
				devices.append('/dev/ttyUSB5')
			if os.path.exists('/dev/ttyUSB6'):
				devices.append('/dev/ttyUSB6')
			if os.path.exists('/dev/ttyUSB7'):
				devices.append('/dev/ttyUSB7')
			if os.path.exists('/dev/ttyUSB8'):
				devices.append('/dev/ttyUSB8')
			if os.path.exists('/dev/ttyUSB9'):
				devices.append('/dev/ttyUSB9')
			
			if os.path.exists('/dev/ttyACM0'):
				devices.append('/dev/ttyACM0')
			if os.path.exists('/dev/ttyACM1'):
				devices.append('/dev/ttyACM1')
			if os.path.exists('/dev/ttyACM2'):
				devices.append('/dev/ttyACM2')
			if os.path.exists('/dev/ttyACM3'):
				devices.append('/dev/ttyACM3')
			if os.path.exists('/dev/ttyACM4'):
				devices.append('/dev/ttyACM4')
			
			if os.path.exists('/dev/tty.usbmodemfd1221'):
				devices.append('/dev/tty.usbmodemfd1221')
			if os.path.exists('/dev/tty.usbmodemfd1222'):
				devices.append('/dev/tty.usbmodemfd1222')
			if os.path.exists('/dev/tty.usbmodem1411'):
				devices.append('/dev/tty.usbmodem1411')
			if os.path.exists('/dev/tty.usbmodem14231'):
				devices.append('/dev/tty.usbmodem14231')
				
			
			#if os.path.exists('/dev/tty.usbserial-A602050J'):
				#devices.append('/dev/tty.usbserial-A602050J')
			#if os.path.exists('/dev/tty.usbserial-A100MZB6'):
				#devices.append('/dev/tty.usbserial-A100MZB6')
		
		
		if (sys.platform == 'darwin'):
			for device in os.listdir('/dev'):
				if device.startswith('tty.usbserial'):
					devices.append( os.path.join('/dev', device))
				if device.startswith('tty.usbmodem'):
					devices.append( os.path.join('/dev', device))
		
		
		return(devices)
	
	
	##################################################################
	
	def updateSliderConcentration(self):
		
		self.updatePowerThresholds()
	
	
	##################################################################
	
	def updateSliderRelaxation(self):
		
		self.updatePowerThresholds()
	
	
	##################################################################
	
	def updatePowerThresholds(self):
		
		minimum_power = self.configuration.DEFAULT_BLOOM_POWER_MINIMUM
		maximum_power = self.configuration.DEFAULT_BLOOM_POWER_MAXIMUM
		
		# Reset all values to zero
		for index in range(101):
			self.thresholds['concentration'][index] = 0
			self.thresholds['relaxation'][index] = 0
		
		
		concentration_value = self.horizontalSliderBloomConcentration.value()
		
		if concentration_value != 0:
			
			concentration_range = 101 - concentration_value
			
			for x in range(concentration_range):
				
				current_index = x + concentration_value
				if (concentration_value == 100):
					percent_of_max_power = x # don't divide by zero
				else:
					percent_of_max_power = x / (100.0 - concentration_value)
				new_power = minimum_power + ((maximum_power - minimum_power) * percent_of_max_power)
				self.thresholds['concentration'][current_index] = int(new_power)
		
		
		relaxation_value = self.horizontalSliderBloomRelaxation.value()
		
		if relaxation_value != 0:
			relaxation_range = 101 - relaxation_value
			
			for x in range(relaxation_range):
				
				current_index = x + relaxation_value
				if (relaxation_value == 100):
					percent_of_max_power = x # don't divide by zero
				else:
					percent_of_max_power = x / (100.0 - relaxation_value)
				new_power = minimum_power + ((maximum_power - minimum_power) * percent_of_max_power)
				self.thresholds['relaxation'][current_index] = int(new_power)
		
		
		#if self.DEBUG > 2:
			#concentration_keys = self.thresholds['concentration'].keys()
			#concentration_keys.sort()
			#for key in concentration_keys:
				#print "%i: %i" % (key, self.thresholds['concentration'][key])
			
			#print
			#print
			
			#concentration_keys = self.thresholds['relaxation'].keys()
			#concentration_keys.sort()
			#for key in concentration_keys:
				#print "%i: %i" % (key, self.thresholds['relaxation'][key])
	
	
	##################################################################
	
	def processCustomData(self, packet):
		
		return(packet)
	
	
	##################################################################
	
	#def connectToThinkGearHost(self):
		
		#pass
	
	
	##################################################################
	
	#def disconnectFromThinkGearHost(self):
		
		#self.progressBarBloomConcentration.setValue(0)
		#self.progressBarBloomRelaxation.setValue(0)
		#self.progressBarBloomConnectionLevel.setValue(0)
	
	
	##################################################################
	
	def updateEEGProcessingGUI(self):
		
		self.progressBarBloomConcentration.setValue(0)
		self.progressBarBloomRelaxation.setValue(0)
		self.progressBarBloomConnectionLevel.setValue(0)
		
		#self.stopControl()
	
	
	##################################################################
	
	def processPacketEEG(self, packet):
		
		self.processPacketThinkGear(packet)
		#self.processPacketEmotiv(packet)
	
	
	##################################################################
	
	def processPacketThinkGear(self, packet):
		
		if (self.parent.tabWidget.currentIndex() == \
		    self.tabIndex):
		    #self.parent.tabWidget.indexOf(self.parent.tabBloom))
			
			#if ('rawEeg' in packet.keys()):
				##self.parent.packets['rawEeg'].append(packet['rawEeg'])
				##value = packet['rawEeg']
				##if MATPLOTLIB_AVAILABLE and \
				##(self.parent.tabWidget.currentIndex() == self.tabIndex):
					##self.rawEEGMatplot.update_figure(value)
				#return
			
			
			if ('rawEeg' in packet.keys()):
				self.rawEEGMatplot.updateValues(packet['rawEeg'])
				return
			
			
			if ('eSense' in packet.keys()):
				
				#self.processEyeBlinks()
				
				if ('attention' in packet['eSense'].keys()):
					if self.pushButtonBloomConcentrationEnable.isChecked():
						self.progressBarBloomConcentration.setValue(packet['eSense']['attention'])
						
						# Perform custom function for packet data
						#packet = self.processCustomData(packet)
				
				
				if ('meditation' in packet['eSense'].keys()):
					if self.pushButtonBloomRelaxationEnable.isChecked():
						self.progressBarBloomRelaxation.setValue(packet['eSense']['meditation'])
				
				
				self.updateBloomPower()
				#self.updateProgressBarColors()
				
				if MATPLOTLIB_AVAILABLE:
					self.historyEEGMatplot.updateValues('eSense', packet['eSense'])
					if (self.parent.tabWidget.currentIndex() == self.tabIndex):
						self.historyEEGMatplot.updateFigure('eSense', packet['eSense'])
			
			
			if ('poorSignalLevel' in packet.keys()):
				
				if packet['poorSignalLevel'] == 200:
					value = 0
					self.textLabelBloomConnectionLevel.setText('No Contact')
				elif packet['poorSignalLevel'] == 0:
					value = 100
					self.textLabelBloomConnectionLevel.setText('Connected')
				else:
					value = int(100 - ((packet['poorSignalLevel'] / 200.0) * 100))
				#self.textLabelBloomConnectionLevel.setText('Connection Level')
				self.progressBarBloomConnectionLevel.setValue(value)
	
	
	##################################################################
	
	#def processPacketEmotiv(self, packet):
		
		#pass
	
	
	##################################################################
	
	def updateBloomPower(self, new_speed=None):
		
		if new_speed == None:
			
			concentration=self.progressBarBloomConcentration.value()
			relaxation=self.progressBarBloomRelaxation.value()
			
			new_speed = self.calculateSpeed(concentration, relaxation)
		
		
		self.current_power = new_speed
		
		# Update GUI
		#if self.pushButtonControlPowerEnable.isChecked():
			#self.progressBarControlPower.setValue(new_speed)
		
		self.progressBarBloomPower.setValue(new_speed)
		#self.dialBloomPower.setValue(new_speed)
		
		
		self.triggerActions(power=self.current_power)
		
		
	##################################################################
	
	def triggerActions(self, power):
		
		bloomDevice = str(self.comboBoxBloomModelName.currentText())
		
		if power == 0:
			
			if bloomDevice == 'Puzzlebox Bloom':
				
				if self.protocol != None:
					
					concentration = 0
					relaxation = 0
					
					if (self.horizontalSliderBloomConcentration.value() > 0):
						concentration = self.progressBarBloomConcentration.value()
						
					if (self.horizontalSliderBloomRelaxation.value() > 0):
						relaxation = self.progressBarBloomRelaxation.value()
					
					self.protocol.updateBloom(power, concentration, relaxation)
		
		else:
			
			if bloomDevice == 'Puzzlebox Bloom':
				
				if self.protocol != None:
					
					concentration = 0
					relaxation = 0
					
					if (self.horizontalSliderBloomConcentration.value() > 0):
						concentration = self.progressBarBloomConcentration.value()
						
					if (self.horizontalSliderBloomRelaxation.value() > 0):
						relaxation = self.progressBarBloomRelaxation.value()
					
					self.protocol.updateBloom(power, concentration, relaxation)
	
	
	##################################################################
	
	def calculateSpeed(self, concentration, relaxation):
		
		speed = 0
		
		#thresholds = self.configuration.THINKGEAR_POWER_THRESHOLDS
		#thresholds = THINKGEAR_POWER_THRESHOLDS
		
		match = int(concentration)
		
		while ((match not in self.thresholds['concentration'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		
		if match in self.thresholds['concentration'].keys():
			speed = self.thresholds['concentration'][match]
		
		
		match = int(relaxation)
		
		while ((match not in self.thresholds['relaxation'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		if match in self.thresholds['relaxation'].keys():
			speed = speed + self.thresholds['relaxation'][match]
		
		
		# Power settings cannot exceed 100
		# and must be higher than 50
		if (speed > 100):
			speed = 100
		elif (speed < 50):
			speed = 0
		
		
		return(speed)
	
	
	##################################################################
	
	def updateSliderRed(self):
		
		self.updateBloomColor()
	
	
	##################################################################
	
	def updateSliderGreen(self):
		
		self.updateBloomColor()
	
	
	##################################################################
	
	def updateSliderBlue(self):
		
		self.updateBloomColor()
	
	
	##################################################################
	
	def setBloomColor(self, red, green, blue):
	
		self.red = red
		self.green = green
		self.blue = blue
		
		self.horizontalSliderBloomRed.setValue(self.red)
		self.horizontalSliderBloomGreen.setValue(self.green)
		self.horizontalSliderBloomBlue.setValue(self.blue)
		
		if self.protocol != None:
			self.protocol.setColor(self.red, self.green, self.blue)
	
	
	##################################################################
	
	def updateBloomColor(self):
		
		self.red = self.horizontalSliderBloomRed.value()
		self.green = self.horizontalSliderBloomGreen.value()
		self.blue = self.horizontalSliderBloomBlue.value()
		
		if self.protocol != None:
			self.protocol.setColor(self.red, self.green, self.blue)
		
	
	##################################################################
	
	def updateSliderPosition(self):
		
		self.position = self.horizontalSliderBloomPosition.value()
		
		if self.protocol != None:
			self.protocol.setPosition(self.position)
	
	
	##################################################################
	
	def enableBloomClose(self):
		
		if not self.pushButtonBloomClose.isChecked():
			self.pushButtonBloomClose.setChecked(True)
		
		if self.pushButtonBloomOpen.isChecked():
			self.pushButtonBloomOpen.setChecked(False)
			self.disableBloomOpen()
		
		if self.pushButtonBloomCycle.isChecked():
			self.pushButtonBloomCycle.setChecked(False)
			self.disableBloomCycle()
		
		if self.pushButtonBloomDemo.isChecked():
			self.pushButtonBloomDemo.setChecked(False)
			self.disableBloomDemo()
		
		
		self.horizontalSliderBloomRed.setEnabled(True)
		self.horizontalSliderBloomGreen.setEnabled(True)
		self.horizontalSliderBloomBlue.setEnabled(True)
		self.horizontalSliderBloomPosition.setEnabled(True)
		
		
		self.position = 0
		self.horizontalSliderBloomPosition.setSliderPosition(self.position)
		
		if self.protocol != None:
			self.protocol.setPosition(self.position)
		
		
		self.disconnect(self.pushButtonBloomClose, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableBloomClose)
		
		self.connect(self.pushButtonBloomClose, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableBloomClose)
		
		
		# Uncheck close after operation performed
		self.disableBloomClose()
	
	
	##################################################################
	
	def disableBloomClose(self):
		
		if self.pushButtonBloomClose.isChecked():
			self.pushButtonBloomClose.setChecked(False)
		
		self.disconnect(self.pushButtonBloomClose, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableBloomClose)
		
		self.connect(self.pushButtonBloomClose, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomClose)
	
	
	##################################################################
	
	def enableBloomOpen(self):
		
		if not self.pushButtonBloomOpen.isChecked():
			self.pushButtonBloomOpen.setChecked(True)
		
		if self.pushButtonBloomClose.isChecked():
			self.pushButtonBloomClose.setChecked(False)
			self.disableBloomClose()
		
		if self.pushButtonBloomCycle.isChecked():
			self.pushButtonBloomCycle.setChecked(False)
			self.disableBloomCycle()
		
		if self.pushButtonBloomDemo.isChecked():
			self.pushButtonBloomDemo.setChecked(False)
			self.disableBloomDemo()
		
		
		self.horizontalSliderBloomRed.setEnabled(True)
		self.horizontalSliderBloomGreen.setEnabled(True)
		self.horizontalSliderBloomBlue.setEnabled(True)
		self.horizontalSliderBloomPosition.setEnabled(True)

		
		self.position = 100
		self.horizontalSliderBloomPosition.setSliderPosition(self.position)
		
		if self.protocol != None:
			self.protocol.setPosition(self.position)
		
		
		self.disconnect(self.pushButtonBloomOpen, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableBloomOpen)
		
		self.connect(self.pushButtonBloomOpen, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableBloomOpen)
		
		
		# Uncheck open after operation performed
		self.disableBloomOpen()
	
	
	##################################################################
	
	def disableBloomOpen(self):
		
		if self.pushButtonBloomOpen.isChecked():
			self.pushButtonBloomOpen.setChecked(False)
		
		self.disconnect(self.pushButtonBloomOpen, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableBloomOpen)
		
		self.connect(self.pushButtonBloomOpen, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomOpen)
	
	
	##################################################################
	
	def enableBloomCycle(self):
		
		if not self.pushButtonBloomCycle.isChecked():
			self.pushButtonBloomCycle.setChecked(True)
		
		if self.pushButtonBloomOpen.isChecked():
			self.pushButtonBloomOpen.setChecked(False)
			self.disableBloomOpen()
		
		if self.pushButtonBloomClose.isChecked():
			self.pushButtonBloomClose.setChecked(False)
			self.disableBloomClose()
		
		if self.pushButtonBloomDemo.isChecked():
			self.pushButtonBloomDemo.setChecked(False)
			self.disableBloomDemo()
		
		
		self.horizontalSliderBloomRed.setEnabled(False)
		self.horizontalSliderBloomGreen.setEnabled(False)
		self.horizontalSliderBloomBlue.setEnabled(False)
		self.horizontalSliderBloomPosition.setEnabled(False)
		
		
		if self.protocol != None:
			self.protocol.setColorCycle()
		
		
		self.disconnect(self.pushButtonBloomCycle, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableBloomCycle)
		
		self.connect(self.pushButtonBloomCycle, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableBloomCycle)
	
	
	##################################################################
	
	def disableBloomCycle(self):
		
		if self.pushButtonBloomCycle.isChecked():
			self.pushButtonBloomCycle.setChecked(False)
		
		
		self.horizontalSliderBloomRed.setEnabled(True)
		self.horizontalSliderBloomGreen.setEnabled(True)
		self.horizontalSliderBloomBlue.setEnabled(True)
		self.horizontalSliderBloomPosition.setEnabled(True)
		
		
		self.disconnect(self.pushButtonBloomCycle, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableBloomCycle)
		
		self.connect(self.pushButtonBloomCycle, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomCycle)
	
	
	##################################################################
	
	def enableBloomDemo(self):
		
		if not self.pushButtonBloomDemo.isChecked():
			self.pushButtonBloomDemo.setChecked(True)
		
		if self.pushButtonBloomOpen.isChecked():
			self.pushButtonBloomOpen.setChecked(False)
			self.disableBloomOpen()
		
		if self.pushButtonBloomClose.isChecked():
			self.pushButtonBloomClose.setChecked(False)
			self.disableBloomClose()
			
		if self.pushButtonBloomCycle.isChecked():
			self.pushButtonBloomCycle.setChecked(False)
			self.disableBloomCycle()
		
		
		self.horizontalSliderBloomRed.setEnabled(False)
		self.horizontalSliderBloomGreen.setEnabled(False)
		self.horizontalSliderBloomBlue.setEnabled(False)
		self.horizontalSliderBloomPosition.setEnabled(False)
		
		
		if self.protocol != None:
			self.protocol.setDemoMode()
		
		
		self.disconnect(self.pushButtonBloomDemo, \
		                QtCore.SIGNAL("clicked()"), \
		                self.enableBloomDemo)
		
		self.connect(self.pushButtonBloomDemo, \
		             QtCore.SIGNAL("clicked()"), \
		             self.disableBloomDemo)
	
	
	##################################################################
	
	def disableBloomDemo(self):
		
		if self.pushButtonBloomDemo.isChecked():
			self.pushButtonBloomDemo.setChecked(False)
		
		
		self.horizontalSliderBloomRed.setEnabled(True)
		self.horizontalSliderBloomGreen.setEnabled(True)
		self.horizontalSliderBloomBlue.setEnabled(True)
		self.horizontalSliderBloomPosition.setEnabled(True)
		
		
		self.disconnect(self.pushButtonBloomDemo, \
		                QtCore.SIGNAL("clicked()"), \
		                self.disableBloomDemo)
		
		self.connect(self.pushButtonBloomDemo, \
		             QtCore.SIGNAL("clicked()"), \
		             self.enableBloomDemo)
	
	
	##################################################################
	
	def stop(self):
		
		self.triggerActions(power=0)
		
		self.disconnectBloomDevice()


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

#if __name__ == '__main__':
	
	#pass

