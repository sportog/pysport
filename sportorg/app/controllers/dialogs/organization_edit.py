import sys
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFormLayout, QLabel, \
    QLineEdit, QComboBox, QCompleter, QApplication, QTableView, QDialog, \
    QPushButton

from sportorg.app.controllers.global_access import GlobalAccess
from sportorg.app.models.memory import race, Organization


def get_countries():
    return ['Russia', 'Finland', 'Norway', 'Germany', 'France', 'Austria', 'Kazakhstan', 'Ukraine', 'Poland', 'Estonia']


def get_regions():
    return ['Тюменская обл.', 'Курганская обл.', 'Свердловская обл.', 'Челябинская обл.', 'Республика Коми', 'г.Москва',
            'ХМАО-Югра']


class AdvComboBox(QComboBox):
    """
    Combo with autocomplete
    Found in Internet by Sergei
    """

    def __init__(self, parent=None):
        super(AdvComboBox, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

        self.setCompleter(self.completer)

        # connect signals

        def filter_function(text):
            self.pFilterModel.setFilterFixedString(str(text))

        self.lineEdit().textEdited.connect(filter_function)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(str(text))
            self.setCurrentIndex(index)


class OrganizationEditDialog(QDialog):
    def __init__(self, table=None, index=None):
        super().__init__()
        self.init_ui()
        if table is not None:
            self.set_values_from_table(table, index)

    def close_dialog(self):
        self.close()

    def init_ui(self):
        self.setWindowTitle('Team properties')
        self.setWindowIcon(QIcon('sportorg.ico'))
        self.setSizeGripEnabled(False)
        self.setModal(True)
        self.setToolTip('Team Edit Window')

        self.layout = QFormLayout(self)

        self.label_name = QLabel('Name')
        self.item_name = QLineEdit()
        self.layout.addRow(self.label_name, self.item_name)

        self.label_country = QLabel('Country')
        self.item_country = AdvComboBox()
        self.item_country.addItems(get_countries())
        self.layout.addRow(self.label_country, self.item_country)

        self.label_region = QLabel('Region')
        self.item_region = AdvComboBox()
        self.item_region.addItems(get_regions())
        self.layout.addRow(self.label_region, self.item_region)

        self.label_contact = QLabel('Contact')
        self.item_contact = QLineEdit()
        self.layout.addRow(self.label_contact, self.item_contact)

        self.label_address = QLabel('Address')
        self.item_address = QLineEdit()
        self.layout.addRow(self.label_address, self.item_address)

        def cancel_changes():
            self.close()

        def apply_changes():
            try:
                self.apply_changes_impl()
            except:
                print(sys.exc_info())
                traceback.print_exc()
            self.close()

        self.button_ok = QPushButton('OK')
        self.button_ok.clicked.connect(apply_changes)
        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.clicked.connect(cancel_changes)
        self.layout.addRow(self.button_ok, self.button_cancel)

        self.show()

    def set_values_from_table(self, table, index):
        self.table = table
        self.current_index = index
        assert (isinstance(table, QTableView))
        model = table.model()
        assert (isinstance(model, QSortFilterProxyModel))
        orig_index = model.mapToSource(index)
        assert (isinstance(orig_index, QModelIndex))
        orig_index_int = orig_index.row()

        current_object = race().organizations[orig_index_int]
        assert (isinstance(current_object, Organization))
        self.current_object = current_object

        self.item_name.setText(current_object.name)

        if current_object.country is not None:
            self.item_country.setCurrentText(current_object.country.name)
        if current_object.region is not None:
            self.item_region.setCurrentText(current_object.region)
        if current_object.contact is not None:
            self.item_contact.setText(current_object.contact.name)
        if current_object.address is not None:
            self.item_address.setText(current_object.address.street)

    def apply_changes_impl(self):
        changed = False
        org = self.current_object
        assert (isinstance(org, Organization))

        if org.name != self.item_name.text():
            org.name = self.item_name.text()
            changed = True

        if org.country.name != self.item_country.currentText():
            org.country.name = self.item_country.currentText()
            changed = True

        if org.region != self.item_region.currentText():
            org.region = self.item_region.currentText()
            changed = True

        if org.contact != self.item_contact.text():
            org.contact.name = self.item_contact.text()
            changed = True

        if org.address != self.item_address.text():
            org.address.street = self.item_address.text()
            changed = True

        if changed:
            self.get_parent_window().refresh()
            # table.model().sourceModel().update_one_object(part, table.model().mapToSource(self.current_index).row())

    def get_parent_window(self):
        return GlobalAccess().get_main_window()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OrganizationEditDialog()
    sys.exit(app.exec_())