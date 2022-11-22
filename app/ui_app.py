# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.3.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGridLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QSlider, QSplitter,
    QStatusBar, QTabWidget, QTextBrowser, QToolBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.NonModal)
        MainWindow.resize(1045, 706)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QTabWidget.Rounded)
        self.actionopen = QAction(MainWindow)
        self.actionopen.setObjectName(u"actionopen")
        self.actionpiBondOrder = QAction(MainWindow)
        self.actionpiBondOrder.setObjectName(u"actionpiBondOrder")
        self.actionpiSelectOrder = QAction(MainWindow)
        self.actionpiSelectOrder.setObjectName(u"actionpiSelectOrder")
        self.actionlabel = QAction(MainWindow)
        self.actionlabel.setObjectName(u"actionlabel")
        self.actionclear = QAction(MainWindow)
        self.actionclear.setObjectName(u"actionclear")
        self.actionsigmaBondOrder = QAction(MainWindow)
        self.actionsigmaBondOrder.setObjectName(u"actionsigmaBondOrder")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_5 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.tabWidget_2 = QTabWidget(self.splitter_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tabWidget_2.setBaseSize(QSize(200, 0))
        self.tabWidget_2.setTabPosition(QTabWidget.West)
        self.tab_files = QWidget()
        self.tab_files.setObjectName(u"tab_files")
        self.verticalLayout_3 = QVBoxLayout(self.tab_files)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidget_files = QListWidget(self.tab_files)
        self.listWidget_files.setObjectName(u"listWidget_files")
        self.listWidget_files.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_3.addWidget(self.listWidget_files)

        self.tabWidget_2.addTab(self.tab_files, "")
        self.tab_orbitals = QWidget()
        self.tab_orbitals.setObjectName(u"tab_orbitals")
        self.verticalLayout = QVBoxLayout(self.tab_orbitals)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidget_orbitals = QListWidget(self.tab_orbitals)
        self.listWidget_orbitals.setObjectName(u"listWidget_orbitals")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidget_orbitals.sizePolicy().hasHeightForWidth())
        self.listWidget_orbitals.setSizePolicy(sizePolicy1)
        self.listWidget_orbitals.setBaseSize(QSize(400, 0))
        self.listWidget_orbitals.setFrameShape(QFrame.NoFrame)

        self.verticalLayout.addWidget(self.listWidget_orbitals)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.radioCloud = QRadioButton(self.tab_orbitals)
        self.radioCloud.setObjectName(u"radioCloud")

        self.gridLayout.addWidget(self.radioCloud, 0, 1, 1, 1)

        self.radioVector = QRadioButton(self.tab_orbitals)
        self.radioVector.setObjectName(u"radioVector")
        self.radioVector.setChecked(True)

        self.gridLayout.addWidget(self.radioVector, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(self.tab_orbitals)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.cloudRangeSlider = QSlider(self.tab_orbitals)
        self.cloudRangeSlider.setObjectName(u"cloudRangeSlider")
        self.cloudRangeSlider.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.cloudRangeSlider)


        self.verticalLayout.addLayout(self.formLayout)

        self.clearCloudBtn = QPushButton(self.tab_orbitals)
        self.clearCloudBtn.setObjectName(u"clearCloudBtn")

        self.verticalLayout.addWidget(self.clearCloudBtn)

        self.tabWidget_2.addTab(self.tab_orbitals, "")
        self.tab_clouds = QWidget()
        self.tab_clouds.setObjectName(u"tab_clouds")
        self.verticalLayout_6 = QVBoxLayout(self.tab_clouds)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.listWidget_clouds = QListWidget(self.tab_clouds)
        self.listWidget_clouds.setObjectName(u"listWidget_clouds")
        self.listWidget_clouds.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_6.addWidget(self.listWidget_clouds)

        self.tabWidget_2.addTab(self.tab_clouds, "")
        self.splitter_2.addWidget(self.tabWidget_2)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.canvasWidget = QWidget(self.splitter)
        self.canvasWidget.setObjectName(u"canvasWidget")
        self.verticalLayout_4 = QVBoxLayout(self.canvasWidget)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.canvasLayout = QVBoxLayout()
        self.canvasLayout.setSpacing(0)
        self.canvasLayout.setObjectName(u"canvasLayout")

        self.verticalLayout_4.addLayout(self.canvasLayout)

        self.splitter.addWidget(self.canvasWidget)
        self.lineEdit = QLineEdit(self.splitter)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setFamilies([u"Consolas"])
        self.lineEdit.setFont(font)
        self.splitter.addWidget(self.lineEdit)
        self.log = QTextBrowser(self.splitter)
        self.log.setObjectName(u"log")
        self.splitter.addWidget(self.log)
        self.splitter_2.addWidget(self.splitter)
        self.widget = QWidget(self.splitter_2)
        self.widget.setObjectName(u"widget")
        self.info = QVBoxLayout(self.widget)
        self.info.setObjectName(u"info")
        self.info.setContentsMargins(0, 0, 0, 0)
        self.imgLabel = QLabel(self.widget)
        self.imgLabel.setObjectName(u"imgLabel")

        self.info.addWidget(self.imgLabel)

        self.textBrowser = QTextBrowser(self.widget)
        self.textBrowser.setObjectName(u"textBrowser")

        self.info.addWidget(self.textBrowser)

        self.splitter_2.addWidget(self.widget)

        self.verticalLayout_5.addWidget(self.splitter_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1045, 22))
        self.menufile = QMenu(self.menubar)
        self.menufile.setObjectName(u"menufile")
        self.menucompute = QMenu(self.menubar)
        self.menucompute.setObjectName(u"menucompute")
        self.menuview = QMenu(self.menubar)
        self.menuview.setObjectName(u"menuview")
        self.menuselect = QMenu(self.menubar)
        self.menuselect.setObjectName(u"menuselect")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menufile.menuAction())
        self.menubar.addAction(self.menucompute.menuAction())
        self.menubar.addAction(self.menuview.menuAction())
        self.menubar.addAction(self.menuselect.menuAction())
        self.menufile.addAction(self.actionopen)
        self.menucompute.addAction(self.actionpiBondOrder)
        self.menucompute.addAction(self.actionpiSelectOrder)
        self.menucompute.addAction(self.actionsigmaBondOrder)
        self.menuview.addAction(self.actionlabel)
        self.menuselect.addAction(self.actionclear)
        self.toolBar.addAction(self.actionclear)

        self.retranslateUi(MainWindow)

        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"HFV", None))
        self.actionopen.setText(QCoreApplication.translate("MainWindow", u"open", None))
        self.actionpiBondOrder.setText(QCoreApplication.translate("MainWindow", u"piBondOrder", None))
        self.actionpiSelectOrder.setText(QCoreApplication.translate("MainWindow", u"piSelectOrder", None))
        self.actionlabel.setText(QCoreApplication.translate("MainWindow", u"label", None))
        self.actionclear.setText(QCoreApplication.translate("MainWindow", u"clear", None))
        self.actionsigmaBondOrder.setText(QCoreApplication.translate("MainWindow", u"sigmaBondOrder", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_files), QCoreApplication.translate("MainWindow", u"files", None))
        self.radioCloud.setText(QCoreApplication.translate("MainWindow", u"\u7bad\u5934", None))
        self.radioVector.setText(QCoreApplication.translate("MainWindow", u"\u70b9\u4e91", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u8303\u56f4", None))
        self.clearCloudBtn.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u9664", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_orbitals), QCoreApplication.translate("MainWindow", u"orbitals", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_clouds), QCoreApplication.translate("MainWindow", u"clouds", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"input command here", None))
        self.imgLabel.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u50cf", None))
        self.textBrowser.setPlaceholderText("")
        self.menufile.setTitle(QCoreApplication.translate("MainWindow", u"file", None))
        self.menucompute.setTitle(QCoreApplication.translate("MainWindow", u"compute", None))
        self.menuview.setTitle(QCoreApplication.translate("MainWindow", u"view", None))
        self.menuselect.setTitle(QCoreApplication.translate("MainWindow", u"select", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

