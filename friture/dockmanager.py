from PyQt4 import QtCore
from PyQt4.QtGui import QMainWindow
from friture.defaults import DEFAULT_DOCKS
from friture.dock import Dock

class DockManager(QtCore.QObject):
	def __init__(self, parent, logger):
		QtCore.QObject.__init__(self, parent)

		# the parent must of the QMainWindow so that docks are created as children of it
		assert(isinstance(parent, QMainWindow))

		self.docks = []
		self.logger = logger


	# slot
	def new_dock(self):
		# the dock objectName is unique
		docknames = [dock.objectName() for dock in self.docks]
		dockindexes = [int(str(name).partition(' ')[-1]) for name in docknames]
		if len(dockindexes) == 0:
			index = 1
		else:
			index = max(dockindexes)+1
		name = "Dock %d" %index
		new_dock = Dock(self.parent(), self.logger, name)
		self.parent().addDockWidget(QtCore.Qt.TopDockWidgetArea, new_dock)
		
		self.docks += [new_dock]
	
	#slot
	def close_dock(self, dock):
		self.docks.remove(dock)


	def saveState(self, settings):
		docknames = [dock.objectName() for dock in self.docks]
		settings.setValue("dockNames", docknames)
		for dock in self.docks:
			settings.beginGroup(dock.objectName())
			dock.saveState(settings)
			settings.endGroup()


	def restoreState(self, settings):
		if settings.contains("dockNames"):
			docknames = settings.value("dockNames", []).toList()
			docknames = [dockname.toString() for dockname in docknames]
			# list of docks
			self.docks = [Dock(self.parent(), self.logger, name) for name in docknames]
			for dock in self.docks:
				settings.beginGroup(dock.objectName())
				dock.restoreState(settings)
				settings.endGroup()
		else:
			self.logger.push("First launch, display a default set of docks")
			self.docks = [Dock(self.parent(), self.logger, "Dock %d" %(i), type = type) for i, type in enumerate(DEFAULT_DOCKS)]
			for dock in self.docks:
				self.parent().addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)


	def update(self):
		for dock in self.docks:
			dock.update()
