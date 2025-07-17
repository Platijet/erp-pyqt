import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

from dialogs import AddProductDialog
from database import Session
from models import Product


class InventoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = Session()

        # Search & Add button
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Εύρεση…")
        self.btn_add = QPushButton("Προσθήκη")

        hl = QHBoxLayout()
        hl.addWidget(self.search_input)
        hl.addWidget(self.btn_add)

        # Table + model + proxy
        self.model = QStandardItemModel()
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(hl)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Connections
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.search_input.textChanged.connect(self.on_search)

        # Load data
        self.load_data()

    def load_data(self):
        self.model.clear()
        headers = [
            "ID", "SKU-Man", "SKU-Sup", "Supplier", "Name", "Desc",
            "Size", "Color", "SKU", "Season", "Qty", "Position",
            "Category", "VAT", "CostEx", "CostInc", "PriceInc",
            "Disc1", "Disc2", "SUB-SKU"
        ]
        self.model.setHorizontalHeaderLabels(headers)

        for p in self.session.query(Product).all():
            try:
                vat_pct = float(p.vat.strip('%')) / 100
            except Exception:
                vat_pct = 0.0
            cost_inc = p.cost_ex * (1 + vat_pct)
            row = [
                QStandardItem(str(p.id)),
                QStandardItem(p.sku_manufacturer or ""),
                QStandardItem(p.sku_supplier or ""),
                QStandardItem(p.supplier or ""),
                QStandardItem(p.name),
                QStandardItem(p.description),
                QStandardItem(p.size or ""),
                QStandardItem(p.color or ""),
                QStandardItem(p.sku),
                QStandardItem(p.season),
                QStandardItem(str(p.quantity)),
                QStandardItem(p.position),
                QStandardItem(p.category),
                QStandardItem(p.vat),
                QStandardItem(f"{p.cost_ex:.2f}"),
                QStandardItem(f"{cost_inc:.2f}"),
                QStandardItem(f"{p.price_inc:.2f}"),
                QStandardItem(f"{p.discount1_inc:.2f}"),
                QStandardItem(f"{p.discount2_inc:.2f}"),
                QStandardItem(p.format_str)
            ]
            self.model.appendRow(row)

        self.table.resizeColumnsToContents()

    def open_add_dialog(self):
        dlg = AddProductDialog(self)
        if dlg.exec_():
            self.load_data()

    def on_search(self, text):
        regex = QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString)
        self.proxy.setFilterRegExp(regex)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Αυξάνουμε το default font size σε όλα τα widgets
    font = app.font()
    font.setPointSize(12)   # διάλεξε το μέγεθος που σε βολεύει
    app.setFont(font)

    window = QMainWindow()
    window.setWindowTitle("ERP System")
    window.resize(1500, 800)

    tabs = QTabWidget()
    tabs.addTab(QWidget(), "ΠΩΛΗΣΕΙΣ")
    tabs.addTab(QWidget(), "ΕΞΟΔΑ")
    tabs.addTab(InventoryTab(), "ΑΠΟΘΗΚΕΣ")
    tabs.addTab(QWidget(), "ΠΡΟΜΗΘΕΥΤΕΣ")
    tabs.addTab(QWidget(), "ΠΕΛΑΤΕΣ")
    tabs.addTab(QWidget(), "STATS")
    tabs.addTab(QWidget(), "ΡΥΘΜΙΣΕΙΣ")

    window.setCentralWidget(tabs)
    window.show()

    sys.exit(app.exec_())
