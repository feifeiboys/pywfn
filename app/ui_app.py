# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSplitter,
    QStatusBar, QTabWidget, QTextBrowser, QToolBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.NonModal)
        MainWindow.resize(895, 706)
        MainWindow.setStyleSheet(u"#canvas{\n"
"height:80%;\n"
"background-color:gray;\n"
"}")
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
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter_2.setHandleWidth(0)
        self.icons = QFrame(self.splitter_2)
        self.icons.setObjectName(u"icons")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icons.sizePolicy().hasHeightForWidth())
        self.icons.setSizePolicy(sizePolicy)
        self.icons.setMinimumSize(QSize(40, 0))
        self.icons.setMaximumSize(QSize(40, 16777215))
        self.icons.setFrameShape(QFrame.NoFrame)
        self.icons.setFrameShadow(QFrame.Sunken)
        self.icons.setLineWidth(0)
        self.splitter_2.addWidget(self.icons)
        self.view = QFrame(self.splitter_2)
        self.view.setObjectName(u"view")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(4)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.view.sizePolicy().hasHeightForWidth())
        self.view.setSizePolicy(sizePolicy1)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setFrameShadow(QFrame.Raised)
        self.view.setLineWidth(0)
        self.splitter_2.addWidget(self.view)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(10)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy2)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(1)
        self.fileTab = QFrame(self.splitter)
        self.fileTab.setObjectName(u"fileTab")
        self.fileTab.setFrameShape(QFrame.StyledPanel)
        self.fileTab.setFrameShadow(QFrame.Raised)
        self.splitter.addWidget(self.fileTab)
        self.canvas = QFrame(self.splitter)
        self.canvas.setObjectName(u"canvas")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(4)
        sizePolicy3.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy3)
        self.canvas.setFrameShape(QFrame.WinPanel)
        self.splitter.addWidget(self.canvas)
        self.command = QLineEdit(self.splitter)
        self.command.setObjectName(u"command")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.command.sizePolicy().hasHeightForWidth())
        self.command.setSizePolicy(sizePolicy4)
        font = QFont()
        font.setFamilies([u"Consolas"])
        self.command.setFont(font)
        self.splitter.addWidget(self.command)
        self.log = QTextBrowser(self.splitter)
        self.log.setObjectName(u"log")
        self.splitter.addWidget(self.log)
        self.splitter_2.addWidget(self.splitter)

        self.verticalLayout.addWidget(self.splitter_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 895, 22))
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
        self.command.setPlaceholderText(QCoreApplication.translate("MainWindow", u"input command here", None))
        self.menufile.setTitle(QCoreApplication.translate("MainWindow", u"file", None))
        self.menucompute.setTitle(QCoreApplication.translate("MainWindow", u"compute", None))
        self.menuview.setTitle(QCoreApplication.translate("MainWindow", u"view", None))
        self.menuselect.setTitle(QCoreApplication.translate("MainWindow", u"select", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

