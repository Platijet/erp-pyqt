# dialogs.py

from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QLineEdit, QLabel, QPushButton,
    QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit,
    QFormLayout, QHBoxLayout, QVBoxLayout, QScrollArea,
    QMessageBox, QInputDialog, QAbstractSpinBox, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from sqlalchemy.exc import IntegrityError
from database import Session
from models import Product


class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()
    def textFromValue(self, value):
        # επιτρέπει κενό όταν value == minimum()
        if value == self.minimum():
            return ""
        return super().textFromValue(value)


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()
    def textFromValue(self, value):
        if value == self.minimum():
            return ""
        return super().textFromValue(value)


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Προσθήκη Προϊόντος")
        self.setMinimumWidth(800)
        self.session = Session()

        bold = QFont()
        bold.setBold(True)

        # — A1: SKU/Barcode Κατασκευαστή
        self.le_sku_man = QLineEdit()
        self.lbl_sku_man_warn = QLabel(); self.lbl_sku_man_warn.setFont(bold)
        self.lbl_sku_man_warn.setStyleSheet("color: red;")

        # — A2: SKU/Barcode Προμηθευτή
        self.le_sku_sup = QLineEdit()
        self.lbl_sku_sup_warn = QLabel(); self.lbl_sku_sup_warn.setFont(bold)
        self.lbl_sku_sup_warn.setStyleSheet("color: red;")

        # — Προμηθευτής
        self.cb_supplier = NoWheelComboBox(); self.cb_supplier.setEditable(True)
        self.cb_supplier.addItem(""); self.btn_add_supplier = QPushButton("ADD")
        sup_layout = QHBoxLayout(); sup_layout.addWidget(self.cb_supplier); sup_layout.addWidget(self.btn_add_supplier)

        # — A3: Όνομα Προϊόντος
        self.le_name = QLineEdit()

        # — A4: Περιγραφή Προϊόντος
        self.te_desc = QTextEdit()

        # — A5: Μέγεθος
        self.le_size = QLineEdit()
        self.cb_no_size = QCheckBox("Δεν υπόκειται σε μέγεθος")

        # — A6: Χρώμα
        self.le_color = QLineEdit()
        self.cb_no_color = QCheckBox("Δεν υπόκειται σε χρώμα")

        # — A7: SKU Προϊόντος + Αυτόματη δημιουργία
        self.le_sku = QLineEdit()
        self.cb_auto_sku = QCheckBox("Αυτόματη δημιουργία SKU")
        self.cb_auto_sku.setChecked(True)

        # — A8: Εποχικό
        self.cb_season = NoWheelComboBox(); self.cb_season.setEditable(True)
        self.cb_season.addItem("")
        for opt in ["Όχι","Χριστουγεννιάτικα","Αποκριάτικα","Πασχαλινά","Καλοκαιρινά"]:
            self.cb_season.addItem(opt)
        self.btn_add_season = QPushButton("ADD")
        season_layout = QHBoxLayout(); season_layout.addWidget(self.cb_season); season_layout.addWidget(self.btn_add_season)

        # — A9: Ποσότητα (ξεκινά κενό)
        self.sb_qty = NoWheelSpinBox(); self.sb_qty.setRange(0,1_000_000)
        self.sb_qty.setSpecialValueText("")
        self.sb_qty.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # — Νέο: Ειδοπ. Χαμηλού Αποθέματος (ξεκινά κενό, επιτρέπεται 0)
        self.sb_low_stock = NoWheelSpinBox(); self.sb_low_stock.setRange(0,1_000_000)
        self.sb_low_stock.setSpecialValueText("")
        self.sb_low_stock.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # — A10: Θέση
        self.cb_position = NoWheelComboBox(); self.cb_position.setEditable(True)
        self.cb_position.addItem("")
        for p in ["ΡΚ","ΡΑ","ΔΚ","ΔΑ","ΕΧ"]:
            self.cb_position.addItem(p)
        self.btn_add_position = QPushButton("ADD")
        pos_layout = QHBoxLayout(); pos_layout.addWidget(self.cb_position); pos_layout.addWidget(self.btn_add_position)

        # — A11: Κατηγορία
        self.cb_category = NoWheelComboBox(); self.cb_category.setEditable(True)
        self.cb_category.addItem(""); self.btn_add_category = QPushButton("ADD")
        cat_layout = QHBoxLayout(); cat_layout.addWidget(self.cb_category); cat_layout.addWidget(self.btn_add_category)

        # — A12: ΦΠΑ
        self.cb_vat = NoWheelComboBox(); self.cb_vat.setEditable(True)
        self.cb_vat.addItem(""); self.cb_vat.addItem("24")
        self.btn_add_vat = QPushButton("ADD")
        vat_layout = QHBoxLayout(); vat_layout.addWidget(self.cb_vat); vat_layout.addWidget(self.btn_add_vat)
        self.lbl_vat_warn = QLabel(); self.lbl_vat_warn.setFont(bold)
        self.lbl_vat_warn.setStyleSheet("color: orange;")

        # — A13: Τιμή Κόστους ΧΩΡΙΣ ΦΠΑ
        lbl_cost_ex = QLabel("Τίμη Κόστους ΧΩΡΙΣ ΦΠΑ"); lbl_cost_ex.setFont(bold)
        self.dsb_cost = NoWheelDoubleSpinBox(); self.dsb_cost.setRange(0,1_000_000)
        self.dsb_cost.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.lbl_cost_vat = QLabel(); self.lbl_cost_vat.setFont(bold)

        # — A14: Τιμή Πώλησης ΜΕ ΦΠΑ
        lbl_price = QLabel("Τιμή Πώλησης ΜΕ ΦΠΑ"); lbl_price.setFont(bold)
        self.dsb_price = NoWheelDoubleSpinBox(); self.dsb_price.setRange(0,1_000_000)
        self.dsb_price.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.dsb_price.setFont(bold)
        self.lbl_price_ex = QLabel(); self.lbl_profit = QLabel(); self.lbl_margin = QLabel()
        self.lbl_margin_warn = QLabel(); self.lbl_margin_warn.setFont(bold)
        self.lbl_margin_warn.setStyleSheet("color: red; font-size:12pt;")
        self.lbl_margin_warn.setAlignment(Qt.AlignCenter)

        # — Switch Ποσό / Ποσοστό για εκπτώσεις
        self.rb_amount  = QRadioButton("Ποσό")
        self.rb_percent = QRadioButton("Ποσοστό")
        self.rb_percent.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.rb_amount); grp.addButton(self.rb_percent)
        sw_layout = QHBoxLayout()
        sw_layout.addWidget(QLabel("Τύπος Έκπτωσης:")); sw_layout.addWidget(self.rb_amount); sw_layout.addWidget(self.rb_percent)

        # — A15: 1η Έκπτωση
        self.dsb_disc1      = NoWheelDoubleSpinBox(); self.dsb_disc1.setRange(0,1_000_000)
        self.dsb_disc1.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.lbl_disc1_title = QLabel("Ποσό Έκπτωσης 1")
        self.lbl_disc1_pct   = QLabel()

        # — A16: 2η Έκπτωση
        self.dsb_disc2      = NoWheelDoubleSpinBox(); self.dsb_disc2.setRange(0,1_000_000)
        self.dsb_disc2.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.lbl_disc2_title = QLabel("Ποσό Έκπτωσης 2")
        self.lbl_disc2_pct   = QLabel()

        # — SUB-SKU
        self.lbl_sub_sku = QLabel(); self.lbl_sub_sku.setAlignment(Qt.AlignCenter)

        # — Buttons
        self.btn_exit   = QPushButton("Έξοδος")
        self.btn_submit = QPushButton("Καταχώρηση")


        # ——— Build form inside scroll area ———
        form = QFormLayout()
        form.addRow("SKU/Barcode Κατασκευαστή:", self.le_sku_man); form.addRow("", self.lbl_sku_man_warn)
        form.addRow("SKU/Barcode Προμηθευτή:", self.le_sku_sup);    form.addRow("", self.lbl_sku_sup_warn)
        form.addRow("Προμηθευτής:", sup_layout)
        form.addRow("Όνομα Προϊόντος:", self.le_name)
        form.addRow("Περιγραφή Προϊόντος:", self.te_desc)
        form.addRow("Μέγεθος:", self.le_size);       form.addRow("", self.cb_no_size)
        form.addRow("Χρώμα:", self.le_color);        form.addRow("", self.cb_no_color)
        form.addRow("SKU Προϊόντος:", self.le_sku);  form.addRow("", self.cb_auto_sku)
        form.addRow("Εποχικό:", season_layout)
        form.addRow("Ποσότητα:", self.sb_qty)
        form.addRow("Ειδοπ. Χαμηλού Απ:", self.sb_low_stock)
        form.addRow("Θέση:", pos_layout)
        form.addRow("Κατηγορία:", cat_layout)
        form.addRow("ΦΠΑ:", vat_layout);             form.addRow("", self.lbl_vat_warn)
        form.addRow(lbl_cost_ex, self.dsb_cost);     form.addRow("Κόστος με ΦΠΑ:", self.lbl_cost_vat)
        form.addRow(lbl_price, self.dsb_price);      form.addRow("Τιμή χωρίς ΦΠΑ:", self.lbl_price_ex)
        form.addRow("Κέρδος:", self.lbl_profit)
        form.addRow("MARGIN:", self.lbl_margin);     form.addRow("", self.lbl_margin_warn)
        form.addRow(sw_layout)
        form.addRow(self.lbl_disc1_title, self.dsb_disc1); form.addRow("", self.lbl_disc1_pct)
        form.addRow(self.lbl_disc2_title, self.dsb_disc2); form.addRow("", self.lbl_disc2_pct)
        form.addRow("", self.lbl_sub_sku)

        btns = QHBoxLayout(); btns.addWidget(self.btn_exit); btns.addStretch(); btns.addWidget(self.btn_submit)

        content = QWidget(); v = QVBoxLayout(content)
        v.addLayout(form); v.addLayout(btns)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(content)

        dlg_layout = QVBoxLayout(self); dlg_layout.addWidget(scroll)
        self.setLayout(dlg_layout)

        # — Connections —
        self.le_sku_man.textChanged.connect(self.check_sku_man)
        self.le_sku_sup.textChanged.connect(self.check_sku_sup)
        self.btn_add_supplier.clicked.connect(self.add_supplier)
        self.cb_no_size.toggled.connect(self.le_size.setDisabled)
        self.cb_no_color.toggled.connect(self.le_color.setDisabled)
        self.cb_auto_sku.toggled.connect(self.update_sku)
        self.le_size.textChanged.connect(self.update_sku)
        self.le_color.textChanged.connect(self.update_sku)
        self.btn_add_season.clicked.connect(self.add_season)
        self.btn_add_position.clicked.connect(self.add_position)
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_add_vat.clicked.connect(self.add_vat)
        self.cb_vat.currentTextChanged.connect(self.on_vat_changed)
        self.dsb_cost.valueChanged.connect(self.recalculate_all)
        self.dsb_price.valueChanged.connect(self.recalculate_all)
        self.dsb_disc1.valueChanged.connect(self.recalculate_all)
        self.dsb_disc2.valueChanged.connect(self.recalculate_all)
        self.rb_amount.toggled.connect(self.recalculate_all)
        self.rb_percent.toggled.connect(self.recalculate_all)
        self.cb_position.currentTextChanged.connect(self.recalculate_all)
        self.btn_exit.clicked.connect(self.on_exit)
        self.btn_submit.clicked.connect(self.submit)

        # Αρχικός υπολογισμός
        self.update_sku()
        self.recalculate_all()

        # Height limits
        self.setMinimumHeight(700)
        self.resize(self.width(), 600)
        rect = QApplication.primaryScreen().availableGeometry()
        self.setMaximumHeight(rect.height() - 50)


    def check_sku_man(self, text):
        exists = self.session.query(Product).filter_by(sku_manufacturer=text).first()
        self.lbl_sku_man_warn.setText("Ο κωδικός υπάρχει ήδη." if exists else "")


    def check_sku_sup(self, text):
        exists = self.session.query(Product).filter_by(sku_supplier=text).first()
        self.lbl_sku_sup_warn.setText("Ο κωδικός υπάρχει ήδη." if exists else "")


    def add_supplier(self):
        t, ok = QInputDialog.getText(self, "Νέος Προμηθευτής", "Όνομα Προμηθευτή:")
        if ok and t:
            self.cb_supplier.addItem(t); self.cb_supplier.setCurrentText(t)


    def add_season(self):
        t, ok = QInputDialog.getText(self, "Νέα Εποχή", "Εποχικό:")
        if ok and t:
            self.cb_season.addItem(t); self.cb_season.setCurrentText(t)


    def add_position(self):
        t, ok = QInputDialog.getText(self, "Νέα Θέση", "Θέση:")
        if ok and t:
            self.cb_position.addItem(t); self.cb_position.setCurrentText(t)


    def add_category(self):
        t, ok = QInputDialog.getText(self, "Νέα Κατηγορία", "Κατηγορία:")
        if ok and t:
            self.cb_category.addItem(t); self.cb_category.setCurrentText(t)


    def add_vat(self):
        t, ok = QInputDialog.getText(self, "Νέο ΦΠΑ", "Ποσοστό ΦΠΑ (π.χ. 24):")
        if ok and t:
            self.cb_vat.addItem(t); self.cb_vat.setCurrentText(t)


    def update_sku(self):
        if not self.cb_auto_sku.isChecked():
            return
        prefix = "CC" + (self.le_size.text()[:2] or "00").ljust(2,"0") + (self.le_color.text()[:2] or "00").ljust(2,"0")
        rem = 13 - len(prefix)
        rows = self.session.query(Product.sku)\
            .filter(Product.sku.like(f"{prefix}%")).all()
        mx = 0
        for (v,) in rows:
            tail = v[len(prefix):]
            if tail.isdigit():
                mx = max(mx,int(tail))
        self.le_sku.setText(prefix + str(mx+1).zfill(rem))


    def on_vat_changed(self, t):
        t = t.strip().rstrip('%')
        if t and not t.isdigit():
            self.lbl_vat_warn.setText("Το ΦΠΑ πρέπει να είναι αριθμός ή ποσοστό")
        else:
            self.lbl_vat_warn.clear()


    def recalculate_all(self):
        # Υπολογισμοί κόστους/margin
        try:
            pct = float(self.cb_vat.currentText().strip('%'))/100
        except:
            pct = 0.0
        c = self.dsb_cost.value()
        self.lbl_cost_vat.setText(f"{c*(1+pct):.2f}")
        price = self.dsb_price.value()
        ex = price/(1+pct) if pct else price
        pr = ex - c
        mg = (pr/price*100) if price else 0
        self.lbl_price_ex.setText(f"{ex:.2f}")
        self.lbl_profit.setText(f"{pr:.2f}")
        self.lbl_margin.setText(f"{mg:.2f}%")
        if c>0 and mg<20:
            self.lbl_margin_warn.setText("Το Margin είναι χαμηλό")
        else:
            self.lbl_margin_warn.clear()

        # Εκπτώσεις
        mode_pct = self.rb_percent.isChecked()
        if mode_pct:
            self.lbl_disc1_title.setText("Ποσό Έκπτωσης 1")
            self.lbl_disc2_title.setText("Ποσό Έκπτωσης 2")
        else:
            self.lbl_disc1_title.setText("Ποσοστό Έκπτωσης 1")
            self.lbl_disc2_title.setText("Ποσοστό Έκπτωσης 2")

        for dsb, lbl in [(self.dsb_disc1,self.lbl_disc1_pct),(self.dsb_disc2,self.lbl_disc2_pct)]:
            val = dsb.value()
            if mode_pct:
                amt = price * val/100
                lbl.setText(f"{amt:.2f}")
            else:
                pct2 = (val/price*100) if price else 0
                lbl.setText(f"{pct2:.2f}%")

        # SUB-SKU
        d1 = str(self.dsb_disc1.value()).replace('.','/')
        d2 = str(self.dsb_disc2.value()).replace('.','/')
        pos = self.cb_position.currentText()
        self.lbl_sub_sku.setText(f"SUB-SKU:{pos}-A{d1}B{d2}Casa-CozyGRC")


    def on_exit(self):
        if (self.cb_supplier.currentText().strip() or
            self.le_name.text().strip() or
            self.te_desc.toPlainText().strip()):
            r = QMessageBox.question(self,"Έξοδος χωρίς αποθήκευση","Έξοδος χωρίς αποθήκευση;",
                                      QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
            if r==QMessageBox.Yes: self.reject()
        else:
            self.reject()


    def closeEvent(self, e):
        if (self.cb_supplier.currentText().strip() or
            self.le_name.text().strip() or
            self.te_desc.toPlainText().strip()):
            r = QMessageBox.question(self,"Έξοδος χωρίς αποθήκευση","Έξοδος χωρίς αποθήκευση;",
                                      QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
            if r==QMessageBox.Yes: e.accept()
            else: e.ignore()
        else:
            e.accept()


    def submit(self):
        # Validation
        if not self.cb_supplier.currentText().strip():
            QMessageBox.warning(self,"Λάθος","Ο Προμηθευτής είναι υποχρεωτικός."); return
        if not self.le_name.text().strip():
            QMessageBox.warning(self,"Λάθος","Το Όνομα Προϊόντος είναι υποχρεωτικό."); return
        if not self.cb_no_size.isChecked() and not self.le_size.text().strip():
            QMessageBox.warning(self,"Λάθος","Το Μέγεθος είναι υποχρεωτικό."); return
        if not self.cb_no_color.isChecked() and not self.le_color.text().strip():
            QMessageBox.warning(self,"Λάθος","Το Χρώμα είναι υποχρεωτικό."); return
        if not self.cb_season.currentText().strip():
            QMessageBox.warning(self,"Λάθος","Το Εποχικό είναι υποχρεωτικό."); return
        if self.sb_qty.value()<=0:
            QMessageBox.warning(self,"Λάθος","Η Ποσότητα είναι υποχρεωτική."); return
        # low-stock: επιτρέπεται 0
        if not self.cb_position.currentText().strip():
            QMessageBox.warning(self,"Λάθος","Η Θέση είναι υποχρεωτική."); return
        if not self.cb_category.currentText().strip():
            QMessageBox.warning(self,"Λάθος","Η Κατηγορία είναι υποχρεωτική."); return
        if not self.cb_vat.currentText().strip():
            QMessageBox.warning(self,"Λάθος","Το ΦΠΑ είναι υποχρεωτικό."); return
        if self.dsb_cost.value()==0:
            QMessageBox.warning(self,"Λάθος","Η Τίμη Κόστους ΧΩΡΙΣ ΦΠΑ είναι υποχρεωτική."); return
        if self.dsb_price.value()==0:
            QMessageBox.warning(self,"Λάθος","Η Τίμη Πώλησης ΜΕ ΦΠΑ είναι υποχρεωτική."); return
        if self.dsb_disc1.value()==0:
            QMessageBox.warning(self,"Λάθος","Η 1η Έκπτωση είναι υποχρεωτική."); return
        if self.dsb_disc2.value()==0:
            QMessageBox.warning(self,"Λάθος","Η 2η Έκπτωση είναι υποχρεωτική."); return

        # Manual SKU duplicate pre-check
        if not self.cb_auto_sku.isChecked():
            if self.session.query(Product).filter_by(sku=self.le_sku.text()).first():
                QMessageBox.warning(self,"Διπλότυπο SKU","Αυτό το SKU υπάρχει ήδη."); return

        # Επιβεβαίωση ΦΠΑ
        txt = self.cb_vat.currentText().strip().rstrip('%')
        if txt and txt!="24":
            r = QMessageBox.question(self,"Επιβεβαίωση ΦΠΑ","Είσαι σίγουρος ότι το ΦΠΑ δεν είναι 24%;",
                                     QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
            if r==QMessageBox.No: return

        # Save
        prod = Product(
            sku_manufacturer=self.le_sku_man.text(),
            sku_supplier=self.le_sku_sup.text(),
            supplier=self.cb_supplier.currentText(),
            name=self.le_name.text(),
            description=self.te_desc.toPlainText(),
            size=None if self.cb_no_size.isChecked() else self.le_size.text(),
            color=None if self.cb_no_color.isChecked() else self.le_color.text(),
            sku=self.le_sku.text(),
            season=self.cb_season.currentText(),
            quantity=self.sb_qty.value(),
            low_stock_notification=self.sb_low_stock.value(),
            position=self.cb_position.currentText(),
            category=self.cb_category.currentText(),
            vat=self.cb_vat.currentText(),
            cost_ex=self.dsb_cost.value(),
            price_inc=self.dsb_price.value(),
            discount1_inc=self.dsb_disc1.value(),
            discount2_inc=self.dsb_disc2.value(),
            format_str=self.lbl_sub_sku.text()
        )
        self.session.add(prod)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            QMessageBox.critical(self,"Σφάλμα Βάσης", str(e.orig))
            return

        QMessageBox.information(self,"Επιτυχία","Το προϊόν καταχωρήθηκε.")
        self.accept()