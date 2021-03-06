"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

#if (sys.platform != "win32") and hasattr(sys, 'frozen'):
  #root.tk.call('console', 'hide')

from setuptools import setup
import PySide

APP = ['bloom-gui.py']

data_files=[ \
	(".", \
	#("Content/Resources", \
		["puzzlebox_bloom_configuration.ini"]),
	("images", \
		["images/puzzlebox.ico", \
			"images/puzzlebox.icns", \
			"images/puzzlebox_logo.png", \
			"images/bloom-cycle.svg", \
			"images/bloom-open.svg", \
			"images/bloom-close.png", \
			"images/bloom-cycle.png", \
			"images/bloom-demo.png", \
			"images/bloom-open.png", \
			"images/puzzlebox_bloom.png", \
		]), \
	#("audio", \
		#["audio/throttle_hover_os_x.wav", \
		#]), \
	#("qt_menu.nib", \
		#["/opt/local/lib/Resources/qt_menu.nib/classes.nib", \
			#"/opt/local/lib/Resources/qt_menu.nib/info.nib", \
			#"/opt/local/lib/Resources/qt_menu.nib/keyedobjects.nib", \
		#]), \
]

data_files=[]

OPTIONS = { \
	#'argv_emulation': True, \
	'argv_emulation': False, \
	'iconfile': 'images/puzzlebox.icns', \
	'strip': True, \
	
	# Semi-standalone is an option you can enable with py2app that makes 
	# your code reliant on the version of Python that is installed with the OS.
	# You also need to enable site-packages, as well (which apparently encourages
	# py2app to create the links to Python necessary for getting the bundle up
	# and running, although it's only supposed to tell it to include the
	# system and user site-packages in the system path)
	# http://beckism.com/2009/03/pyobjc_tips/
	
	#'semi_standalone': True, \
	#'site_packages': True, \
	
	'includes': [ \
		'PySide', \
		'PySide.QtSvg', \
	], \
	
#	'excludes': ['PyQt4', 'sip'], \
	'excludes': ['PyQt4'], \
	
	'frameworks': [ \
		"/opt/local/share/qt4/plugins/imageformats/libqjpeg.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqgif.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqico.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqmng.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqsvg.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqtiff.dylib", \
	], \
	
	"resources": [ \
		"puzzlebox_bloom_configuration.ini", \
		#"images/puzzlebox.ico", \
		#"/opt/local/lib/Resources/qt_menu.nib/classes.nib", \
		#"/opt/local/lib/Resources/qt_menu.nib/info.nib", \
		#"/opt/local/lib/Resources/qt_menu.nib/keyedobjects.nib", \
	], \
}

setup(
	
	name='Puzzlebox Bloom',
	version='1.6.0',
	description='An integrated bio and neurofeedback marketing solution for web design, content, and software evaluation',
	author='Steve Castellotti',
	author_email='sc@puzzlebox.io',
	url='http://puzzlebox.io',
	
	classifiers=[ \
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: End Users/Desktop',
		'Programming Language :: Python',
		'Operating System :: OS Independent',
		'License :: Commercial',
		'Topic :: Scientific/Engineering :: Human Machine Interfaces',
	],
	
	app=APP,
	data_files=data_files,
	options={'py2app': OPTIONS},
	setup_requires=['py2app'],

)
