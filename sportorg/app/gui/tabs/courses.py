import logging

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView

from sportorg.app.gui.dialogs.course_edit import CourseEditDialog
from sportorg.app.models.memory_model import CourseMemoryModel
from sportorg.app.gui.tabs.table import TableView
from sportorg.app.gui.global_access import GlobalAccess

from sportorg.language import _


class CoursesTableView(TableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.popup_items = [
            (_("Add object"), GlobalAccess().add_object)
        ]


class Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setAcceptDrops(False)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setAutoFillBackground(False)
        self.course_layout = QtWidgets.QGridLayout(self)
        self.course_layout.setObjectName("course_layout")

        self.CourseTable = CoursesTableView(self)
        self.CourseTable.setObjectName("CourseTable")
        self.CourseTable.setModel(CourseMemoryModel())
        self.CourseTable.setSortingEnabled(True)
        self.CourseTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        hor_header = self.CourseTable.horizontalHeader()
        assert (isinstance(hor_header, QHeaderView))
        hor_header.setSectionsMovable(True)
        hor_header.setDropIndicatorShown(True)
        hor_header.setSectionResizeMode(QHeaderView.ResizeToContents)

        def course_double_clicked(index):
            logging.debug('Courses - clicked on ' + str(index.row()))
            try:
                dialog = CourseEditDialog(self.CourseTable, index)
                dialog.exec()
            except Exception as e:
                logging.exception(e)

        self.CourseTable.activated.connect(course_double_clicked)
        self.course_layout.addWidget(self.CourseTable)

    def get_table(self):
        return self.CourseTable