#!/usr/bin/env python

# MIT License

# Copyright (c) 2024 Rafael Arvelo

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
# This file contains the classes for the PlotViewer UI of the DataViewer application
#
# pylint: disable-all

# Standard modules
import os
import sys
import logging
import typing
import warnings
import json

from pathlib import Path

# Application paths
DATAVIEWER_BASE_PATH = os.path.dirname(os.path.realpath(__file__))
REPOSITORY_BASE_PATH = str(Path(DATAVIEWER_BASE_PATH).parent.absolute())
IMAGES_PATH          = os.path.join(DATAVIEWER_BASE_PATH, "ui", "images")

# Application paths
SETTINGS_PATH  = os.path.join(DATAVIEWER_BASE_PATH, "settings")

# Update PYTHONPATH
sys.path.append(DATAVIEWER_BASE_PATH)
sys.path.append(IMAGES_PATH)

# Third-party modules
from pandas            import DataFrame
from PyQt5.QtWidgets   import QWidget, QApplication, QFileDialog
from PyQt5.QtCore      import Qt, QFileInfo, pyqtSignal, pyqtSlot
from PyQt5.QtGui       import QMouseEvent
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Suppress the MatplotlibDeprecationWarning
from matplotlib import MatplotlibDeprecationWarning
warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)

# Package modules
from ui.ui_plotviewer  import Ui_PlotViewer
from dataframemodel    import DataFrameModel, PlotInfo, DataFrameFactory, getUserSettingsPath
from customchartdialog import CustomChartDialog

class PlotViewer(QWidget):
    """
    The PlotViewer is a QWidget to encapsulate a single MatPlotLib Figure Canvas
    """
    settings_filter = 'JSON Files *.json;;All Files *'
    save_filter     = '{name} Files *{suffix};;All Files *'
    
    # PlotViewer Signals
    requestNewPlot = pyqtSignal(DataFrameModel, PlotInfo)

    def __init__(self,
                 model  : DataFrameModel,
                 parent : QWidget = None) -> None:
        """
        Create a PlotViewer object
        """
        super().__init__(parent)
        self.ui     = Ui_PlotViewer()
        self.info   : PlotInfo       = None
        self.figure : Figure         = None
        self.canvas : FigureCanvas   = None
        self.model  : DataFrameModel = model
        self.logger : logging.Logger = logging.getLogger(__name__)

        self.initUI()

    def initUI(self) -> None:
        """"
        Initialize the UI and connect signals
        """
        self.ui.setupUi(self)

        # Update UI
        self.ui.filenameLabel.setText(self.model.filename)
        self.ui.placeholderWidget.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.setWindowTitle(f"Plot::{self.model.filename}")

        # Connect signals / slots
        self.ui.editPlotButton.pressed.connect(self.editPlotSettings)
        self.ui.copyButton.pressed.connect(self.duplicatePlot)
        self.ui.saveSettingsButton.clicked.connect(self.saveSettingsToFile)
        self.ui.loadSettingsButton.clicked.connect(self.readSettingsFromFile)

        self.show()
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        """
        Double click the widget to edit the plot settings
        """
        self.editPlotSettings()
        return super().mouseDoubleClickEvent(a0)
    
    @pyqtSlot()
    def duplicatePlot(self):
        """
        Request a new plot with the same settings
        """
        self.requestNewPlot.emit(self.model, self.info)

    @pyqtSlot()
    def editPlotSettings(self):
        """
        Open a dialog to customize the current plot
        """
        if isinstance(self.info, PlotInfo):
            info = self.info
        else:
            info = PlotInfo()
        self.custom_chart_dialog = CustomChartDialog(self.model.getColumnModel(), info)
        self.custom_chart_dialog.customChartRequested.connect(self.updatePlot)
        self.custom_chart_dialog.show()

    @pyqtSlot(PlotInfo)
    def updatePlot(self, 
                   info : typing.Union[PlotInfo, dict]) -> None:
        """
        Update the current plot based on the given settings
        """
        if isinstance(info, dict):
            info = PlotInfo.from_dict(info)

        if isinstance(info, PlotInfo) and info.isValid() and info != self.info:
            # Save the current plot info
            self.info = info

            # Create the new plot from the internal model
            figure = self.model.plotColumns(info, interactive=False)

            # Attempt to render the plot
            if isinstance(figure, Figure):
                self.__drawCanvas(figure)
            else:
                self.logger.error(f"Unable to create plot from {info}")
    
    def getSettings(self) -> dict:
        """
        Return a dictionary with the plot settings
        """
        if isinstance(self.info, PlotInfo) and self.info.isValid():
            settings = self.info.to_dict()
        else:
            settings = PlotInfo().to_dict()
        settings['viewer_type'] = "plot"
        return settings

    @pyqtSlot()
    def saveSettingsToFile(self, filename : str = None) -> None:
        """
        Save the plot settings to a file
        """
        settings = self.getSettings()
        user_settings_path = getUserSettingsPath()
        if not(isinstance(filename, str)) or len(filename) < 1:
            filename = QFileDialog.getSaveFileName(self, "Input Save Filename", user_settings_path, self.settings_filter)[0]
        if isinstance(filename, str) and len(filename) > 0:
            if not(filename.endswith('.json')):
                filename += '.json'
            with open(filename, 'w') as file:
                json.dump(settings, file, indent=2)
        else:
            self.logger.error(f"Unable to save to file \"{filename}\"")

    @pyqtSlot()
    def readSettingsFromFile(self, filename : str = None) -> None:
        """
        Load the plot settings from a file
        """
        user_settings_path = getUserSettingsPath()
        if not(isinstance(filename, str)) or len(filename) < 1:
            filename = QFileDialog.getOpenFileName(self, "Select Settings File", user_settings_path, self.settings_filter)[0]
        if isinstance(filename, str) and len(filename) > 0:
            if not(filename.endswith('.json')):
                filename += '.json'
            with open(filename, 'r') as file:
                settings = json.load(file)
                info = PlotInfo.from_dict(settings)
                self.updatePlot(info)

    def __drawCanvas(self,
                     figure : Figure) -> None:
        """
        Attempt to render a plot on the UI
        """
        if isinstance(self.info, PlotInfo):
            filename = QFileInfo(self.model.filename).fileName()
            if "title" in self.info.options.keys():
                self.setWindowTitle(f"{filename}::{self.info.options['title']}")
            else:
                self.setWindowTitle(f"{filename}::{self.info.name(short=True)}")

        # Clear the plot if it already exists
        if isinstance(self.figure, Figure):
            self.figure.clear()
        
        # Update the figure
        self.figure = figure

        # Remove the placeholder
        if isinstance(self.ui.placeholderWidget, QWidget):
            self.ui.plotLayout.removeWidget(self.ui.placeholderWidget)
            self.ui.placeholderWidget = None

        # Remove the canvas if it already exists
        if isinstance(self.canvas, FigureCanvas):
            self.ui.plotLayout.removeWidget(self.toolbar)
            self.ui.plotLayout.removeWidget(self.canvas)

        # Create a new canvas and toolbar
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Add the new canvas to the layout
        self.ui.plotLayout.addWidget(self.toolbar)
        self.ui.plotLayout.addWidget(self.canvas)

        # Render the plot
        self.canvas.draw()
        self.ui.copyButton.setEnabled(True)

def create_plot(file_or_model : typing.Union[str, DataFrameModel, DataFrame], 
                info : PlotInfo = None,
                **kwargs):
    """
    Convenience method to create a plot viewer
    """
    logger = logging.getLogger(__name__)
    factory = DataFrameFactory.getInstance()
    if isinstance(file_or_model, DataFrameModel):
        filename = file_or_model.filename
        view     = PlotViewer(file_or_model)
    elif isinstance(file_or_model, str):
        filename = file_or_model
        model    = factory.createModel(filename, **kwargs)
        view     = PlotViewer(model)
    elif isinstance(file_or_model, DataFrame):
        model    = factory.createModel(filename="", df=file_or_model, **kwargs)
        filename = model.filename
        view     = PlotViewer(model)
    else:
        logger.error(f"Unable to create PlotViewer from type: {file_or_model}")
        view     = PlotViewer(DataFrameModel(DataFrame()))
        filename = ""

    view.setToolTip(filename)
    view.setWindowTitle(f"Plot::{os.path.basename(filename)}")
    view.updatePlot(info)
    logger.info(f"Created PlotViewer {view.windowTitle()}")
    return view

if __name__ == "__main__":

    # Test the stand-alone plotviewer
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        view = create_plot(sys.argv[1])
    else:
        import numpy
        x     = numpy.arange(-numpy.pi * 2 , numpy.pi * 2, numpy.pi / 16)
        df    = DataFrame({"X" : x, "Sin(x)" : numpy.sin(x), "Cos(x)" : numpy.cos(x)})
        view  = create_plot(df, PlotInfo(x=None, y=df.columns))
    view.show()

    sys.exit(app.exec_())