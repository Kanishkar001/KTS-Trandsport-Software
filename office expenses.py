import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QGridLayout, QMessageBox,
    QLineEdit, QGroupBox, QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class MonthWidget(QGroupBox):
    def __init__(self, month_title, notify_totals_changed, parent=None):
        super().__init__(parent)
        self.notify_totals_changed = notify_totals_changed

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold; color: #003366;
                border: 1.5px solid #336699;
                border-radius: 8px;
                margin-top: 8px;
                padding: 8px;
                background: #fcfcfc;
            }
        """)

        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setSpacing(8)

        header_hbox = QHBoxLayout()

        self.month_edit = QLineEdit()
        self.month_edit.setText(month_title)
        self.month_edit.setFont(QFont("Arial Black", 14))
        self.month_edit.setStyleSheet("color:#003366;")
        self.month_edit.setMaximumWidth(220)
        self.month_edit.textChanged.connect(self.update_groupbox_title)
        header_hbox.addWidget(self.month_edit)

        self.setTitle(self.month_edit.text())

        self.lbl_total = QLabel("Amount: ₹ 0.00")
        self.lbl_total.setFont(QFont("Arial", 12))
        self.lbl_total.setStyleSheet("color:#003366; padding-left: 20px;")
        header_hbox.addWidget(self.lbl_total)

        header_hbox.addStretch()

        self.btn_expand = QPushButton("Expand")
        self.btn_edit = QPushButton("Edit")
        self.btn_save = QPushButton("Save")
        self.btn_delete = QPushButton("Delete")

        for btn in (self.btn_expand, self.btn_edit, self.btn_save, self.btn_delete):
            btn.setStyleSheet("""
                QPushButton {
                    background: #336699;
                    color: white;
                    padding: 4px 10px;
                    border-radius: 6px;
                    min-width: 62px;
                    min-height: 28px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #294d66;
                }
            """)

        header_hbox.addWidget(self.btn_expand)
        header_hbox.addWidget(self.btn_edit)
        header_hbox.addWidget(self.btn_save)
        header_hbox.addWidget(self.btn_delete)

        self.outer_layout.addLayout(header_hbox)

        self.expand_widget = QWidget()
        self.expand_layout = QVBoxLayout(self.expand_widget)
        self.outer_layout.addWidget(self.expand_widget)

        self.fields = {}
        for label_text in ("Office Expenses", "Manager Salary", "Current Bill", "Other Expenses"):
            h_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color:#003366; min-width:140px;")
            edit = QLineEdit("0")
            edit.setFont(QFont("Arial", 12))
            edit.setAlignment(Qt.AlignmentFlag.AlignRight)
            edit.setStyleSheet("""
                QLineEdit {
                    background: white;
                    color: #003366;
                    border: 1px solid #336699;
                    border-radius: 5px;
                    padding: 6px;
                    min-width: 80px;
                }
                QLineEdit:read-only {
                    background: #f0f8ff;
                }
            """)
            edit.textChanged.connect(self.recalc_total)
            h_layout.addWidget(label)
            h_layout.addWidget(edit)
            self.expand_layout.addLayout(h_layout)
            self.fields[label_text] = edit

        self.btn_expand.clicked.connect(self.toggle_expand)
        self.btn_edit.clicked.connect(self.enable_editing)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_delete.clicked.connect(self.confirm_delete)

        self.disable_editing()
        self.collapse()
        self.recalc_total()

    def update_groupbox_title(self, new_text: str):
        self.setTitle(new_text)

    def toggle_expand(self):
        if self.expand_widget.isVisible():
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.expand_widget.setVisible(True)
        self.btn_expand.setText("Collapse")

    def collapse(self):
        self.expand_widget.setVisible(False)
        self.btn_expand.setText("Expand")

    def enable_editing(self):
        self.expand()
        for edit in self.fields.values():
            edit.setReadOnly(False)

    def disable_editing(self):
        for edit in self.fields.values():
            edit.setReadOnly(True)

    def save_changes(self):
        confirmed = self.show_message_box_question("Confirm Save",
                                                  "Are you sure you want to save changes?")
        if confirmed:
            self.disable_editing()
            self.notify_totals_changed()

    def confirm_delete(self):
        confirmed = self.show_message_box_question("Confirm Delete",
                                                  "Do you really want to delete this monthly record?\nThis action cannot be undone.")
        if confirmed:
            self.hide()
            self.setParent(None)
            self.deleteLater()
            self.notify_totals_changed()

    def show_message_box_question(self, title: str, message: str) -> bool:
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setFont(QFont("Arial", 12))
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #003366;
            }
            QPushButton {
                background-color: #336699;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #294d66;
            }
            QLabel {
                color: #003366;
            }
        """)
        result = msg.exec()
        return result == int(QMessageBox.StandardButton.Yes)

    def recalc_total(self):
        total = 0.0
        for edit in self.fields.values():
            text = edit.text().strip()
            if not text:
                continue
            try:
                normalized = text.replace(",", "")
                val = float(normalized)
                total += val
            except Exception:
                pass
        self.lbl_total.setText(f"Amount: ₹ {total:.2f}")
        try:
            self.notify_totals_changed()
        except Exception:
            pass

    def get_totals(self):
        totals = {}
        for key, edit in self.fields.items():
            try:
                text = edit.text().strip()
                if not text:
                    totals[key] = 0.0
                else:
                    totals[key] = float(text.replace(",", ""))
            except Exception:
                totals[key] = 0.0
        return totals


class OfficeExpensePage(QWidget):
    def __init__(self, back_callback=None):
        super().__init__()
        self.back_callback = back_callback

        self.setWindowTitle("Office Expense Page")
        self.resize(1000, 700)
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setStyleSheet("background-color: white;")

        back_btn = QPushButton("← Back to Home")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #336699; color: white;
                font-weight: bold; padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background: #294d66; }
        """)
        back_btn.clicked.connect(self.go_back_home)
        layout.addWidget(back_btn, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        header = QLabel("Office Expense")
        header.setFont(QFont("Arial Black", 30))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("background-color:#336699; color:white; padding:15px; border-radius:15px;")
        layout.addWidget(header, 0, 1, 1, 1)

        left_vbox = QVBoxLayout()
        label_monthly = QLabel("Monthly Records")
        label_monthly.setFont(QFont("Arial", 18))
        label_monthly.setStyleSheet("color:#003366; padding-bottom:10px;")
        left_vbox.addWidget(label_monthly)

        self.btn_add_month = QPushButton("New Month Record")
        self.btn_add_month.setStyleSheet("""
            QPushButton {
                background: #336699; color: white;
                font-weight: bold; padding: 10px; border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover { background: #294d66; }
        """)
        self.btn_add_month.clicked.connect(self.prompt_add_month_record)
        left_vbox.addWidget(self.btn_add_month)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(15)
        self.scroll_area.setWidget(self.scroll_content)
        left_vbox.addWidget(self.scroll_area)

        left_widget = QWidget()
        left_widget.setLayout(left_vbox)

        right_vbox = QVBoxLayout()
        label_summary = QLabel("Office Expenses Summary")
        label_summary.setFont(QFont("Arial", 20))
        label_summary.setStyleSheet("color:#003366; margin-bottom: 10px;")
        right_vbox.addWidget(label_summary)

        self.summary_labels = {}
        summary_items = [
            "Total Current Bill",
            "Manager Salary",
            "Office Rent",
            "Others",
            "Grand Total"
        ]
        for item in summary_items:
            h_layout = QHBoxLayout()
            lbl = QLabel(item)
            lbl.setFont(QFont("Arial", 14))
            lbl.setStyleSheet("color:#222222;")
            val = QLabel("₹ 0.00")
            val.setFont(QFont("Arial", 14))
            val.setStyleSheet("background:#d0e4f7; border:1px solid #336699; border-radius:6px; padding:4px; color:#003366;")
            h_layout.addWidget(lbl)
            h_layout.addWidget(val)
            right_vbox.addLayout(h_layout)
            self.summary_labels[item] = val

        label_business_summary = QLabel("Business Summary")
        label_business_summary.setFont(QFont("Arial", 20))
        label_business_summary.setStyleSheet("color:#003366; margin: 20px 0 10px 0;")
        right_vbox.addWidget(label_business_summary)

        self.business_summary_labels = {}
        business_items = [
            "Trip Expenses",
            "Office Expenses",
            "Vehicle Expenses",
            "Trip Profits",
            "Grand Total"
        ]
        for item in business_items:
            h_layout = QHBoxLayout()
            lbl = QLabel(item)
            lbl.setFont(QFont("Arial", 14))
            lbl.setStyleSheet("color:#222222;")
            val = QLabel("₹ 0.00")
            val.setFont(QFont("Arial", 14))
            val.setStyleSheet("background:#f4e6e6; border:1px solid #993333; border-radius:6px; padding:4px; color:#660000;")
            h_layout.addWidget(lbl)
            h_layout.addWidget(val)
            right_vbox.addLayout(h_layout)
            self.business_summary_labels[item] = val

        refresh_btn = QPushButton("Refresh Totals")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background:#336699; color:white;
                padding: 10px; border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background:#294d66; }
        """)
        refresh_btn.clicked.connect(self.refresh_totals)
        right_vbox.addWidget(refresh_btn)
        right_vbox.addStretch(10)

        right_widget = QWidget()
        right_widget.setLayout(right_vbox)

        layout.addWidget(left_widget, 1, 0)
        layout.addWidget(right_widget, 1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.month_widgets = []

        for i in range(3):
            month_name = f"Month {i+1} - 2025"
            self.add_month_record(month_name)

    def prompt_add_month_record(self):
        text, ok = QInputDialog.getText(self, "New Month Record", "Enter name for new month record:")
        if ok and text.strip():
            self.add_month_record(text.strip())

    def add_month_record(self, month_name=None):
        if month_name is None:
            month_name = f"Month {len(self.month_widgets) + 1} - 2025"
        month_widget = MonthWidget(month_name, self.refresh_totals)
        month_widget.collapse()
        self.scroll_layout.insertWidget(0, month_widget)
        self.month_widgets.insert(0, month_widget)
        self.refresh_totals()

    def refresh_totals(self):
        self.month_widgets = [w for w in self.month_widgets if w.parent() is not None]

        total_current_bill = 0.0
        total_manager_salary = 0.0
        total_office_rent = 0.0
        total_others = 0.0

        # Business summary fields - only Office Expenses will sum all monthly fields!
        total_office_expenses = 0.0

        for widget in self.month_widgets:
            if widget.isVisible():
                totals = widget.get_totals()
                total_current_bill += totals.get("Current Bill", 0.0)
                total_manager_salary += totals.get("Manager Salary", 0.0)
                total_office_rent += totals.get("Office Expenses", 0.0)
                total_others += totals.get("Other Expenses", 0.0)

                # Office Expenses in Business Summary is the sum of all monthly fields below
                total_office_expenses += (
                    totals.get("Office Expenses", 0.0)
                    + totals.get("Manager Salary", 0.0)
                    + totals.get("Current Bill", 0.0)
                    + totals.get("Other Expenses", 0.0)
                )
                # Other fields in business summary should NOT be affected by monthly records!

        grand_total = total_current_bill + total_manager_salary + total_office_rent + total_others
        self.summary_labels["Total Current Bill"].setText(f"₹ {total_current_bill:.2f}")
        self.summary_labels["Manager Salary"].setText(f"₹ {total_manager_salary:.2f}")
        self.summary_labels["Office Rent"].setText(f"₹ {total_office_rent:.2f}")
        self.summary_labels["Others"].setText(f"₹ {total_others:.2f}")
        self.summary_labels["Grand Total"].setText(f"₹ {grand_total:.2f}")

        # Now, in Business Summary: only "Office Expenses" changes, rest remain zero or use other logic
        self.business_summary_labels["Trip Expenses"].setText(f"₹ {0.00:.2f}")
        self.business_summary_labels["Office Expenses"].setText(f"₹ {total_office_expenses:.2f}")
        self.business_summary_labels["Vehicle Expenses"].setText(f"₹ {0.00:.2f}")
        self.business_summary_labels["Trip Profits"].setText(f"₹ {0.00:.2f}")
        # Grand Total = Office Expenses only, unless other logic required
        self.business_summary_labels["Grand Total"].setText(f"₹ {total_office_expenses:.2f}")

    def go_back_home(self):
        if self.back_callback:
            self.back_callback()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Back to Home")
            msg.setText("Back button pressed. Implement actual home navigation here.")
            msg.setFont(QFont("Arial", 12))
            msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    def on_back_button():
        print("Back button pressed - implement home page navigation here")

    window = OfficeExpensePage(back_callback=on_back_button)
    window.show()
    sys.exit(app.exec())
