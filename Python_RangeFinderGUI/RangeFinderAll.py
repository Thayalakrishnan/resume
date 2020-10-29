""" @package RangeFinder
  This package contains all the classes that are used to create an instance of the GUI
  The classes dont take any input and run off of each other. Button input triggers the 
 instance of one of these classes as every class generates a new window, except the plotting 
"""
import collections, math, struct, sys, time, copy, serial
import numpy as np
from threading import Thread
from PyQt5 import QtSerialPort
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from qtpy.uic import loadUi
from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import QLocale, QObject, QSize, Qt, QTimer
from qtpy.QtGui import QColor, QColorConstants, QFont, QVector3D, qRgb, QPalette
from qtpy.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, 
                            QFontComboBox, QFrame, QHBoxLayout, QLabel, 
                            QLCDNumber, QMainWindow, QPushButton, 
                            QSizePolicy, QSlider, QVBoxLayout, QWidget, QStyleFactory, QStyle)
from qtpy.QtDatavisualization import (Q3DCamera, Q3DScatter, Q3DTheme,
                                      QAbstract3DAxis, QAbstract3DGraph,
                                      QAbstract3DSeries, QCustom3DItem,
                                      QScatter3DSeries, QScatterDataItem,
                                      QScatterDataProxy, QValue3DAxis,
                                      QValue3DAxisFormatter)
""" RangeFinder Class
    This class creates an instance of the rangefiner application, inclduing the layout,
    the serial connection and the plotting options. 
    Buttons on the interface allow for interaction with the board
    
    This Class subclasses the QtWidgets to create an instance
    
    Methods from this class control the user interaction.
"""
class RangeFinder(QtWidgets.QWidget):
    """ The constructor."""
    def __init__(self, parent=None): 
        super(RangeFinder, self).__init__(parent)
        self.message_le = QtWidgets.QLineEdit()
        self.message_le.setFixedSize(120,50)
        self.send_btn = QtWidgets.QPushButton(text="Send to Board",clicked=self.send)
        self.send_btn.setFixedSize(120,50)
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.output_te.setFixedWidth(500)
        self.button = QtWidgets.QPushButton(text="Connect", checkable=True,toggled=self.on_toggled)
        self.button.setStyleSheet("background-color: red")
        self.button.setFixedSize(120,50)
        ''' Timers (ms) '''
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.start()
        self.timer.timeout.connect(self.receive)
        ''' Graphing '''
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        self.container.setMinimumSize(QSize(500, 500))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.modifier = RangeFinderPlotter(graph)
        ''' Buttons '''
        self.button_quick_scan = QtWidgets.QPushButton()
        self.button_quick_scan.setFixedSize(120,50)
        self.button_quick_scan.setText("Quick Scan")
        self.button_deep_scan = QtWidgets.QPushButton()
        self.button_deep_scan.setFixedSize(120,50)
        self.button_deep_scan.setText("Deep Scan")
        self.button_custom_scan = QtWidgets.QPushButton()
        self.button_custom_scan.setFixedSize(120,50)
        self.button_custom_scan.setText("Custom Scan")
        self.button_calibrate = QtWidgets.QPushButton()
        self.button_calibrate.setFixedSize(120,50)
        self.button_calibrate.setText("Calibrate")
        self.button_ptu_control = QtWidgets.QPushButton()
        self.button_ptu_control.setFixedSize(120,50)
        self.button_ptu_control.setText("PTU Control")
        self.button_help = QtWidgets.QPushButton()
        self.button_help.setFixedSize(120,50)
        self.button_help.setText("Help!?")
        ''' Layout '''
        horizontal_layout = QtWidgets.QHBoxLayout(self)
        vertical_layout_one = QtWidgets.QVBoxLayout()
        vertical_layout_one.addWidget(self.container, 1)
        vertical_layout_two = QtWidgets.QVBoxLayout()
        vertical_layout_two.addWidget(self.output_te)
        vertical_layout_three = QtWidgets.QVBoxLayout()
        vertical_layout_three.addWidget(self.message_le)
        vertical_layout_three.addWidget(self.send_btn)
        vertical_layout_three.addWidget(self.button)
        vertical_layout_three.addWidget(self.button_quick_scan)
        vertical_layout_three.addWidget(self.button_deep_scan)
        vertical_layout_three.addWidget(self.button_custom_scan)
        vertical_layout_three.addWidget(self.button_calibrate)
        vertical_layout_three.addWidget(self.button_ptu_control)
        vertical_layout_three.addWidget(self.button_help)
        
        horizontal_layout.addLayout(vertical_layout_one)
        horizontal_layout.addLayout(vertical_layout_two)
        horizontal_layout.addLayout(vertical_layout_three)
        """ Serial Connection configuration """
        self.serial = QtSerialPort.QSerialPort('COM4',baudRate=QtSerialPort.QSerialPort.Baud9600,readyRead=self.receive)
        self.setWindowTitle("Range Finder")
        ''' commands '''
        self.command_quick_scan = '-on-q'
        self.command_deep_scan = '-on-l'
        self.command_custom_scan = '-c'
        self.command_ptu_control= '-test'
        self.command_calibrate = '-cal'
        self.command_help = '-help'
        self.command_d = 'd'
        self.command_h = 'h'
        
        self.plotbank = []
    """ Method to read from serial, convert the data and send it to be plotted  """
    #  @param self The object pointer
    @pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            raw_input_data = self.serial.readLine().data().decode()
            self.output_te.append(raw_input_data)
            raw_input_data = list(map(int, raw_input_data.rstrip('\r\n').split(',')))
            theta = math.radians(raw_input_data[1])
            phi = math.radians(raw_input_data[0])
            distance = raw_input_data[2]

            x_val = distance*math.sin(theta)*math.cos(phi)
            y_val = distance*math.sin(theta)*math.sin(phi)
            z_val = distance*math.cos(theta)
            self.output_te.append(f'x = {x_val} y = {y_val} z = {z_val}')
            self.plotbank.append(f'x = {x_val} y = {y_val} z = {z_val}')
            pos = QVector3D(x_val,z_val,y_val)
            self.modifier.addCustomItem(pos)
    
    """ Method to send commands via serial
    #  @param self The object pointer"""
    @pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())
    
    """ Method to create a serial connection with the board
    #  @param self The object pointer"""
    @pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        self.button.setStyleSheet("background-color: green" if checked else "background-color: red")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button.setChecked(False)
        else:
            self.serial.close()
    
    ''' Quick Scan '''
    """ Button to trigger a quick scan
    #  @param self The object pointer"""
    def button_quick_scan_click(self):
        self.quick_scan = GraphConsole()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_quick_scan.encode())
    ''' Deep Scan '''
    """ Button to trigger a deep scan
    #  @param self The object pointer"""
    def button_deep_scan_click(self):
        self.deep_scan = GraphConsole()
        self.deep_scan.show()
        self.deep_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_deep_scan.encode())
    ''' Custom Scan '''
    """ Button to trigger a custom scan
    #  @param self The object pointer"""
    def button_custom_scan_click(self):
        self.custom_scan = CustomScanConsole()
        self.custom_scan.slider_azimuth_max.valueChanged.connect(self.custom_scan.)
        self.custom_scan.slider_azimuth_min.valueChanged.connect(self.custom_scanazimuth_min_change)
        self.custom_scan.slider_elevation_max.valueChanged.connect(self.custom_scan.elevation_max_change)
        self.custom_scan.slider_elevation_min.valueChanged.connect(self.custom_scan.elevation_min_change)
        self.custom_scan.slider_scan_frequency.valueChanged.connect(self.custom_scan.scan_frequency_change)
        self.custom_scan.slider_step_change.valueChanged.connect(self.custom_scan.step_change_change)
        self.custom_scan.slider_samples_orientation.valueChanged.connect(self.custom_scan.samples_orientation_change)
        self.custom_scan.button_main_menu.clicked.connect(self.custom_scan.button_main_menu_click)
        self.custom_scan.button_finish_setting_values.clicked.connect(self.custom_scan.button_finish_setting_values_click)
        self.custom_scan.show()
        self.custom_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_custom_scan.encode())
    ''' Calibrate '''
    """ Button to trigger a calibration
    #  @param self The object pointer"""
    def button_calibrate_click(self):
        self.quick_scan = GraphConsole()
        self.quick_scan.show()
        self.quick_scan.setAttribute(Qt.WA_DeleteOnClose)
        # Output Command
        self.serial.write(self.command_calibrate.encode())
    ''' PTU Control '''
    """ Button to control the PTU
    #  @param self The object pointer"""
    def button_ptu_control_click(self):
        self.serial.write(self.command_h.encode())
    ''' Help?! '''
    """ Button to trigger the help commands
    #  @param self The object pointer"""
    def button_help_click(self):
        self.serial.write(self.command_d.encode())

""" This class handles the entire plotting infrastructure. 

  The class is instantiated within another window and can take in data to be plotted.
  The graph is a scatter plot and is pannable and zoomable. """
class RangeFinderPlotter(QObject):
    def __init__(self, scatter):
        super(RangeFinderPlotter, self).__init__()
        self.graph = scatter  # name of scatter plot
        self.m_fontSize = 12
        self.m_style = QAbstract3DSeries.MeshSphere
        self.m_smooth = True
        self.plot_timer = QTimer()
        customTheme = self.graph.activeTheme()
        """ Graph Theme """ 
        customTheme.setAmbientLightStrength(0.3)
        customTheme.setBackgroundColor(QColor(QColorConstants.White))
        customTheme.setBackgroundEnabled(False)
        customTheme.setBaseColors([QColorConstants.Red,QColorConstants.DarkRed,QColorConstants.Magenta])
        customTheme.setColorStyle(Q3DTheme.ColorStyleUniform)
        customTheme.setFont(QFont("Arial"))
        customTheme.setGridEnabled(True)
        customTheme.setGridLineColor(QColor(QColorConstants.White))
        customTheme.setHighlightLightStrength(7.0)
        # label
        customTheme.setLabelBackgroundColor(QColor(QColorConstants.Black))
        customTheme.setLabelBackgroundEnabled(True)
        customTheme.setLabelBorderEnabled(True)
        customTheme.setLabelTextColor(QColor(QColorConstants.White))
        #light
        customTheme.setLightColor(QColor(QColorConstants.White))
        customTheme.setLightStrength(6.0)
        customTheme.setMultiHighlightColor(QColor(QColorConstants.White))
        customTheme.setSingleHighlightColor(QColor(QColorConstants.White))
        #window 
        #customTheme.setWindowColor(QColor(QColorConstants.Black)) 
        customTheme.setWindowColor(QColor(QColorConstants.Blue))
        self.graph.activeTheme().setType(Q3DTheme.ThemeUserDefined)
        ''' shadow quality '''
        font = self.graph.activeTheme().font()
        font.setPointSize(12.0)
        self.graph.activeTheme().setFont(QFont("Arial"))
        self.graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)
        self.graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetIsometricRight)
        self.graph.scene().activeCamera().setZoomLevel(150.0)
        proxy = QScatterDataProxy()
        series = QScatter3DSeries(proxy)
        # this is how an indidiaul point should be labelled when it is clicked on 
        # so the label here will be dipslayed in the graph view when a plotted item is clicked
        series.setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
        series.setMeshSmooth(self.m_smooth)
        series.setItemSize(0.01)
        self.graph.addSeries(series)
        """ Configure axis"""
        xaxis_proxy = QValue3DAxisFormatter()
        xaxis = QValue3DAxis(xaxis_proxy)
        xaxis.setLabelFormat("%.2f mm")
        xaxis.setSegmentCount(5)
        xaxis.setSubSegmentCount(2)
        xaxis.setTitle("X axis")
        xaxis.setTitleVisible(True)
        self.graph.addAxis(xaxis)
        # configure y axis
        yaxis_proxy = QValue3DAxisFormatter()
        yaxis = QValue3DAxis(yaxis_proxy)
        yaxis.setLabelFormat("%.2f mm")
        yaxis.setSegmentCount(5)
        yaxis.setSubSegmentCount(2)
        yaxis.setTitle("Y axis")
        yaxis.setTitleVisible(True)
        self.graph.addAxis(yaxis)
        # configure z axis
        zaxis_proxy = QValue3DAxisFormatter()
        zaxis = QValue3DAxis(zaxis_proxy)
        zaxis.setLabelFormat("%.2f mm")
        zaxis.setSegmentCount(5)
        zaxis.setSubSegmentCount(2)
        zaxis.setTitle("Z axis")
        zaxis.setTitleVisible(True)
        self.graph.addAxis(zaxis)
        # title axis??
        title_proxy = QValue3DAxisFormatter()
        taxis = QValue3DAxis(title_proxy)
        taxis.setTitle("Range finder")
        taxis.setTitleVisible(True)
        ''' shadow quality '''
        self.graph.setAxisX(xaxis)
        self.graph.setAxisY(yaxis)
        self.graph.setAxisZ(zaxis)
        self.graph.setTitle("Range finder")
        self.graph.axisX().setRange(-1500,1500)
        self.graph.axisY().setRange(-1500,1500)
        self.graph.axisZ().setRange(0,3000)
        self.graph.axisX().setTitle("X axis (azimuth)")
        self.graph.axisY().setTitle("Y axis (elevation)")
        self.graph.axisZ().setTitle("Z axis (depth/range)")
        self.graph.seriesList()[0].setMesh(self.m_style)
        self.graph.seriesList()[0].setMeshSmooth(self.m_smooth)
        self.graph.setAspectRatio(1.0)
    """ Function to plot the given data point
      @param self The object pointer"""
    def addCustomItem(self, point):
        new_item = QCustom3DItem()
        new_item.setMeshFile('sphere.obj')
        new_item.setScaling(QVector3D(0.005,0.005,0.005))
        new_item.setPosition(point)
        self.graph.addCustomItem(new_item)

""" GraphConsole
    This class creates an instance of the graphing console
    the graphing console is a much more detailed scanning conole that provides real time 
    information regarding the current scan. it is instantiated right after triggering one of
    customs can, quick scan or deep scan
    
    This Class subclasses the QtWidgets to create an instance 
"""
''' Generate the Graphing Console '''
class GraphConsole(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GraphConsole, self).__init__(parent)
        ''' Widgets '''
        self.run_scan = QtWidgets.QPushButton(text="Run Scan")
        self.run_scan.setFixedSize(120,50)
        self.stop_scan = QtWidgets.QPushButton(text="Stop Scan")
        self.stop_scan.setFixedSize(120,50)
        ''' Accelerometer '''
        self.lcd_acc = QtWidgets.QLCDNumber()
        self.lcd_acc.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_acc.setSmallDecimalPoint(False)
        self.lcd_acc.setObjectName("lcd_acc")
        self.lcd_acc.setFixedSize(120,50)
        ''' Gyroscope '''
        self.lcd_gyr = QtWidgets.QLCDNumber()
        self.lcd_gyr.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_gyr.setSmallDecimalPoint(False)
        self.lcd_gyr.setObjectName("lcd_gyr")
        self.lcd_gyr.setFixedSize(120,50)
        ''' Magnetometer '''
        self.lcd_mag = QtWidgets.QLCDNumber()
        self.lcd_mag.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_mag.setSmallDecimalPoint(False)
        self.lcd_mag.setObjectName("lcd_mag")
        self.lcd_mag.setFixedSize(120,50)
        ''' Azimuth '''
        self.lcd_azi = QtWidgets.QLCDNumber()
        self.lcd_azi.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_azi.setSmallDecimalPoint(False)
        self.lcd_azi.setObjectName("lcd_azi")
        self.lcd_azi.setFixedSize(120,50)
        ''' Elevation '''
        self.lcd_ele = QtWidgets.QLCDNumber()
        self.lcd_ele.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_ele.setSmallDecimalPoint(False)
        self.lcd_ele.setObjectName("lcd_ele")
        self.lcd_ele.setFixedSize(120,50)
        ''' Distance '''
        self.lcd_dis = QtWidgets.QLCDNumber()
        self.lcd_dis.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_dis.setSmallDecimalPoint(False)
        self.lcd_dis.setObjectName("lcd_dis")
        self.lcd_dis.setFixedSize(120,50)
        
        ''' Graphing '''
        graph = Q3DScatter()
        screenSize = graph.screen().size()
        self.container = QtWidgets.QWidget.createWindowContainer(graph)
        self.container.setMinimumSize(QSize(screenSize.width() / 2, screenSize.height() / 1.5))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.modifier = RangeFinderPlotter(graph)
        
        ''' Labels '''
        self.label_acc = QtWidgets.QLabel()
        self.label_acc.setFixedSize(120,50)
        self.label_acc.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_acc.setAlignment(QtCore.Qt.AlignCenter)
        self.label_acc.setText("Accelerometer")
        
        self.label_gyr = QtWidgets.QLabel()
        self.label_gyr.setFixedSize(120,50)
        self.label_gyr.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_gyr.setAlignment(QtCore.Qt.AlignCenter)
        self.label_gyr.setText("Gyroscope")
        
        self.label_mag = QtWidgets.QLabel()
        self.label_mag.setFixedSize(120,50)
        self.label_mag.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_mag.setAlignment(QtCore.Qt.AlignCenter)
        self.label_mag.setText("Magnetometer")

        self.label_azi = QtWidgets.QLabel()
        self.label_azi.setFixedSize(120,50)
        self.label_azi.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azi.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azi.setText("Azimuth")
        
        self.label_ele = QtWidgets.QLabel()
        self.label_ele.setFixedSize(120,50)
        self.label_ele.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_ele.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ele.setText("Elevation")
        
        self.label_dis = QtWidgets.QLabel()
        self.label_dis.setFixedSize(120,50)
        self.label_dis.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_dis.setAlignment(QtCore.Qt.AlignCenter)
        self.label_dis.setText("Distance")
        
        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.horizontal_layout.addWidget(self.container, 1)
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addWidget(self.run_scan)
        self.vertical_layout.addWidget(self.stop_scan)
        self.vertical_layout.addWidget(self.label_acc)
        self.vertical_layout.addWidget(self.lcd_acc)
        self.vertical_layout.addWidget(self.label_gyr)
        self.vertical_layout.addWidget(self.lcd_gyr)
        self.vertical_layout.addWidget(self.label_mag)
        self.vertical_layout.addWidget(self.lcd_mag)
        self.vertical_layout.addWidget(self.label_azi)
        self.vertical_layout.addWidget(self.lcd_azi)
        self.vertical_layout.addWidget(self.label_ele)
        self.vertical_layout.addWidget(self.lcd_ele)
        self.vertical_layout.addWidget(self.label_dis)
        self.vertical_layout.addWidget(self.lcd_dis)
        self.setWindowTitle("Graph Console")

""" CustomScanConsole
    This class creates an instance of the custom scanning console
    the custom scan console houses sliders that allow the user to create a custom scan
    once the user is happy with the paramters, they hit proceed which will then pull the values
    and send them to the board to initialise the scan
    
    This Class subclasses the QtWidgets to create an instance
"""
class CustomScanConsole(QtWidgets.QWidget):
    """ The constructor."""
    def __init__(self, parent=None):
        super(CustomScanConsole, self).__init__(parent)
        ''' Widgets '''
        self.button_finish_setting_values = QtWidgets.QPushButton(text="Proceed")
        self.button_finish_setting_values.setFixedSize(120,50)
        self.button_main_menu = QtWidgets.QPushButton(text="Main Menu")
        self.button_main_menu.setFixedSize(120,50)
        self.serial = QtSerialPort.QSerialPort('COM4',baudRate=QtSerialPort.QSerialPort.Baud9600)
        # configure global application font
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setKerning(False)
        ''' set bounds '''
        set_azimuth_min_low = 30
        set_azimuth_min_high = 155
        set_azimuth_min_step = 1
        set_azimuth_max_low = 35
        set_azimuth_max_high = 160
        set_azimuth_max_step = 1
        set_elevate_min_low = -60
        set_elevate_min_high = 55
        set_elevate_min_step = 1
        set_elevate_max_low = -55
        set_elevate_max_high = 60
        set_elevate_max_step = 1
        set_sample_frequency_low = 1
        set_sample_frequency_high = 100
        set_sample_frequency_step = 1
        set_samples_per_orientation_low = 3
        set_samples_per_orientation_high = 10
        set_samples_per_orientation_step = 1
        set_step_change_low = 5
        set_step_change_high = 200
        set_step_change_step = 1
        
        self.groupbox_custom_scan = QtWidgets.QGroupBox()
        self.groupbox_custom_scan.setFont(font)
        ''' Accelerometer '''
        self.lcd_acc = QtWidgets.QLCDNumber()
        self.lcd_acc.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lcd_acc.setSmallDecimalPoint(False)
        self.lcd_acc.setObjectName("lcd_acc")
        self.lcd_acc.setFixedSize(120,50)
        '''begin'''
        self.label_azimuth_max = QtWidgets.QLabel()
        self.label_azimuth_max.setFixedSize(120,50)
        self.label_azimuth_max.setFont(font)
        self.label_azimuth_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azimuth_max.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azimuth_max.setText("Azimuth Max")

        self.label_azimuth_min = QtWidgets.QLabel()
        self.label_azimuth_min.setFixedSize(120,50)
        self.label_azimuth_min.setFont(font)
        self.label_azimuth_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_azimuth_min.setAlignment(QtCore.Qt.AlignCenter)
        self.label_azimuth_min.setText("Azimuth Min")
        
        self.label_elevation_max = QtWidgets.QLabel()
        self.label_elevation_max.setFixedSize(120,50)
        self.label_elevation_max.setFont(font)
        self.label_elevation_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_elevation_max.setAlignment(QtCore.Qt.AlignCenter)
        self.label_elevation_max.setText("Elevation Max")
        
        self.label_elevation_min = QtWidgets.QLabel()
        self.label_elevation_min.setFixedSize(120,50)
        self.label_elevation_min.setFont(font)
        self.label_elevation_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_elevation_min.setAlignment(QtCore.Qt.AlignCenter)
        self.label_elevation_min.setText("Elevation Max")
        
        self.label_step_change = QtWidgets.QLabel()
        self.label_step_change.setFixedSize(120,50)
        self.label_step_change.setFont(font)
        self.label_step_change.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_step_change.setAlignment(QtCore.Qt.AlignCenter)
        self.label_step_change.setText("Step Change")
        
        self.label_scan_frequency = QtWidgets.QLabel()
        self.label_scan_frequency.setFixedSize(120,50)
        self.label_scan_frequency.setFont(font)
        self.label_scan_frequency.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_scan_frequency.setAlignment(QtCore.Qt.AlignCenter)
        self.label_scan_frequency.setText("Scan Frequency")
        
        self.label_samples_orientation = QtWidgets.QLabel()
        self.label_samples_orientation.setFixedSize(120,50)
        self.label_samples_orientation.setFont(font)
        self.label_samples_orientation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label_samples_orientation.setAlignment(QtCore.Qt.AlignCenter)
        self.label_samples_orientation.setText("Samples/Orientation")
        '''sliders start'''
        self.slider_azimuth_max = QtWidgets.QSlider()
        self.slider_azimuth_max.setFixedSize(250,50)
        self.slider_azimuth_max.setFont(font)
        self.slider_azimuth_max.setOrientation(QtCore.Qt.Horizontal)
        self.slider_azimuth_max.setMinimum(set_azimuth_min_low)
        self.slider_azimuth_max.setMaximum(set_azimuth_min_high)
        self.slider_azimuth_max.setSingleStep(set_azimuth_min_step)
        
        self.slider_azimuth_min = QtWidgets.QSlider()
        self.slider_azimuth_min.setFixedSize(250,50)
        self.slider_azimuth_min.setFont(font)
        self.slider_azimuth_min.setOrientation(QtCore.Qt.Horizontal)
        self.slider_azimuth_min.setMinimum(set_azimuth_max_low)
        self.slider_azimuth_min.setMaximum(set_azimuth_max_high)
        self.slider_azimuth_min.setSingleStep(set_azimuth_max_step)
        
        self.slider_scan_frequency = QtWidgets.QSlider()
        self.slider_scan_frequency.setFixedSize(250,50)
        self.slider_scan_frequency.setFont(font)
        self.slider_scan_frequency.setOrientation(QtCore.Qt.Horizontal)
        self.slider_scan_frequency.setMinimum(set_sample_frequency_low)
        self.slider_scan_frequency.setMaximum(set_sample_frequency_high)
        self.slider_scan_frequency.setSingleStep(set_sample_frequency_step)

        self.slider_elevation_max = QtWidgets.QSlider()
        self.slider_elevation_max.setFixedSize(250,50)
        self.slider_elevation_max.setFont(font)
        self.slider_elevation_max.setOrientation(QtCore.Qt.Horizontal)
        self.slider_elevation_max.setMinimum(set_elevate_max_low)
        self.slider_elevation_max.setMaximum(set_elevate_max_high)
        self.slider_elevation_max.setSingleStep(set_elevate_max_step)

        self.slider_elevation_min = QtWidgets.QSlider()
        self.slider_elevation_min.setFixedSize(250,50)
        self.slider_elevation_min.setFont(font)
        self.slider_elevation_min.setOrientation(QtCore.Qt.Horizontal)
        self.slider_elevation_min.setMinimum(set_elevate_min_low)
        self.slider_elevation_min.setMaximum(set_elevate_min_high)
        self.slider_elevation_min.setSingleStep(set_elevate_min_step)
        
        self.slider_step_change = QtWidgets.QSlider()
        self.slider_step_change.setFixedSize(250,50)
        self.slider_step_change.setFont(font)
        self.slider_step_change.setOrientation(QtCore.Qt.Horizontal)
        self.slider_step_change.setMinimum(set_step_change_low)
        self.slider_step_change.setMaximum(set_step_change_high)
        self.slider_step_change.setSingleStep(set_step_change_step)
        
        self.slider_samples_orientation = QtWidgets.QSlider()
        self.slider_samples_orientation.setFixedSize(250,50)
        self.slider_samples_orientation.setFont(font)
        self.slider_samples_orientation.setOrientation(QtCore.Qt.Horizontal)
        self.slider_samples_orientation.setMinimum(set_samples_per_orientation_low)
        self.slider_samples_orientation.setMaximum(set_samples_per_orientation_high)
        self.slider_samples_orientation.setSingleStep(set_samples_per_orientation_step)
        ''' LCD '''
        self.lcd_azimuth_max = QtWidgets.QLCDNumber()
        self.lcd_azimuth_max.setFixedSize(120,50)
        self.lcd_azimuth_max.setFont(font)
        self.lcd_azimuth_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_azimuth_max.setFrameShadow(QtWidgets.QFrame.Plain)        
        self.lcd_azimuth_min = QtWidgets.QLCDNumber()
        self.lcd_azimuth_min.setFixedSize(120,50)
        self.lcd_azimuth_min.setFont(font)
        self.lcd_azimuth_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_azimuth_min.setFrameShadow(QtWidgets.QFrame.Plain)        
        self.lcd_elevation_max = QtWidgets.QLCDNumber()
        self.lcd_elevation_max.setFixedSize(120,50)
        self.lcd_elevation_max.setFont(font)
        self.lcd_elevation_max.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_elevation_max.setFrameShadow(QtWidgets.QFrame.Plain)        
        self.lcd_elevation_min = QtWidgets.QLCDNumber()
        self.lcd_elevation_min.setFixedSize(120,50)
        self.lcd_elevation_min.setFont(font)
        self.lcd_elevation_min.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_elevation_min.setFrameShadow(QtWidgets.QFrame.Plain)        
        self.lcd_step_change = QtWidgets.QLCDNumber()
        self.lcd_step_change.setFixedSize(120,50)
        self.lcd_step_change.setFont(font)
        self.lcd_step_change.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_step_change.setFrameShadow(QtWidgets.QFrame.Plain)
        self.lcd_scan_frequency = QtWidgets.QLCDNumber()
        self.lcd_scan_frequency.setFixedSize(120,50)
        self.lcd_scan_frequency.setFont(font)
        self.lcd_scan_frequency.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_scan_frequency.setFrameShadow(QtWidgets.QFrame.Plain)        
        self.lcd_samples_orientation = QtWidgets.QLCDNumber()
        self.lcd_samples_orientation.setFixedSize(120,50)
        self.lcd_samples_orientation.setFont(font)
        self.lcd_samples_orientation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lcd_samples_orientation.setFrameShadow(QtWidgets.QFrame.Plain)
        ''' Layout '''
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.vertical_layout_one = QtWidgets.QVBoxLayout()
        self.vertical_layout_two = QtWidgets.QVBoxLayout()
        self.vertical_layout_three = QtWidgets.QVBoxLayout()
        self.horizontal_layout.addWidget(self.button_main_menu)
        self.horizontal_layout.addWidget(self.button_finish_setting_values)
        self.horizontal_layout.addLayout(self.vertical_layout_one)
        self.horizontal_layout.addLayout(self.vertical_layout_two)
        self.horizontal_layout.addLayout(self.vertical_layout_three)
        ''' Add Widget '''
        self.vertical_layout_one.addWidget(self.label_azimuth_max)
        self.vertical_layout_one.addWidget(self.label_azimuth_min)
        self.vertical_layout_one.addWidget(self.label_elevation_max)
        self.vertical_layout_one.addWidget(self.label_elevation_min)
        self.vertical_layout_one.addWidget(self.label_step_change)
        self.vertical_layout_one.addWidget(self.label_scan_frequency)
        self.vertical_layout_one.addWidget(self.label_samples_orientation)
        self.vertical_layout_two.addWidget(self.slider_azimuth_max)
        self.vertical_layout_two.addWidget(self.slider_azimuth_min)
        self.vertical_layout_two.addWidget(self.slider_elevation_max)
        self.vertical_layout_two.addWidget(self.slider_elevation_min)
        self.vertical_layout_two.addWidget(self.slider_step_change)
        self.vertical_layout_two.addWidget(self.slider_scan_frequency)
        self.vertical_layout_two.addWidget(self.slider_samples_orientation)
        self.vertical_layout_three.addWidget(self.lcd_azimuth_max)
        self.vertical_layout_three.addWidget(self.lcd_azimuth_min)
        self.vertical_layout_three.addWidget(self.lcd_elevation_max)
        self.vertical_layout_three.addWidget(self.lcd_elevation_min)
        self.vertical_layout_three.addWidget(self.lcd_step_change)
        self.vertical_layout_three.addWidget(self.lcd_scan_frequency)
        self.vertical_layout_three.addWidget(self.lcd_samples_orientation)
        self.setWindowTitle("Graph Console")
    """ Azimuth Max Slider
      @param self The object pointer."""
    def azimuth_max_change(self):
        size = self.slider_azimuth_max.value()
        self.lcd_azimuth_max.display(size)
    """ Azimuth Min Slider.
      @param self The object pointer."""
    def azimuth_min_change(self):
        size = self.slider_azimuth_min.value()
        self.lcd_azimuth_min.display(size)
    """ Elevation Max Slider.
      @param self The object pointer."""
    def elevation_max_change(self):
        size = self.slider_elevation_max.value()
        self.lcd_elevation_max.display(size)
    """ Azimuth Max Slider.
      @param self The object pointer."""
    def elevation_min_change(self):
        size = self.slider_elevation_min.value()
        self.lcd_elevation_min.display(size)
    """ Elevation Min Slider.
      @param self The object pointer."""
    def scan_frequency_change(self):
        size = self.slider_scan_frequency.value()
        self.lcd_scan_frequency.display(size)
    """ Step Change Slider.
      @param self The object pointer."""
    def step_change_change(self):
        size = self.slider_step_change.value()
        self.lcd_step_change.display(size)
    """ Samples per orientaion Slider.
      @param self The object pointer."""
    def samples_orientation_change(self):
        size = self.slider_samples_orientation.value()
        self.lcd_samples_orientation.display(size)
    """ Button for main menu
      @param self The object pointer."""
    def button_main_menu_click(self):
        self.main_menu = GraphConsole()
        self.main_menu.show()
        self.main_menu.setAttribute(Qt.WA_DeleteOnClose)
        self.close()
    """ Button to trigger the beggining of the custom scan. takes the values here and sends them via serial to modify the scan
      @param self The object pointer."""
    def button_finish_setting_values_click(self):
        self.finish_setting_values = GraphConsole()
        self.finish_setting_values.show()
        t_a = self.lcd_azimuth_min.value()
        t_b = self.lcd_azimuth_max.value()
        t_c = self.lcd_elevation_min.value()
        t_d = self.lcd_elevation_max.value()
        t_f = self.lcd_step_change.value()
        t_g = self.lcd_samples_orientation.value()
        t_h = self.lcd_scan_frequency.value()
        temp_string = f'-a={t_a},{t_b}-e={t_c},{t_d}-s{t_f}.'
        self.serial.write(temp_string.encode())
        self.finish_setting_values.setAttribute(Qt.WA_DeleteOnClose)
        self.close()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = RangeFinder()
    ''' Sliders '''
    w.button_quick_scan.clicked.connect(w.button_quick_scan_click)
    w.button_deep_scan.clicked.connect(w.button_deep_scan_click)
    w.button_custom_scan.clicked.connect(w.button_custom_scan_click)
    w.button_calibrate.clicked.connect(w.button_calibrate_click)
    w.button_ptu_control.clicked.connect(w.button_ptu_control_click)
    w.button_help.clicked.connect(w.button_help_click)
    w.show()
    sys.exit(app.exec_())