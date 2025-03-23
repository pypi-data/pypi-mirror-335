#!/usr/bin/env python

# MIT License

# Copyright (c) 2021-2024 Rafael Arvelo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# This file contains the top level classes for the Data Viewer application
#
# pylint: disable-all

# Standard python modules
import os
import sys
import glob
import json
import argparse
import logging
import subprocess
import platform
import typing
import pkg_resources
from   pathlib     import Path
from   collections import namedtuple

# Application paths
DATAVIEWER_BASE_PATH = os.path.dirname(os.path.realpath(__file__))
REPOSITORY_BASE_PATH = str(Path(DATAVIEWER_BASE_PATH).parent.absolute())
USER_MANUAL_PATH     = os.path.join(DATAVIEWER_BASE_PATH, "docs", "user_manual.pdf")
SAMPLE_DATA_PATH     = os.path.join(DATAVIEWER_BASE_PATH, "data")
IMAGES_PATH          = os.path.join(DATAVIEWER_BASE_PATH, "ui", "images")
APP_ICON_PATH        = os.path.join(IMAGES_PATH, 'app_icon.png')
PASTE_ICON_PATH      = os.path.join(IMAGES_PATH, 'paste.png')
FILE_ICON_PATH       = os.path.join(IMAGES_PATH, 'file2.png')
USER_MANUAL_WEB_LINK = "https://rafyarvelo.gitlab.io/py_data_viewer/index.html"

# Update PYTHONPATH
sys.path.append(DATAVIEWER_BASE_PATH)
sys.path.append(IMAGES_PATH)

# Local python modules
import __version__
from   dataframemodel    import DataFrameModel, DataFrameFactory, PlotInfo, PKG_SETTINGS_PATH, \
                                SETTINGS_DIRECTORY, SETTINGS_FILENAME, getUserSettingsPath
from   dataviewerutils   import QLogger, FileSystemModel, ProgressWidget, DataFrameParserEditor
from   tableviewer       import TableViewer, create_table
from   viewerwindow      import ViewerWindow, WindowInfo
from   mergedialog       import MergeDialog
from   plotviewer        import PlotViewer, create_plot
from   ui.ui_dataviewer  import Ui_DataViewer

# Third-party python modules
import matplotlib.pyplot as plt
from   PyQt5.QtWidgets   import QListWidgetItem, QWidget, QApplication, QMainWindow, QFileDialog, QToolBar, \
                                QAction, QMessageBox, QMenu, QStyleFactory, QFileIconProvider, QActionGroup, QDockWidget, QTabWidget
from   PyQt5.QtGui       import QDragEnterEvent, QDropEvent, QCloseEvent, QIcon, QDesktopServices, QFont
from   PyQt5.QtCore      import Qt, QPoint, QDir, QObject, QSettings, QFileInfo, QUrl, QModelIndex, pyqtSignal, pyqtSlot, QTimer

#####################
# Globals
#####################

# Application information (required for QSetttings)
APPLICATION_NAME     = "Data Viewer"
APPLICATION_VERSION  = __version__.__version__
DEFAULT_LOG_FILENAME = "dataframeviewer.log"
DEFAULT_LOG_FILEPATH = os.path.join(SETTINGS_DIRECTORY, DEFAULT_LOG_FILENAME)
DEFAULT_LOG_FORMAT   = "[%(asctime)s] | %(module)-20s | %(levelname)-8s| %(message)s"
MAX_RECENT_FILES     = 30

# Dictionary mapping Theme names to stylesheets
# Note: Empty strings are equivalent to no stylesheet (default theme)
APPLICATION_THEMES : typing.Dict[str, str] = {
    "Light" : "",
    "Dark"  : ""
}

CHART_THEMES : typing.List[str] = [
    "default",
    "dark_background"
]

#####################
# Helper Functions
#####################

# Read a namedtuple from JSON
def fromJson(json_obj : typing.Union[str, dict], cls : typing.NamedTuple) -> typing.NamedTuple:
    map = None
    obj = None
    if isinstance(json_obj, str) and len(json_obj) > 0:
        map = json.loads(json_obj)
    if isinstance(json_obj, dict):
        map = json_obj
    if isinstance(map, dict) and all([field in map.keys() for field in cls._fields]):
        obj = cls(**map)
    return obj 

# Convert a namedtuple to JSON
def toJson(obj : typing.NamedTuple) -> str:
    map = obj._asdict()
    s   = json.dumps(map)
    return s

#####################
# Classes
#####################

DockWindow = namedtuple('DockWindow', ['info', 'window'])

class DataViewer(QMainWindow):
    FILE_FILTER          = "CSV Files *.csv;;All Files *"
    viewerClosed         = pyqtSignal(str) # absoluteFilePath
    windowClosed         = pyqtSignal(QMainWindow)
    requestNewStyle      = pyqtSignal(str)
    requestNewTheme      = pyqtSignal(str)
    requestNewChartTheme = pyqtSignal(str)
    requestUserManualPDF = pyqtSignal()
    requestUserManualWeb = pyqtSignal()

    def __init__(self, 
                 parent     : QWidget = None,
                 style      : str     = None,
                 theme      : str     = None,
                 chartTheme : str     = None,
                 window_id  : str     = 0):
        super().__init__(parent=parent)
        self.window_id       : int              = window_id
        self.ui              : Ui_DataViewer    = Ui_DataViewer()
        self.fsModel         : FileSystemModel  = FileSystemModel(self)
        self.viewerSettings  : typing.List[WindowInfo]  = []
        self.viewer_windows  : typing.List[DockWindow] = []
        self.fileDockLocked  : bool           = False
        self.currentPath     : str            = ""
        self.recentFiles     : list           = []
        self.recentFolders   : list           = []
        self.open_dir        : bool           = False
        self.requested_files : typing.Dict[str, typing.List[WindowInfo]] = {}
        self.logger          : logging.Logger = logging.getLogger(__name__)
        self.setWindowTitle(f"{APPLICATION_NAME}: v{APPLICATION_VERSION}")
        self.initUI(style, theme, chartTheme)
        self.initFactory()
    
    def initUI(self,
               style      : str = None,
               theme      : str = None,
               chartTheme : str = None):
        self.ui.setupUi(self)
        self.ui.treeView.setModel(self.fsModel)
        self.ui.actionFile.triggered.connect(self.openFiles)
        self.ui.treeView.activated.connect(self.onTreeViewIndexActivated)
        self.ui.tableListWidget.activated.connect(self.onViewerListIndexActivated)
        self.ui.tableListWidget.clicked.connect(self.onViewerListIndexActivated)
        self.ui.showInfoCheckBox.clicked.connect(self.showFileInfo)
        self.ui.actionCloseAll.triggered.connect(self.closeAllViewers)
        self.ui.actionDirectory.triggered.connect(self.openDir)
        self.ui.actionMerge_Tables.triggered.connect(self.onMergeTablesTriggered)
        self.ui.closeAllButton.clicked.connect(self.closeAllViewers)
        self.ui.closeOthersButton.clicked.connect(self.closeOtherViewers)
        self.ui.fileFilterLine.textChanged.connect(self.setNameFilters)
        self.ui.showAllCheckBox.clicked.connect(self.setShowAll)
        self.ui.actionRestoreViewers.triggered.connect(self.restorePreviousViewers)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.onTreeViewContextMenuRequested)
        self.ui.actionAbout.triggered.connect(self.requestUserManualPDF)
        self.ui.actionSave_Windows.triggered.connect(self.saveWindowSettingsToFile)
        self.ui.actionLoad_Window_Settings.triggered.connect(self.readWindowSettingsFromFile)
        self.ui.actionUser_Manual_PDF.triggered.connect(self.requestUserManualPDF)
        self.ui.actionUser_Manual_Web.triggered.connect(self.requestUserManualWeb)
        self.ui.actionFileParserSettings.triggered.connect(self.showParserEditor)

        self.recentsMenu       : QMenu          = None
        self.recentFilesMenu   : QMenu          = None
        self.recentFoldersMenu : QMenu          = None
        self.progressWidget    : ProgressWidget = ProgressWidget(parent=self.statusBar())
        self.progressWidget.hide()

        self.setNameFilters(self.ui.fileFilterLine.text())
        self.setShowAll(self.ui.showAllCheckBox.isChecked())
        self.setAcceptDrops(True)
        self.showFileInfo(False)
        self.setupToolBars()
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.statusBar().addPermanentWidget(self.progressWidget)

        for w in [self.ui.treeView, self.ui.fileExplorerDock]:
            w.dragEnterEvent = self.dragEnterEvent
            w.dropEvent      = self.dropEvent

        # Add application Style Group
        self.appStyleGroup = QActionGroup(self)
        for styleName in QStyleFactory.keys():
            action = self.ui.menuApplication_Style.addAction(styleName)
            action.setCheckable(True)
            action.setChecked(bool(styleName == style))
            self.appStyleGroup.addAction(action)
        self.appStyleGroup.triggered.connect(self.onStyleChanged)

        # Add application theme group
        self.appThemeGroup = QActionGroup(self)
        for themeName in APPLICATION_THEMES.keys():
            action = self.ui.menuApplication_Theme.addAction(themeName)
            action.setCheckable(True)
            if themeName != "Light" and len(APPLICATION_THEMES[themeName]) == 0:
                action.setEnabled(False)
                action.setChecked(False)
            else:
                action.setChecked(bool(themeName == theme))
            self.appThemeGroup.addAction(action)
        self.appThemeGroup.triggered.connect(self.onThemeChanged)

        # Add chart theme group
        self.chartThemeGroup = QActionGroup(self)
        for themeName in CHART_THEMES:
            action = self.ui.menuChart_Theme.addAction(themeName)
            action.setCheckable(True)
            action.setChecked(bool(themeName == chartTheme))
            self.chartThemeGroup.addAction(action)
        self.chartThemeGroup.triggered.connect(self.onChartThemeChanged)
    
    def setupToolBars(self):
        fileToolBar = QToolBar("File Tools", self)
        fileToolBar.setObjectName("fileToolBar")
        fileToolBar.addActions([self.ui.actionAbout, self.ui.actionFile, self.ui.actionDirectory, \
                                self.ui.actionSave_Windows, self.ui.actionLoad_Window_Settings])

        windowToolBar = QToolBar("Window Tools", self)
        windowToolBar.setObjectName("windowToolBar")
        windowToolBar.addActions([self.ui.actionRestoreViewers, self.ui.actionNewWindow, self.ui.actionMerge_Tables, 
                                  self.ui.actionFileParserSettings, self.ui.actionExit])

        self.addToolBar(Qt.LeftToolBarArea, fileToolBar)
        self.addToolBar(Qt.LeftToolBarArea, windowToolBar)

    def initFactory(self):
        self.factory = DataFrameFactory.getInstance()
        self.factory.progressStarted.connect(self.progressWidget.startProgress)
        self.factory.progressUpdate.connect(self.progressWidget.updateProgress)
        self.factory.progressMessage.connect(self.progressWidget.updateProgressMsg)
        self.factory.progressFinished.connect(self.progressWidget.finishProgress)
        self.progressWidget.cancelled.connect(self.factory.onCancel)
        self.viewerClosed.connect(self.factory.onModelClosed)
        self.factory.modelCreated.connect(self.openModel)
    
    # Function to dynamically create a menu of all the table settings
    def createTableSettingsMenu(self, parent : QMenu, filename : str) -> None:
        
        # Icon to use for sub-menus and actions
        file_icon = QIcon(FILE_ICON_PATH)

        # Nested recursive function to create submenus from a folder path
        def createSubMenus(parent : QMenu, folder_path : str):
            info = QFileInfo(folder_path)
            if info.exists() and info.isDir():
                file_list = list(glob.glob(f"{folder_path}/*"))
                if len(file_list) > 0:
                    for file_path in file_list:
                        file_info = QFileInfo(file_path)
                        if file_info.isDir():
                            # Recursively create menus for this subdirectory
                            sub_menu = parent.addMenu(file_info.baseName())
                            createSubMenus(parent=sub_menu, folder_path=file_info.absoluteFilePath())
                        elif file_info.isFile():
                            if file_info.fileName().endswith(".json"):
                                open_action = parent.addAction(file_icon, file_info.baseName(), self.openWithCustomSettings) 
                                open_action.setData( { "filename" : filename,
                                                    "settings_filename" : file_info.absoluteFilePath() })
                        else:
                            self.logger.debug(f"Ignoring unknown table settings file {file_info.fileName()}")

        # Create the sub-menus for the table settings
        user_settings_path = getUserSettingsPath()
        if os.path.exists(user_settings_path):
            files = list(glob.glob(f"{user_settings_path}/**/*.json", recursive=True))
            if len(files) > 0:
                file_icon     = QIcon(FILE_ICON_PATH)
                settings_menu = parent.addMenu(file_icon, "Open File with Custom Settings")
                createSubMenus(parent=settings_menu, folder_path=user_settings_path)

    @pyqtSlot(QPoint)
    def onTreeViewContextMenuRequested(self, pos : QPoint):
        index = self.ui.treeView.indexAt(pos)
        if index.isValid():
            context_menu  = QMenu(self.ui.treeView)
            info          = self.fsModel.fileInfo(index)
            
            # Add file-specific actions
            if info.isFile():
                open_file_action = context_menu.addAction(self.windowIcon(), "Open Table", self.openFileFromAction) 
                open_plot_action = context_menu.addAction(QIcon(":/plot.png"), "Open Plot", self.openFileFromAction) 
                open_file_action.setData(WindowInfo("table", info.absoluteFilePath(), {}))
                open_plot_action.setData(WindowInfo("plot", info.absoluteFilePath(), {}))
                open_file_action.setToolTip(info.absoluteFilePath())
                open_plot_action.setToolTip(info.absoluteFilePath())

                if info.fileName().endswith(".csv"):
                    python_icon = QFileIconProvider().icon(QFileInfo(sys.executable))
                    if python_icon.isNull():
                       python_icon = self.windowIcon()
                    open_terminal_action = context_menu.addAction(python_icon, "Open in Python Interpreter", self.openFileInPythonInterpreter) 
                    open_terminal_action.setData(info.absoluteFilePath())
                
                # Add a sub-menu to open the file with custom table settings
                self.createTableSettingsMenu(parent=context_menu, filename=info.absoluteFilePath())
            else:
                # Add folder only options
                open_folder_action = context_menu.addAction(self.fsModel.fileIcon(index), "Open Folder", self.openFolderFromAction) 
                open_folder_action.setData(info.absoluteFilePath())

            # Add actions common for file and folders
            open_sys_action = context_menu.addAction(self.fsModel.fileIcon(index), "Open with System Editor", self.openWithSystemEditor) 
            open_sys_action.setData(info.absoluteFilePath())

            copy_path_icon   = QIcon(PASTE_ICON_PATH)
            copy_path_action = context_menu.addAction(copy_path_icon, "Copy Path to Clipboard", self.copyPathToClipBoard) 
            copy_path_action.setData(info.absoluteFilePath())

            # Add other options
            parent_path  = info.absolutePath()
            parent_index = self.fsModel.index(parent_path)
            if parent_index.isValid():
                open_parent_action = context_menu.addAction(self.fsModel.fileIcon(parent_index), "Open Parent Folder", self.openWithSystemEditor) 
                open_parent_action.setData(parent_path)
            context_menu.popup(self.ui.treeView.mapToGlobal(pos))
    
    def closeOtherViewers(self, window : QDockWidget = None):
        if isinstance(window, QDockWidget) :
            windows = [t.window for t in self.viewer_windows]
            idx = windows.index(window) if window in windows else -1
        else:
            indexes = self.ui.tableListWidget.selectedIndexes()
            idx     = indexes[0].row() if len(indexes) > 0 else -1
        if idx > -1 and idx < len(self.viewer_windows):
            dock_window = self.removeViewer(idx, delete=False)
            self.closeAllViewers()
            self.addDockWindow(dock_window)
    
    @pyqtSlot(int, str)
    def onMessageLogged(self, level : int, message : str):
        if (level >= logging.CRITICAL):
            QMessageBox.critical(self, "Critical Error Received", message)
        elif (level >= logging.ERROR):
            self.statusBar().showMessage(message, 6000)
        elif (level >= logging.INFO):
            self.statusBar().showMessage(message, 3000)
        else:
            # Ignore Debug messages
            pass
    
    def closeEvent(self, e : QCloseEvent) -> None:
        self.windowClosed.emit(self)
        return super().closeEvent(e)

    @pyqtSlot(DataFrameModel)
    def openModel(self, model : DataFrameModel):

        # Open all the windows for this file
        requested_windows = self.requested_files.get(model.filename, [])
        while len(requested_windows) > 0:

            # Get the Window information
            window_info = requested_windows.pop(0)

            # Update the status bar
            file_info = QFileInfo(model.filename)
            self.statusBar().showMessage(f"Opening {window_info.type} for {file_info.fileName()}...")
            if file_info.isFile() and self.open_dir:
                self.openDir(file_info.absolutePath())

            # Add the viewer window
            self.addViewer(model, window_info)

            # Update UI based on how many tables are open
            factory = DataFrameFactory.getInstance()
            self.ui.actionMerge_Tables.setEnabled(len(factory.models.keys()) > 1)
            self.ui.actionSave_Windows.setEnabled(len(self.viewer_windows) > 0)

        self.statusBar().clearMessage()

    # Function to open a file with the default system editor
    def copyPathToClipBoard(self, filename : str = None) -> bool:
        if not(isinstance(filename, str)) or not(os.path.exists(filename)):
            act = self.sender()
            if isinstance(act, QAction):
                filename = act.data()
        if isinstance(filename, str) and os.path.exists(filename):
            clipboard = QApplication.clipboard()
            clipboard.setText(filename)
            return bool(clipboard.text() == filename)
        return False
    
    # Function to open a file with the default system editor
    def openWithSystemEditor(self, filename : str = None) -> bool:
        if not(isinstance(filename, str)) or not(os.path.exists(filename)):
            act = self.sender()
            if isinstance(act, QAction):
                filename = act.data()
        if isinstance(filename, str) and os.path.exists(filename):
            return QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        return False
    
    # Function to open a CSV in a new python terminal
    def openFileInPythonInterpreter(self, filename : str = None) -> bool:
        if not(isinstance(filename, str)) or not(os.path.exists(filename)):
            act = self.sender()
            if isinstance(act, QAction):
                filename = act.data()
        if isinstance(filename, str) and os.path.exists(filename):
            script_text = f"import pandas as pd; df = pd.read_csv('{filename}', encoding='latin1'); df.head()"
            kwargs      = {}
            if "windows" in platform.platform().lower():
                kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen([sys.executable, "-i", "-c", script_text], env=os.environ, **kwargs)
            return True
        return False
    
    def dragEnterEvent(self, e : QDragEnterEvent) -> None:
        if e.mimeData().hasUrls() or e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()
        return super().dragEnterEvent(e)
    
    def dropEvent(self, e : QDropEvent) -> None:
        m = e.mimeData()
        if m.hasUrls():
            filePaths = [url.path() for url in m.urls()]
        elif m.hasText():
            filePaths = [m.text()]
        else:
            self.logger.debug(f"Drop Event type not supported: {e}")
            filePaths = []
        
        # Fix file paths on Windows
        if 'Windows' in platform.platform():
            for i in range(len(filePaths)):
                if len(filePaths[i]) > 0 and filePaths[i][0] == '/':
                    filePaths[i] = filePaths[i][1:]

        # Separate files and folders
        info    = [QFileInfo(f) for f in filePaths]
        files   = [i.absoluteFilePath() for i in info if i.exists() and i.isFile()]
        folders = [i.absoluteFilePath() for i in info if i.exists() and i.isDir()]
        viewer_info = [WindowInfo("table", f, {}) for f in files]

        # Open the files
        if len(viewer_info) > 0:
            self.open_dir = True
            self.openFiles(viewer_info)
        
        # Open only the last directory since only 1 directory can be open at a time
        if len(folders) > 0:
            self.openDir(folders[-1])

        return super().dropEvent(e)

    @pyqtSlot(str)
    def setNameFilters(self, filterStr : str = ''):
        if isinstance(filterStr, str) and filterStr != '':
            filters = filterStr.split(';')
            self.fsModel.setNameFilters(filters)
        else:
            self.logger.warning(f"Invalid filter str \"{filterStr}\"")

    def addRecentFile(self, filename : str):

        if isinstance(filename, str) and len(filename) > 0:
            info = QFileInfo(filename)
            if info.exists() and not(info.isDir()):

                if self.recentsMenu is None:
                    self.recentsMenu = self.ui.menuOpen.addMenu("Open Recents")
                
                if self.recentFilesMenu is None:
                    self.recentFilesMenu = self.recentsMenu.addMenu("Recent Files")
            
                if not(info.absoluteFilePath() in self.recentFiles):
                    act = self.recentFilesMenu.addAction(info.absoluteFilePath(), self.openFileFromAction)
                    act.setData(WindowInfo("table", info.absoluteFilePath(), {}))
                    act.setToolTip(info.absoluteFilePath())
                    self.recentFiles.append(info.absoluteFilePath())

    def addRecentFolder(self, filename : str):
        if isinstance(filename, str) and len(filename) > 0:
            info = QFileInfo(filename)
            if info.exists() and info.isDir():

                if self.recentsMenu is None:
                    self.recentsMenu = self.ui.menuOpen.addMenu("Open Recents")
                
                if self.recentFoldersMenu is None:
                    self.recentFoldersMenu = self.recentsMenu.addMenu("Recent Folders")
            
                if not(info.absoluteFilePath() in self.recentFolders):
                    act = self.recentFoldersMenu.addAction(info.absoluteFilePath(), self.openFileFromAction)
                    act.setData(WindowInfo("table", info.absoluteFilePath(), {}))
                    act.setToolTip(info.absoluteFilePath())
                    self.recentFolders.append(info.absoluteFilePath())

    def setRecentFiles(self, recents : list = []):
        if isinstance(recents, list) and len(recents) > 0:
            for f in recents:
                self.addRecentFile(f)
        else:
            self.logger.warning(f"Invalid recents list in \"setRecentFiles()\": {recents}")

    def setRecentFolders(self, recents : list = []):
        if isinstance(recents, list) and len(recents) > 0:
            for f in recents:
                self.addRecentFolder(f)
        else:
            self.logger.warning(f"Invalid recents list in \"setRecentFolders()\": {recents}")

    @pyqtSlot(bool)
    def setShowAll(self, showAll : bool):
        self.fsModel.setNameFilterDisables(showAll)

    @pyqtSlot(QAction)
    def onStyleChanged(self, action : QAction):
        style = action.text()
        self.requestNewStyle.emit(style)

    @pyqtSlot(QAction)
    def onThemeChanged(self, action : QAction):
        theme = action.text()
        self.requestNewTheme.emit(theme)

    @pyqtSlot(QAction)
    def onChartThemeChanged(self, action : QAction):
        theme = action.text()
        self.requestNewChartTheme.emit(theme)
    
    def saveWindowSettings(self) -> typing.List[dict]:
        """Return the current Window Settings in JSON format"""
        self.viewerSettings = []
        json_settings       = []
        for item in self.viewer_windows:
            widget = item.window.widget()
            if isinstance(widget, TableViewer):
                widget.updateSettings() # Update the table settings
                viewer_settings = widget.settings
            elif isinstance(widget, PlotViewer):
                viewer_settings = widget.getSettings()
            else:
                viewer_settings = item.info.settings if isinstance(item.info.settings, dict) else {}
            viewer_settings["objectName"] = item.window.objectName()
            info = WindowInfo(item.info.type, item.info.filename, viewer_settings)
            self.viewerSettings.append(info)
            json_settings.append(toJson(info))
        return json_settings
    
    @pyqtSlot()
    def saveWindowSettingsToFile(self, filepath : str = None):
        """Save the Window Settings to an INI file"""
        user_settings_path = getUserSettingsPath()
        if not(isinstance(filepath, str)) or filepath == '':
            filepath = QFileDialog.getSaveFileName(self, "Save window settings to file", user_settings_path, "INI Files *.ini;;All Files *")[0]
        if isinstance(filepath, str) and len(filepath) > 0:
            settings  = QSettings(filepath, QSettings.IniFormat)
            self.writeSettings(settings)
            settings.sync()
            self.statusBar().showMessage(f"Sucessfully created {filepath}", 4000)
    
    @pyqtSlot()
    def readWindowSettingsFromFile(self, filepath : str = None):
        """Read the Window Settings from an INI file"""
        user_settings_path = getUserSettingsPath()
        if not(isinstance(filepath, str)) or filepath == '':
            filepath = QFileDialog.getOpenFileName(self, "Select window settings file", user_settings_path, "INI Files *.ini;;All Files *")[0]
        if isinstance(filepath, str) and len(filepath) > 0:
            settings  = QSettings(filepath, QSettings.IniFormat)
            self.readSettings(settings)
            if self.ui.actionRestoreViewers.isEnabled():
                self.restorePreviousViewers()
    
    def readSettings(self, settings : QSettings):
        keys = settings.allKeys()

        # Convenience function to set a value from settings
        def setValue(key, func, type = None, **kwargs):
            groupKey = f"windowSettings/{self.window_id+1}/{key}"
            if key in keys or groupKey in keys:
                value  = settings.value(key)
                if value != None:
                    if type != None:
                        if type == bool:
                            value = bool(value == 'true' or value == 'True' or (isinstance(value, bool) and value))
                        else:
                            value = type(value)
                    func(value, **kwargs)
        
        self.setObjectName(f"data_viewer_window_{self.window_id}")
        self.window_state = settings.value("state")
        setValue('pos'          , self.move)
        setValue('size'         , self.resize)
        setValue('showAll'      , self.ui.showAllCheckBox.setChecked, bool)
        setValue('showAll'      , self.setShowAll, bool)
        setValue('showFileInfo' , self.ui.showInfoCheckBox.setChecked, bool)
        setValue('showFileInfo' , self.showFileInfo, bool)
        setValue('fileFilters'  , self.ui.fileFilterLine.setText, str)
        setValue('fileFilters'  , self.setNameFilters, str)
        viewerSettings = settings.value('viewerSettings', defaultValue=[])
        if viewerSettings is None:
            viewerSettings = []
        for s in viewerSettings:
            info = fromJson(s, WindowInfo)
            if isinstance(info, WindowInfo):
                self.viewerSettings.append(info)
        if not(isinstance(self.viewerSettings, list)) or len(self.viewerSettings) < 1 or any([i == None for i in self.viewerSettings]):
            self.ui.actionRestoreViewers.setVisible(False)
            self.ui.actionRestoreViewers.setEnabled(False)
        else:
            self.ui.actionRestoreViewers.setVisible(True)
            self.ui.actionRestoreViewers.setEnabled(True)

        currentPath = settings.value('currentPath')
        if isinstance(currentPath, str) and os.path.exists(currentPath):
            self.openDir(currentPath)
        else:
            self.openDir(QDir.currentPath())

    def writeSettings(self, settings : QSettings):

        settings.setValue('pos'          , self.pos())
        settings.setValue('size'         , self.size())
        settings.setValue('state'        , self.saveState())
        settings.setValue('showAll'      , bool(self.ui.showAllCheckBox.isChecked()))
        settings.setValue('showFileInfo' , bool(self.ui.showInfoCheckBox.isChecked()))
        settings.setValue('fileFilters'  , self.ui.fileFilterLine.text())
        settings.setValue('currentPath'  , self.currentPath)
        settings.setValue('viewerSettings', self.saveWindowSettings())
    
    @pyqtSlot()
    def restorePreviousViewers(self):
        if isinstance(self.viewerSettings, list) and len(self.viewerSettings) > 0:
            info = self.viewerSettings.copy()
            self.viewerSettings = []
            self.openFiles(info)
            self.ui.actionRestoreViewers.setVisible(False)
            if hasattr(self, "window_state") and self.window_state:
                self.restoreState(self.window_state)

    @pyqtSlot(bool)
    def showFileInfo(self, show : bool):
        for i in range(1, 5):
            self.ui.treeView.setColumnHidden(i, show == False)
    
    @pyqtSlot()
    def showParserEditor(self):
        self.parserEditor = DataFrameParserEditor()
        self.parserEditor.show()
    
    @pyqtSlot()
    def closeAllViewers(self):
        while (len(self.viewer_windows) > 0):
            self.viewer_windows[0].window.close()
    
    @pyqtSlot(QModelIndex)
    def onTreeViewIndexActivated(self, index : QModelIndex):
        filename = self.fsModel.filePath(index)
        if self.fsModel.fileInfo(index).isFile():
            self.open_dir = False
            self.openFiles([WindowInfo("table", filename, {})])

    @pyqtSlot(QModelIndex)
    def onViewerListIndexActivated(self, index : QModelIndex):
        if index.isValid():
            idx = index.row()
            if idx > -1 and idx < len(self.viewer_windows):
                self.viewer_windows[idx].window.raise_()
    
    @pyqtSlot(str)
    def removeViewerByName(self, name : str, delete : bool = True) -> DockWindow:
        for i in range(len(self.viewer_windows)):
            if self.viewer_windows[i].info.filename == name:
                return self.removeViewer(i, delete)
        return None

    @pyqtSlot(int)
    def removeViewer(self, i : int, delete : bool = True) -> DockWindow:
        viewer = None
        if i > -1 and i < len(self.viewer_windows):

            # Remove viewer from viewer list
            viewer = self.viewer_windows[i]
            self.viewer_windows.remove(viewer)

            # Remove row from Table List Widget
            if i < self.ui.tableListWidget.count():
                item = self.ui.tableListWidget.takeItem(i)
            else:
                item = None
            
            # Delete the viewer from RAM
            if delete:
                filename = viewer.info.filename
                del viewer
                viewer = None
                self.viewerClosed.emit(filename)
                if not(item is None):
                    del item
                
                # Only allow merges when 2 or more tables are open
                factory = DataFrameFactory.getInstance()
                self.ui.actionMerge_Tables.setEnabled(len(factory.models.keys()) > 1)
                self.ui.actionSave_Windows.setEnabled(len(self.viewer_windows) > 0)
        
        if len(self.viewer_windows) < 1:
            self.ui.centralwidget.show()

        return viewer 

    @pyqtSlot()
    def openFolderFromAction(self):
        act = self.sender()
        if isinstance(act, QAction):
            info = act.data()
            if (isinstance(info, str)):
                file_info = QFileInfo(info)
                if file_info.exists() and file_info.isDir():
                    self.openDir(file_info.absoluteFilePath())

    @pyqtSlot()
    def openFileFromAction(self):
        act = self.sender()
        if isinstance(act, QAction):
            info = act.data()
            if (isinstance(info, WindowInfo)):
                file_info = QFileInfo(info.filename)
                if file_info.exists():
                    if file_info.isDir():
                        self.openDir(file_info.absoluteFilePath())
                    else:
                        self.open_dir = True
                        self.openFiles([info])

    @pyqtSlot()
    def openWithCustomSettings(self):
        act = self.sender()
        if isinstance(act, QAction):
            data = act.data()
            if isinstance(data, dict):
                file_info     = QFileInfo(data.get("filename", ""))
                settings_info = QFileInfo(data.get("settings_filename", ""))
                if settings_info.exists() and settings_info.isFile():
                    try:
                        with open(settings_info.absoluteFilePath(), 'r') as file:
                            settings_data = json.load(file)
                    except:
                        settings_data = {}
                        self.logger.error(f"Error reading settings from {settings_info.fileName()}")

                    if isinstance(settings_data, dict) and file_info.exists() and file_info.isFile():
                        self.open_dir = False
                        window_info = WindowInfo(settings_data.get("viewer_type", "table"), file_info.absoluteFilePath(), settings_data)
                        self.openFiles([window_info])
    
    def addDockWindow(self, dock_window : DockWindow):

        # Add file to list widget
        filename = dock_window.window.info.filename
        index = self.fsModel.index(filename)
        if index.isValid():
            item = QListWidgetItem(self.fsModel.fileIcon(index), dock_window.window.windowTitle(), self.ui.tableListWidget)
            item.setData(Qt.ToolTipRole, filename)
        else:
            item = dock_window.window.windowTitle()
        self.ui.tableListWidget.addItem(item)

        self.__lockFileDock()
        if not(self.restoreDockWidget(dock_window.window)):
            if len(self.viewer_windows) > 0:
                self.tabifyDockWidget(self.viewer_windows[-1].window, dock_window.window)
            else:    
                # Temporarily lock the width of the file exploer dock so it doesn't resize
                self.addDockWidget(Qt.RightDockWidgetArea, dock_window.window)

        dock_window.window.show()
        dock_window.window.raise_()
        self.viewer_windows.append(dock_window) 
    
    def addPlot(self, model : DataFrameModel, info : PlotInfo = None):
        """Create a new PlotViewer from the model"""
        # Create a new PlotViewer widget
        if not(isinstance(info, PlotInfo)):
            info = PlotInfo()
        plot = create_plot(model, info)
        plot.requestNewPlot.connect(self.onNewPlotRequested)

        return plot

    def addTable(self, model : DataFrameModel, info : WindowInfo = None):
        """Create a new TableViewer from the model"""
        table = create_table(model)
        table.requestNewPlot.connect(self.onNewPlotRequested)
        if isinstance(info, WindowInfo) and isinstance(info.settings, dict):
            table.setSettings(info.settings)
        return table

    @pyqtSlot(DataFrameModel, PlotInfo)
    def onNewPlotRequested(self, model : DataFrameModel, info : PlotInfo):
        """Create a new PlotViewer from the model"""
        # Create a new PlotViewer widget
        if isinstance(info, PlotInfo):
            self.addViewer(model, WindowInfo("plot", model.filename, info.to_dict()))
    
    def addViewer(self, model : DataFrameModel, info : WindowInfo):
        """Create a new ViewerWindow from the model"""
        
        # Open a new table by default
        if not(isinstance(info, WindowInfo)):
            info = WindowInfo("table", model.filename, {})
        
        if info.type == "plot":
            widget = self.addPlot(model, PlotInfo.from_dict(info.settings))
        else:
            widget = self.addTable(model, info)

        # Add file to recents
        self.addRecentFile(model.filename)

        # Create a new DockWidget for the viewer
        viewer = ViewerWindow(title=widget.windowTitle(), widget=widget, info=info)
        viewer.aboutToClose.connect(self.onDockWindowClosed)
        viewer.requestCloseAll.connect(self.closeAllViewers)
        viewer.requestCloseOthers.connect(self.closeOtherViewers)
        viewer.requestArea.connect(self.moveDockWindow)

        if "objectName" in info.settings.keys():
            viewer.setObjectName(info.settings["objectName"])

        # Add the Dock Window
        window = DockWindow(info=info, window=viewer)

        self.addDockWindow(window)

    @pyqtSlot()
    def __lockFileDock(self):
        if not(self.fileDockLocked):
            self.fileDockLocked = True
            self.dock_width     = self.ui.fileExplorerDock.width()
            self.dock_max_width = self.ui.fileExplorerDock.maximumWidth()
            self.ui.fileExplorerDock.setMaximumWidth(self.dock_width)
            self.ui.centralwidget.hide()
            QTimer.singleShot(500, self.__unlockFileDock)

    @pyqtSlot()
    def __unlockFileDock(self):
        if self.fileDockLocked:
            self.ui.fileExplorerDock.setMaximumWidth(self.dock_max_width)
            self.resizeDocks([self.ui.fileExplorerDock], [self.dock_width], Qt.Horizontal)
            self.fileDockLocked = False

    @pyqtSlot(QDockWidget, Qt.DockWidgetArea)
    def moveDockWindow(self, window : QDockWidget, area : Qt.DockWidgetArea):
        if isinstance(window, QDockWidget):

            # Remove the window from it's current location
            self.removeDockWidget(window)
            
            if area == Qt.DockWidgetArea.NoDockWidgetArea:
                window.setFloating(True)
            else:
                # Check if any dock widgets are in the area
                first = None
                for item in reversed(self.viewer_windows):
                    if self.dockWidgetArea(item.window) == area:
                        first = item.window
                        break

                # Add the widget to the new location
                if first:
                    self.tabifyDockWidget(first, window)
                else:
                    self.addDockWidget(area, window)
                
            window.show()
            window.raise_()
    
    @pyqtSlot(QDockWidget)
    def onDockWindowClosed(self, window : QDockWidget):
        windows = [item.window for item in self.viewer_windows]
        idx     = windows.index(window) if window in windows else -1
        if idx > -1:
            self.removeViewer(idx)

    @pyqtSlot()
    def openFiles(self, info_list : typing.List[WindowInfo] = None):
        if not(isinstance(info_list, list)) or len(info_list) < 1:
            files = QFileDialog.getOpenFileNames(self, "Select File(s),", self.currentPath, self.FILE_FILTER)[0]
            info_list = [WindowInfo("table", f, {}) for f in files]
            self.open_dir = True
        else:
            files = [info.filename for info in info_list]

        if len(info_list) > 0:
            for info in info_list:
                if not(info.filename in self.requested_files.keys()):
                    self.requested_files[info.filename] = []
                self.requested_files[info.filename].append(info)
            self.factory.createModels(files)

    @pyqtSlot()
    def openDir(self, filepath : str = None) -> bool:
        if not(isinstance(filepath, str)) or filepath == '':
            filepath = QFileDialog.getExistingDirectory(self, "Select Directory", self.currentPath)
        try:
            index = self.fsModel.setRootPath(filepath)
            if index.isValid():
                self.ui.filePathLineEdit.setText(filepath)
                self.ui.treeView.setRootIndex(index)
                self.currentPath = filepath
                self.addRecentFolder(filepath)
                self.open_dir = False
                self.setWindowTitle(f"{APPLICATION_NAME}: v{APPLICATION_VERSION}: {filepath}")
                QDir.setCurrent(filepath)
                return True
        except:
            self.logger.error(f"Could not load files for directory {filepath}")
        return False
    
    @pyqtSlot()
    def plotColumns(self, columns : list) -> bool:
        if len(self.viewer_windows) > 0 and isinstance(columns, list) and len(columns) > 0:
            success = True
            for dock_window in self.viewer_windows:
                widget = dock_window.window.widget()
                if isinstance(widget, TableViewer):
                    success &= widget.plotColumns(columns)
            return success
        return False
    
    @pyqtSlot(str)
    def onMergeTablesRequested(self, filename : str):
        if not(filename in self.requested_files.keys()):
            self.requested_files[filename] = []
        self.requested_files[filename].append(WindowInfo("table", filename, {}))

    @pyqtSlot()
    def onMergeTablesTriggered(self):
        self.merge_dialog = MergeDialog()
        self.merge_dialog.mergeTablesRequested.connect(self.onMergeTablesRequested)
        self.merge_dialog.show()

# Convert a nested list of regexes into resolved column names
def expand_regexes(model : DataFrameModel, nested_list : list, join : bool) -> list:
    new_list = []
    if isinstance(nested_list, list):
        for sub_list in nested_list:
            matches = []
            if isinstance(sub_list, list):
                matches = model.findAllColumns(sub_list)
                if len(matches) > 0:
                    if join:
                        new_list.append(matches)
                    else:
                        new_list += [[m] for m in matches]
    return new_list

class DataViewerApplication(QObject):

    def __init__(self, parent : QObject = None) -> None:
        super().__init__(parent=parent)
        self.factory          : DataFrameFactory        = DataFrameFactory.getInstance()
        self.windows          : typing.List[DataViewer] = []
        self.app              : QApplication            = None
        self.applicationStyle : str                     = None
        self.applicationTheme : str                     = None
        self.chartTheme       : str                     = None

    # Convert a list of lists into a single list
    def flattenList(self, nested_list : list) -> list:
        new_list = []
        if isinstance(nested_list, list):
            for sub_list in nested_list:
                if isinstance(sub_list, list):
                    for item in sub_list:
                        new_list.append(item)
        return new_list

    # Convert a nested list of regexes into resolved column names
    def expandRegexes(self, model : DataFrameModel, nested_list : list, join : bool) -> list:
        new_list = []
        if isinstance(nested_list, list):
            for sub_list in nested_list:
                matches = []
                if isinstance(sub_list, list):
                    matches = model.findAllColumns(sub_list)
                    if len(matches) > 0:
                        if join:
                            new_list.append(matches)
                        else:
                            new_list += [[m] for m in matches]
        return new_list

    def setupLogging(self, args) -> None:
        # Load the application settings
        settings        = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        default_logfile = DEFAULT_LOG_FILEPATH

        # Setup application logging
        file_log_level  = getattr(logging, settings.value('fileLogLevel', 'DEBUG'))
        log_format      = settings.value('logFormat'   , DEFAULT_LOG_FORMAT)
        if args.quiet:
            log_level = logging.CRITICAL
        elif args.verbose:
            log_level = logging.DEBUG
        else:
            log_level = getattr(logging, settings.value('logLevel', 'INFO'))
        if isinstance(args.log_filename, str):
            log_filename = args.log_filename
        else:
            log_filename = settings.value('logFilename ', default_logfile)

        self.qlogger : QLogger = QLogger(level=log_level)
        file_handler    = logging.FileHandler(log_filename)
        console_handler = logging.StreamHandler(sys.stdout)
        logging.basicConfig(level=logging.DEBUG, format=log_format, handlers=[self.qlogger, file_handler, console_handler])

        # Log to different levels for the different handlers
        self.qlogger.setLevel(log_level)
        file_handler.setLevel(file_log_level)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter("%(levelname)-8s | %(message)s"))

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting {APPLICATION_NAME} v{APPLICATION_VERSION}")

    # Set the global application style
    @pyqtSlot(str)
    def setApplicationStyle(self, style : str):
        if isinstance(style, str) and style != self.applicationStyle:
            if style in QStyleFactory.keys():
                self.logger.info(f'Setting Application Style to "{style}"')
                QApplication.setStyle(style)
                self.applicationStyle = style
            else:
                self.logger.warning(f'Invalid style: "{style}", available: {QStyleFactory.keys()}')

    # Set the global application color theme
    @pyqtSlot(str)
    def setApplicationTheme(self, theme : str):
        if isinstance(theme, str) and theme != self.applicationTheme:
            if hasattr(self, "app") and isinstance(self.app, QApplication):
                if theme in APPLICATION_THEMES.keys():
                    self.app.setStyleSheet(APPLICATION_THEMES[theme])
                    self.applicationTheme = theme
                else:
                    self.logger.warning(f'Invalid theme: "{theme}", available: {APPLICATION_THEMES.keys()}')
            else:
                self.logger.error("Invalid QApplication reference")

    # Set the global chart color theme
    @pyqtSlot(str)
    def setChartTheme(self, theme : str):
        if isinstance(theme, str) and theme != self.chartTheme:
            if theme in CHART_THEMES:
                try:
                    plt.style.use(theme)
                    self.chartTheme = theme
                except:
                    self.logger.warning(f'Unable to set color theme "{theme}" in matplotlib.pyplot')
            else:
                self.logger.warning(f'Invalid chart color theme: "{theme}", available: {CHART_THEMES}')

    def getUserManualPDF(self) -> str:
        """
        Return the path to the User Manual PDF
        """
        resource_path = pkg_resources.resource_filename("dataframeviewer", "docs/user_manual.pdf")
        if os.path.exists(resource_path):
            return resource_path
        elif os.path.exists(USER_MANUAL_PATH):
            return USER_MANUAL_PATH
        else:
            self.logger.error(f"Unable to find user manual at {resource_path} or {USER_MANUAL_PATH}")

        return ""
    
    @pyqtSlot()
    def openUserManualPDF(self) -> None:
        user_manual_path = self.getUserManualPDF()

        if os.path.exists(user_manual_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(user_manual_path))
        else:
            QMessageBox.warning(self.sender(), "Application error", "User Manual not found")

    @pyqtSlot()
    def openUserManualWeb(self) -> None:
        QDesktopServices.openUrl(QUrl(USER_MANUAL_WEB_LINK))

    def getSampleSettings(self) -> str:
        """
        Return the file path to the example settings file
        """
        filename = ""

        resource_path = pkg_resources.resource_filename("dataframeviewer", "settings/examples/stock_settings.json")
        if os.path.exists(resource_path):
            filename = str(Path(resource_path).absolute())
        elif os.path.exists(PKG_SETTINGS_PATH):
            filename = os.path.join(PKG_SETTINGS_PATH, "examples", "stock_settings.json")
        else:
            self.logger.error(f"Unable to find sample settings at {resource_path} or {PKG_SETTINGS_PATH}")

        return filename

    def getSampleData(self) -> typing.Tuple[str, typing.List[str]]:
        """
        Return a directory and some sample data files to demo the application
        """
        folder, filenames = "", []

        resource_path = pkg_resources.resource_filename("dataframeviewer", "data/example.csv")
        if os.path.exists(resource_path):
            folder = str(Path(resource_path).parent.absolute())
        elif os.path.exists(SAMPLE_DATA_PATH):
            folder = SAMPLE_DATA_PATH
        else:
            self.logger.error(f"Unable to find sample data at {resource_path} or {SAMPLE_DATA_PATH}")

        # Add the filenames to return
        if os.path.exists(folder):
            filenames.append(os.path.join(folder, "stocks", "FB.csv"))
            filenames.append(os.path.join(folder, "stocks", "GOOG.csv"))

        return folder, filenames

    def __loadDarkTheme(self):
        try:
            import qdarkstyle
            APPLICATION_THEMES["Dark"] = qdarkstyle.load_stylesheet()
            self.logger.info(f"Successfully imported QDarkStyle")
        except:
            self.logger.warning(f"Unable to import QDarkStyle")

    def runCommandLine(self, args : typing.List[str]) -> int:
        self.setupLogging(args)
        self.logger.debug(f"Command Line Arguments: {args}")

        # Filenames can be passed as positional arguments or with the -f option
        filenames = self.flattenList(args.filename) + self.flattenList(args.filenames)

        if args.example:
            _, sample_files = self.getSampleData()
            filenames.extend(sample_files)

        if len(filenames) > 0:
            any_plot = False
            for f in filenames:
                model = self.factory.createModel(f)
                if isinstance(args.plot, list) and len(args.plot) > 0:
                    if args.enable_regex:
                        expanded_list = self.expandRegexes(model, args.plot, args.join_plots)
                    else:
                        expanded_list = args.plot
                    for column_list in expanded_list:
                        any_plot |= model.plotColumns(PlotInfo(x=None,y=column_list), interactive=False)
            if any_plot:
                plt.show(block=True)
                return 0
            else:
                return 1
        else:
            return 1
    
    def startApplication(self, app : QApplication, args : typing.List[str]):

        # Store QApplication instance for use later
        self.app = app

        # Setup the log first
        self.setupLogging(args)

        # Load the application dark theme if possible
        self.__loadDarkTheme()

        # Filenames can be passed as positional arguments or with the -f option
        filenames = self.flattenList(args.filename) + self.flattenList(args.filenames)

        if args.example:
            sample_folder, sample_files = self.getSampleData()
            args.directory = sample_folder
            args.settings = self.getSampleSettings()
            filenames.extend(sample_files)

        # Load the application settings
        settings    = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        num_windows = settings.value('numWindows', 1)
        try:
            num_windows = int(num_windows)
            if not(isinstance(num_windows, int)) or num_windows < 1:
                num_windows = 1
        except:
            num_windows = 1
        
        style      = settings.value("applicationStyle", None)
        theme      = str(settings.value("applicationTheme", "Dark"))
        chartTheme = str(settings.value("chartTheme", "default"))
        self.setApplicationStyle(style)
        self.setApplicationTheme(theme)
        self.setChartTheme(chartTheme)

        # Run the DataViewer GUI Application
        for _ in range(num_windows):
            self.createWindow(cascade=False)

        # Open files from the command line
        for f in filenames:
            for window in self.windows:
                if not(f in window.requested_files.keys()):
                    window.requested_files[f] = []
                window.requested_files[f].append(WindowInfo("table", f, {}))
            self.factory.createModel(f)

        # Open a folder from the command line
        if args.directory:
            for window in self.windows:
                window.openDir(args.directory)

        # Apply settings from the command line
        if isinstance(args.settings, str) and os.path.exists(args.settings) and args.settings.endswith('.json'):
            for window in self.windows:
                for viewer in window.viewer_windows:
                    widget = viewer.window.widget()
                    if isinstance(widget, TableViewer):
                        widget.readSettingsFromFile(args.settings)

        for window in self.windows:
            window.show()

        if isinstance(args.plot, list) and len(args.plot) > 0:
            for window in self.windows:
                for dock_window in window.viewer_windows:
                    widget = dock_window.window.widget()
                    if hasattr(widget, 'model'):
                        model = widget.model
                        if args.enable_regex:
                            expanded_list = self.expandRegexes(model, args.plot, args.join_plots)
                        else:
                            expanded_list = args.plot
                        for column_list in expanded_list:
                            model.plotColumns(PlotInfo(x=None, y=column_list))

    def writeSettings(self):
        settings = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        settings.clear()
        settings.setValue('numWindows'      , len(self.windows))
        settings.setValue('applicationTheme', self.applicationTheme)
        settings.setValue('applicationStyle', self.applicationStyle)
        settings.setValue('chartTheme'      , self.chartTheme)
        settings.setValue("autofitColumnMax", settings.value("autofitColumnMax", 100))

        parsers = []
        for p in self.factory.parsers.values():
            d = p.toDict()
            d['default'] = bool(p == self.factory.default_parser)
            parsers.append(d)
        settings.setValue('parsers', parsers)
        if len(self.windows) > 0:

            # Get recents list
            recent_files   = []
            recent_folders = []
            for window in self.windows:
                recent_files   += [x for x in window.recentFiles if x not in recent_files]
                recent_folders += [x for x in window.recentFolders if x not in recent_folders]
            if len(recent_files) > MAX_RECENT_FILES:
                recent_files = recent_files[-MAX_RECENT_FILES:]
            if len(recent_folders) > MAX_RECENT_FILES:
                recent_folders = recent_folders[-MAX_RECENT_FILES:]
            settings.setValue('recentFiles'  , recent_files)
            settings.setValue('recentFolders', recent_folders)

            # Set window settings
            settings.beginWriteArray("windowSettings", len(self.windows))
            for i in range(len(self.windows)):
                window = self.windows[i]
                settings.setArrayIndex(i)
                window.writeSettings(settings=settings)
            settings.endArray()
        settings.sync()
    
    @pyqtSlot()
    def createWindow(self, cascade : bool = True) -> DataViewer:

        # Read the application settings
        settings       = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        recent_files   = settings.value('recentFiles', [])
        recent_folders = settings.value('recentFolders', [])

        # Update the window settings
        window = DataViewer(style=self.applicationStyle,
                            theme=self.applicationTheme,
                            chartTheme=self.chartTheme,
                             window_id=len(self.windows))
        settings.beginReadArray("windowSettings")
        settings.setArrayIndex(len(self.windows))
        window.readSettings(settings=settings)
        settings.endArray()

        # Initialize the window
        if isinstance(recent_files, list) and len(recent_files) > 0:
            window.setRecentFiles(recent_files)
        if isinstance(recent_folders, list) and len(recent_folders) > 0:
            window.setRecentFolders(recent_folders)

        window.ui.actionNewWindow.triggered.connect(self.createWindow)
        window.ui.actionExit.triggered.connect(self.exitApplication)
        window.windowClosed.connect(self.onWindowClosed)
        window.requestNewStyle.connect(self.setApplicationStyle)
        window.requestNewTheme.connect(self.setApplicationTheme)
        window.requestNewChartTheme.connect(self.setChartTheme)
        window.requestUserManualPDF.connect(self.openUserManualPDF)
        window.requestUserManualWeb.connect(self.openUserManualWeb)
        self.qlogger.message.connect(window.onMessageLogged)
        self.windows.append(window)

        if cascade and len(self.windows) > 1:
            firstWindow = self.windows[0]
            window.move(firstWindow.pos().x()+20, firstWindow.pos().y()+20)
            window.show()
            window.setFocus()

            if QFileInfo(firstWindow.currentPath).exists():
                window.openDir(firstWindow.currentPath)

        self.logger.info(f"Created Data Viewer Window #{len(self.windows)}")
        return window

    @pyqtSlot(QMainWindow)
    def onWindowClosed(self, window : DataViewer):
        if len(self.windows) > 1:
            if isinstance(window, DataViewer) and window in self.windows:
                self.windows.remove(window)
            else:
                self.logger.debug(f"Unexpected window closed: {window}")

    @pyqtSlot()
    def exitApplication(self):
        self.writeSettings()
        sys.exit(0)

#####################
# Application Main
#####################
        
def main(argv : list = []) -> int:
    default_logfile = DEFAULT_LOG_FILEPATH

    parser = argparse.ArgumentParser(description='Qt Application to visualize Pandas DataFrames')
    parser.add_argument('filename'            , type=str, help='One or more input filenames', action='append', nargs='*')
    parser.add_argument('-f', '--filenames'   , type=str, help='One or more input filenames', action='append', nargs='*')
    parser.add_argument('-d', '--directory'   , type=str, help='Path to input directory')
    parser.add_argument('-p', '--plot'        , type=str, help='Column name(s) of one or more plots to create from the file(s)', action='append', nargs='*')
    parser.add_argument('-s', '--settings'    , type=str, help='Path to a table settings file (JSON) to apply to tables')
    parser.add_argument('-n', '--no-gui'      , help='Flag to run without DataViewer gui (Use for plots only)', action='store_true', default=False)
    parser.add_argument('-e', '--enable-regex', help='Enable regular expressions for plot column names', action='store_true', default=False)
    parser.add_argument('-j', '--join-plots'  , help='Flag to join plots into a single figure when using regular expressions', action='store_true', default=False)
    parser.add_argument('-l', '--log-filename', help='Path to application log file', default=default_logfile)
    parser.add_argument('-v', '--verbose'     , help='Enable verbose logging', action='store_true', default=False)
    parser.add_argument('-q', '--quiet'       , help='Enable limited logging (critical only)', action='store_true', default=False)
    parser.add_argument('--example'           , help='Open a sample data file called example.csv', action='store_true', default=False)
    args = parser.parse_args(argv)

    # Create the QApplication
    app = QApplication(sys.argv)

    # Attempt to set application icon
    resource_path = pkg_resources.resource_filename("dataframeviewer", "ui/images/app_icon.png")
    if os.path.exists(resource_path):
        app.setWindowIcon(QIcon(resource_path))
    elif os.path.exists(APP_ICON_PATH):
        app.setWindowIcon(QIcon(APP_ICON_PATH))
    
    # Make sure the user settings directory is available
    getUserSettingsPath()

    # Initialize the DataViewer application
    data_viewer = DataViewerApplication()
    app.lastWindowClosed.connect(data_viewer.exitApplication)

    # Run the Data Viewer
    if args.no_gui:
        return data_viewer.runCommandLine(args)
    else:
        data_viewer.startApplication(app, args)

    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    exit(main(sys.argv[1:]))
