# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSplitter, QStatusBar, QTableWidget, QTableWidgetItem,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(911, 607)
        self.action_import = QAction(MainWindow)
        self.action_import.setObjectName(u"action_import")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.list = QListWidget(self.widget)
        self.list.setObjectName(u"list")
        self.list.setMinimumSize(QSize(200, 0))

        self.verticalLayout_2.addWidget(self.list)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.route_input = QLineEdit(self.widget)
        self.route_input.setObjectName(u"route_input")

        self.horizontalLayout.addWidget(self.route_input)

        self.route_btn = QPushButton(self.widget)
        self.route_btn.setObjectName(u"route_btn")

        self.horizontalLayout.addWidget(self.route_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.widget)
        self.widget1 = QWidget(self.splitter)
        self.widget1.setObjectName(u"widget1")
        self.verticalLayout_3 = QVBoxLayout(self.widget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_2 = QLineEdit(self.widget1)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.verticalLayout_3.addWidget(self.lineEdit_2)

        self.table = QTableWidget(self.widget1)
        self.table.setObjectName(u"table")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.table)

        self.splitter.addWidget(self.widget1)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.img = QLabel(self.layoutWidget)
        self.img.setObjectName(u"img")
        self.img.setMinimumSize(QSize(0, 200))

        self.verticalLayout.addWidget(self.img)

        self.text = QTextBrowser(self.layoutWidget)
        self.text.setObjectName(u"text")
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(10)
        self.text.setFont(font)

        self.verticalLayout.addWidget(self.text)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_4.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 911, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action_import)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"gaussian Manager", None))
        self.action_import.setText(QCoreApplication.translate("MainWindow", u"import", None))
        self.route_btn.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0", None))
        self.img.setText("")
        self.text.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"</style></head><body style=\" font-family:'Consolas'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"file", None))
    # retranslateUi

