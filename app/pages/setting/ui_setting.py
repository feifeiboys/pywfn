# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QSizePolicy,
    QSlider, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_setting(object):
    def setupUi(self, setting):
        if not setting.objectName():
            setting.setObjectName(u"setting")
        setting.resize(1010, 643)
        self.verticalLayout = QVBoxLayout(setting)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(setting)
        self.tabWidget.setObjectName(u"tabWidget")
        self.mainTab = QWidget()
        self.mainTab.setObjectName(u"mainTab")
        self.tabWidget.addTab(self.mainTab, "")
        self.colorTab = QWidget()
        self.colorTab.setObjectName(u"colorTab")
        self.verticalLayout_3 = QVBoxLayout(self.colorTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget = QTableWidget(self.colorTab)
        if (self.tableWidget.columnCount() < 8):
            self.tableWidget.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)

        self.horizontalLayout.addWidget(self.tableWidget)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_7 = QLabel(self.colorTab)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_2.addWidget(self.label_7)

        self.frame = QFrame(self.colorTab)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.frame)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.lineEdit = QLineEdit(self.frame)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lineEdit)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.ctl_metalic = QSlider(self.frame)
        self.ctl_metalic.setObjectName(u"ctl_metalic")
        self.ctl_metalic.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.ctl_metalic)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.ctl_roughness = QSlider(self.frame)
        self.ctl_roughness.setObjectName(u"ctl_roughness")
        self.ctl_roughness.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.ctl_roughness)

        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.ctl_opacity = QSlider(self.frame)
        self.ctl_opacity.setObjectName(u"ctl_opacity")
        self.ctl_opacity.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.ctl_opacity)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.ctl_diffuse = QSlider(self.frame)
        self.ctl_diffuse.setObjectName(u"ctl_diffuse")
        self.ctl_diffuse.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.ctl_diffuse)

        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_6)

        self.ctl_specular = QSlider(self.frame)
        self.ctl_specular.setObjectName(u"ctl_specular")
        self.ctl_specular.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.ctl_specular)

        self.label_8 = QLabel(self.frame)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_8)

        self.ctl_radius = QSlider(self.frame)
        self.ctl_radius.setObjectName(u"ctl_radius")
        self.ctl_radius.setTracking(True)
        self.ctl_radius.setOrientation(Qt.Horizontal)
        self.ctl_radius.setTickPosition(QSlider.NoTicks)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.ctl_radius)


        self.verticalLayout_2.addWidget(self.frame)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 7)
        self.horizontalLayout.setStretch(1, 3)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.tabWidget.addTab(self.colorTab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(setting)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(setting)
    # setupUi

    def retranslateUi(self, setting):
        setting.setWindowTitle(QCoreApplication.translate("setting", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mainTab), QCoreApplication.translate("setting", u"Tab 1", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("setting", u"symbol", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("setting", u"color", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("setting", u"metallic", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("setting", u"roughness", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("setting", u"opacity", None));
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("setting", u"diffuse", None));
        ___qtablewidgetitem6 = self.tableWidget.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("setting", u"specular", None));
        ___qtablewidgetitem7 = self.tableWidget.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("setting", u"size", None));
        self.label_7.setText(QCoreApplication.translate("setting", u"\u9884\u89c8", None))
        self.label.setText(QCoreApplication.translate("setting", u"color", None))
        self.label_2.setText(QCoreApplication.translate("setting", u"metallic", None))
        self.label_3.setText(QCoreApplication.translate("setting", u"roughness", None))
        self.label_4.setText(QCoreApplication.translate("setting", u"opacity", None))
        self.label_5.setText(QCoreApplication.translate("setting", u"diffuse", None))
        self.label_6.setText(QCoreApplication.translate("setting", u"specular", None))
        self.label_8.setText(QCoreApplication.translate("setting", u"size", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.colorTab), QCoreApplication.translate("setting", u"Tab 2", None))
    # retranslateUi

