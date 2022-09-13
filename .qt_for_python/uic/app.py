# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSplitter, QStatusBar,
    QTabWidget, QTextEdit, QToolBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(976, 677)
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
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_8 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
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
        self.verticalLayout_4 = QVBoxLayout(self.tab_files)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.listWidget_files = QListWidget(self.tab_files)
        self.listWidget_files.setObjectName(u"listWidget_files")

        self.verticalLayout_4.addWidget(self.listWidget_files)

        icon = QIcon()
        iconThemeName = u"zoom-in"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.tabWidget_2.addTab(self.tab_files, icon, "")
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

        self.verticalLayout.addWidget(self.listWidget_orbitals)

        self.tabWidget_2.addTab(self.tab_orbitals, "")
        self.tab_clouds = QWidget()
        self.tab_clouds.setObjectName(u"tab_clouds")
        self.verticalLayout_5 = QVBoxLayout(self.tab_clouds)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.listWidget_clouds = QListWidget(self.tab_clouds)
        self.listWidget_clouds.setObjectName(u"listWidget_clouds")

        self.verticalLayout_5.addWidget(self.listWidget_clouds)

        self.tabWidget_2.addTab(self.tab_clouds, "")
        self.splitter_2.addWidget(self.tabWidget_2)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(3)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy2)
        self.splitter.setOrientation(Qt.Vertical)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout_canvas = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_canvas.setObjectName(u"verticalLayout_canvas")
        self.verticalLayout_canvas.setContentsMargins(0, 0, 0, 0)
        self.canvas = QFrame(self.verticalLayoutWidget)
        self.canvas.setObjectName(u"canvas")
        self.canvas.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy1)
        self.canvas.setMinimumSize(QSize(0, 0))
        self.canvas.setBaseSize(QSize(400, 500))
        self.canvas.setFrameShape(QFrame.StyledPanel)
        self.canvas.setFrameShadow(QFrame.Plain)

        self.verticalLayout_canvas.addWidget(self.canvas)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)

        self.verticalLayout_canvas.addWidget(self.label)

        self.verticalLayout_canvas.setStretch(1, 1)
        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_log = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_log.setObjectName(u"verticalLayout_log")
        self.verticalLayout_log.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit(self.verticalLayoutWidget_2)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy4)
        font = QFont()
        font.setFamilies([u"Consolas"])
        self.lineEdit.setFont(font)

        self.verticalLayout_log.addWidget(self.lineEdit)

        self.tabWidget = QTabWidget(self.verticalLayoutWidget_2)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tabWidget.setBaseSize(QSize(0, 200))
        self.tab_log = QWidget()
        self.tab_log.setObjectName(u"tab_log")
        self.verticalLayout_2 = QVBoxLayout(self.tab_log)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textLog = QTextEdit(self.tab_log)
        self.textLog.setObjectName(u"textLog")
        self.textLog.setMinimumSize(QSize(0, 0))

        self.verticalLayout_2.addWidget(self.textLog)

        self.tabWidget.addTab(self.tab_log, "")
        self.tab_info = QWidget()
        self.tab_info.setObjectName(u"tab_info")
        self.verticalLayout_3 = QVBoxLayout(self.tab_info)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.textInfo = QTextEdit(self.tab_info)
        self.textInfo.setObjectName(u"textInfo")

        self.verticalLayout_3.addWidget(self.textInfo)

        self.tabWidget.addTab(self.tab_info, "")

        self.verticalLayout_log.addWidget(self.tabWidget)

        self.splitter.addWidget(self.verticalLayoutWidget_2)
        self.splitter_2.addWidget(self.splitter)

        self.verticalLayout_8.addWidget(self.splitter_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 976, 22))
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
        self.menuview.addAction(self.actionlabel)
        self.menuselect.addAction(self.actionclear)
        self.toolBar.addAction(self.actionclear)

        self.retranslateUi(MainWindow)

        self.tabWidget_2.setCurrentIndex(2)
        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionopen.setText(QCoreApplication.translate("MainWindow", u"open", None))
        self.actionpiBondOrder.setText(QCoreApplication.translate("MainWindow", u"piBondOrder", None))
        self.actionpiSelectOrder.setText(QCoreApplication.translate("MainWindow", u"piSelectOrder", None))
        self.actionlabel.setText(QCoreApplication.translate("MainWindow", u"label", None))
        self.actionclear.setText(QCoreApplication.translate("MainWindow", u"clear", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_files), QCoreApplication.translate("MainWindow", u"files", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_orbitals), QCoreApplication.translate("MainWindow", u"orbitals", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_clouds), QCoreApplication.translate("MainWindow", u"clouds", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_log), QCoreApplication.translate("MainWindow", u"logo", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_info), QCoreApplication.translate("MainWindow", u"info", None))
        self.menufile.setTitle(QCoreApplication.translate("MainWindow", u"file", None))
        self.menucompute.setTitle(QCoreApplication.translate("MainWindow", u"compute", None))
        self.menuview.setTitle(QCoreApplication.translate("MainWindow", u"view", None))
        self.menuselect.setTitle(QCoreApplication.translate("MainWindow", u"select", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

