#!/usr/bin/env python
#
# PyQt API:
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html
# Tutorials:
# http://zetcode.com/tutorials/pyqt4/

import os
import sys
import optparse

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QEvent, Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

from obspy.core import read


class MyMainWindow(QtGui.QMainWindow):
    """
    Main Window docstring...
    """
    def __init__(self, options):
        # make all commandline options available for later use
        # e.g. in update() methods
        self.options = options
        # for convenience set some instance wide attributes
        self.low = options.low
        self.high = options.high
        self.zerophase = options.zerophase

        # setup GUI
        QtGui.QMainWindow.__init__(self)
        self.__setup_GUI()
        self.__connect_signals()

        # put some addtional setup stuff here...
        self.st = read()
        
        # make initial plot and show it
        self.update()
        self.canv.show()
        self.show()

    def __setup_GUI(self):
        """
        Add matplotlib canvas, some buttons and stuff...
        """
        self.setWindowTitle("Title of main window...")
        self.setGeometry(300, 300, 500, 500)
        main = QtGui.QWidget()
        self.setCentralWidget(main)
        # add matplotlib canvas and setup layouts to put buttons in
        vlayout = QtGui.QVBoxLayout()
        vlayout.addStretch(1)
        main.setLayout(vlayout)
        canv = QMplCanvas()
        vlayout.addWidget(canv)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch(1)
        vlayout.addLayout(hlayout)

        # add some buttons
        self.qDoubleSpinBox_low = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_low.setValue(self.options.low)
        hlayout.addWidget(QtGui.QLabel("low"))
        hlayout.addWidget(self.qDoubleSpinBox_low)
        
        self.qDoubleSpinBox_high = QtGui.QDoubleSpinBox()
        self.qDoubleSpinBox_high.setValue(self.options.high)
        hlayout.addWidget(QtGui.QLabel("high"))
        hlayout.addWidget(self.qDoubleSpinBox_high)

        self.qCheckBox_zerophase = QtGui.QCheckBox()
        self.qCheckBox_zerophase.setChecked(self.options.zerophase)
        self.qCheckBox_zerophase.setText("zerophase")
        hlayout.addWidget(self.qCheckBox_zerophase)

        qToolBar = QtGui.QToolBar()
        self.toolbar = NavigationToolbar2QTAgg(canv, qToolBar)
        qToolBar.addWidget(self.toolbar)
        qToolBar.setMovable(False)
        qToolBar.setFloatable(False)
        self.addToolBar(Qt.BottomToolBarArea, qToolBar)

        # make matplotlib stuff available
        self.canv = canv
        self.fig = canv.figure
        self.ax = self.fig.add_subplot(111)

    def __connect_signals(self):
        """
        Connect button signals to methods...
        """
        connect = QtCore.QObject.connect
        connect(self.qDoubleSpinBox_low,
                QtCore.SIGNAL("valueChanged(double)"),
                self.on_qDoubleSpinBox_low_valueChanged)
        connect(self.qDoubleSpinBox_high,
                QtCore.SIGNAL("valueChanged(double)"),
                self.on_qDoubleSpinBox_high_valueChanged)
        connect(self.qCheckBox_zerophase,
                QtCore.SIGNAL("stateChanged(int)"),
                self.on_qCheckBox_zerophase_stateChanged)

    def update(self):
        """
        This method should do everything to update the plot.
        """
        # clear axes before anything else
        ax = self.ax
        if ax.lines:
            xlims = list(ax.get_xlim())
            ylims = list(ax.get_ylim())
        ax.clear()

        st = self.st.copy()
        st.filter("bandpass", freqmin=self.low, freqmax=self.high,
                  zerophase=self.zerophase)
        tr = st.select(component="Z")[0]
        ax.plot(tr.data)
        # update matplotlib canvas
        try:
            ax.set_xlim(xlims)
            ax.set_ylim(ylims)
        except UnboundLocalError:
            pass
        self.canv.draw()
    
    def on_qDoubleSpinBox_low_valueChanged(self, newvalue):
        self.low = newvalue
        self.update()

    def on_qDoubleSpinBox_high_valueChanged(self, newvalue):
        self.high = newvalue
        self.update()

    def on_qCheckBox_zerophase_stateChanged(self, value):
        self.zerophase = self.qCheckBox_zerophase.isChecked()
        self.update()


class QMplCanvas(FigureCanvasQTAgg):
    """
    Class to represent the FigureCanvas widget.
    """
    def __init__(self, parent=None):
        # Standard Matplotlib code to generate the plot
        self.fig = plt.Figure()
        # initialize the canvas where the Figure renders into
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)


def main():
    """
    Gets executed when the program starts.
    """
    usage = "Usage information goes here..."
    parser = optparse.OptionParser(usage)
    parser.add_option("-l", "--low", type=float, dest="low", default=1.0,
                      help="Lowpass frequency")
    parser.add_option("--high", type=float, dest="high", default=20.0,
                      help="Highpass frequency")
    parser.add_option("-z", "--zerophase", action="store_true",
                      dest="zerophase", default=False,
                      help="Use zerophase filter option")
    (options, args) = parser.parse_args()

    qApp = QtGui.QApplication(sys.argv)
    myMainWindow = MyMainWindow(options)
    os._exit(qApp.exec_())


if __name__ == "__main__":
    main()
