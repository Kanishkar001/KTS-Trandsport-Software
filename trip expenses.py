from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QDialog, QGridLayout, QMessageBox, QHeaderView,
    QComboBox, QFrame, QAbstractItemView, QMainWindow, QFileDialog, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
import os
import platform
import subprocess

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import pandas as pd

NAVY = "#2c3e50"
NAVY_DARK = "#34495e"
WHITE = "#ffffff"
LIGHT_GRAY = "#f7f7f7"
SELECT_ROW_COLOR = "#dcdcdc"


def safe_float(value, default=0.0):
    try:
        return float(str(value).strip() or "0")
    except Exception:
        return default


def show_int_amount(value):
    try:
        f = safe_float(value)
        return str(int(round(f))) if f else "0"
    except Exception:
        return "0"


class DateRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Custom Date Range")
        layout = QGridLayout(self)

        label_from = QLabel("From:")
        label_to = QLabel("To:")
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        layout.addWidget(label_from, 0, 0)
        layout.addWidget(self.date_from, 0, 1)
        layout.addWidget(label_to, 1, 0)
        layout.addWidget(self.date_to, 1, 1)
        layout.addWidget(btn_ok, 2, 0)
        layout.addWidget(btn_cancel, 2, 1)

    def get_range(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        if d_from > d_to:
            d_from, d_to = d_to, d_from
        return (d_from, d_to)


class TripManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trip Manager")
        self.setGeometry(100, 100, 1280, 780)
        self.rows = []
        self.custom_range = (None, None)
        self.expand_dialog = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"background-color: {NAVY}; color: white;")
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_top_bar()
        self.create_table()
        self.create_summary_box()

    def create_top_bar(self):
        top_bar = QHBoxLayout()

        self.button_back = QPushButton("Back to Home")
        self.button_back.setStyleSheet(f"background: #e67e22; color: white; font-weight: bold; font-size: 14px;")
        self.button_back.clicked.connect(self.back_to_home)
        top_bar.addWidget(self.button_back)

        self.button_new = QPushButton("NEW")
        self.button_new.setStyleSheet(f"background: #27ae60; color: white; font-weight: bold; font-size: 14px;")
        self.button_new.clicked.connect(self.add_row)
        top_bar.addWidget(self.button_new)

        self.button_download_pdf = QPushButton("DOWNLOAD PDF")
        self.button_download_pdf.setStyleSheet(f"background: #2980b9; color: white; font-weight: bold; font-size: 14px;")
        self.button_download_pdf.clicked.connect(self.download_pdf)
        top_bar.addWidget(self.button_download_pdf)

        self.button_download_excel = QPushButton("DOWNLOAD EXCEL")
        self.button_download_excel.setStyleSheet(f"background: #8e44ad; color: white; font-weight: bold; font-size: 14px;")
        self.button_download_excel.clicked.connect(self.download_excel)
        top_bar.addWidget(self.button_download_excel)

        self.date_option = QComboBox()
        self.date_option.addItems(
            ["Filter", "Last 1 Day", "Last Month", "Last 3 Months",
             "Last 6 Months", "Last Year", "Custom..."]
        )
        self.date_option.setStyleSheet("background-color: white; color: black; font-weight: normal; font-size: 13px;")
        self.date_option.currentTextChanged.connect(self.set_date_option)
        top_bar.addWidget(self.date_option)

        label_vehicle = QLabel("Vehicle")
        label_vehicle.setStyleSheet(f"color: white; font-weight: bold; font-size: 14px; margin-left: 8px;")
        top_bar.addWidget(label_vehicle)

        self.vehicle_var = QLineEdit()
        self.vehicle_var.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        top_bar.addWidget(self.vehicle_var)

        label_broker = QLabel("Broker Office")
        label_broker.setStyleSheet(f"color: white; font-weight: bold; font-size: 14px; margin-left: 8px;")
        top_bar.addWidget(label_broker)

        self.brokeroffice_var = QLineEdit()
        self.brokeroffice_var.setPlaceholderText("Search Broker Office")
        self.brokeroffice_var.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        top_bar.addWidget(self.brokeroffice_var)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Paid", "Unpaid"])
        self.status_filter.setStyleSheet("background-color: white; color: black; font-weight: normal; font-size: 13px; margin-left: 8px;")
        self.status_filter.currentTextChanged.connect(self.search)
        top_bar.addWidget(self.status_filter)

        self.button_search = QPushButton("SEARCH")
        self.button_search.setStyleSheet("background: #c0392b; color: white; font-weight: bold; font-size: 14px;")
        self.button_search.clicked.connect(self.search)
        top_bar.addWidget(self.button_search)

        self.button_reset = QPushButton("RESET")
        self.button_reset.setStyleSheet("background: #7f8c8d; color: white; font-weight: bold; font-size: 14px;")
        self.button_reset.clicked.connect(self.reset)
        top_bar.addWidget(self.button_reset)

        top_frame = QFrame()
        top_frame.setStyleSheet(f"background: {NAVY_DARK}; color: white;")
        top_frame.setLayout(top_bar)
        self.main_layout.addWidget(top_frame)

    def back_to_home(self):
        QMessageBox.information(self, "Back to Home", "This would navigate back to the home screen.")

    def create_table(self):
        headers = [
            "Date", "Vehicle No", "Location From - To",
            "Broker Office",
            "Driver Amount", "Profit", "Expense", "Total",
            "Status",
            "Expand", "Delete"
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            f"QTableWidget {{background-color: {WHITE}; color: black; font-size: 14px;}}"
            f"QHeaderView::section {{background-color: {NAVY}; color: white; font-weight: bold;}}"
            f"QTableWidget::item:selected {{background-color: {SELECT_ROW_COLOR}; color: black;}}"
            f"QTableWidget::item:alternate {{background-color: {LIGHT_GRAY};}}"
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.main_layout.addWidget(self.table)

    def create_summary_box(self):
        summary_layout = QHBoxLayout()
        self.total_driver_amount_var = QLabel("0")
        self.total_profit_var = QLabel("0")
        self.total_expense_var = QLabel("0")
        self.total_sum_var = QLabel("0")
        self.total_unpaid_var = QLabel("0")

        def mk_label(text, label):
            lab = QLabel(text)
            lab.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            label.setStyleSheet("background-color: white; color: black; padding: 5px 12px; font-size: 14px; min-width: 100px;")
            summary_layout.addWidget(lab)
            summary_layout.addWidget(label)

        mk_label("Total Driver Amount:", self.total_driver_amount_var)
        mk_label("Total Profit:", self.total_profit_var)
        mk_label("Total Expense:", self.total_expense_var)
        mk_label("Total:", self.total_sum_var)
        mk_label("Total Unpaid:", self.total_unpaid_var)

        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"background: {NAVY_DARK};")
        summary_frame.setLayout(summary_layout)
        self.main_layout.addWidget(summary_frame)

    def _row_of_button(self, button, col):
        for r in range(self.table.rowCount()):
            try:
                if self.table.cellWidget(r, col) is button:
                    return r
            except Exception:
                continue
        return -1

    def set_alignment(self, item, align):
        if item is not None:
            item.setTextAlignment(align)

    def add_row(self):
        current_date_str = datetime.today().strftime("%Y-%m-%d")
        self.table.insertRow(0)
        font = QFont()
        font.setPointSize(14)
        cols = self.table.columnCount()
        for col in range(cols):
            if col in [9, 10]:
                continue
            item = QTableWidgetItem()
            item.setFont(font)
            if col == 0:
                item.setText(current_date_str)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.set_alignment(item, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            elif col == 3:
                item.setText("")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.set_alignment(item, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            elif col in [4, 5, 6, 7]:
                item.setText("0")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.set_alignment(item, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            elif col == 8:
                item.setText("Unpaid")
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.set_alignment(item, Qt.AlignmentFlag.AlignCenter)
            else:
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.set_alignment(item, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, col, item)
        self.table.setRowHeight(0, 42)
        expand_btn = QPushButton("Expand")
        expand_btn.setFont(font)
        expand_btn.setToolTip("Expand/Edit trip details")
        expand_btn.clicked.connect(self.expand_clicked)
        delete_btn = QPushButton("X")
        delete_btn.setFont(font)
        delete_btn.setStyleSheet("color: red;")
        delete_btn.setToolTip("Delete this row")
        delete_btn.clicked.connect(self.delete_clicked)
        self.table.setCellWidget(0, 9, expand_btn)
        self.table.setCellWidget(0, 10, delete_btn)

        entries = [self.table.item(0, c) for c in range(cols)]
        detail_entries = {}
        self.rows.insert(0, {
            "entries": entries,
            "detail_entries": detail_entries,
            "expand_btn": expand_btn,
            "delete_btn": delete_btn,
        })
        if self.rows[0]["entries"][8]:
            self.rows[0]["entries"][8].setText("Unpaid")
        self.update_summary()

    def expand_clicked(self):
        btn = self.sender()
        row_idx = self._row_of_button(btn, 9)
        if row_idx >= 0:
            self.toggle_expand(row_idx)

    def delete_clicked(self):
        btn = self.sender()
        row_idx = self._row_of_button(btn, 10)
        if row_idx >= 0:
            self.delete_row(row_idx)

    def toggle_expand(self, row_idx):
        if self.expand_dialog:
            QMessageBox.information(
                self, "Already Open", "Please close the open detail window first."
            )
            return
        if row_idx < 0 or row_idx >= len(self.rows):
            return
        row = self.rows[row_idx]
        popup = QDialog(self)
        self.expand_dialog = popup
        popup.setWindowTitle("Trip Details")
        popup.setStyleSheet("background-color: white; color: black;")
        popup.setMinimumSize(520, 720)
        layout = QGridLayout(popup)
        fields = [
            "Driver Name", "Start KM", "End KM", "KM Travelled", "Total Trip Amount",
            "Trip Advance", "Return Balance", "Pooja", "Diesel", "R.T.O & P.C", "Toll",
            "Driver Amount", "Driver Advance", "Driver Balance", "Cleaner Amount",
            "Broker Amount", "Load Amount", "Unload Amount", "Others",
        ]
        entries = {}

        def get_float(field):
            if field not in entries:
                return 0.0
            return safe_float(entries[field].text())

        def calculate_km():
            start = get_float("Start KM")
            end = get_float("End KM")
            travelled = max(0, end - start)
            if "KM Travelled" in entries:
                entries["KM Travelled"].setText(show_int_amount(travelled))

        def calculate_driver_balance():
            subtract_fields = [
                "Pooja", "R.T.O & P.C", "Load Amount", "Unload Amount", "Others", "Cleaner Amount",
            ]
            subtract_total = sum(get_float(f) for f in subtract_fields)
            driver_amount = get_float("Driver Amount")
            driver_advance = get_float("Driver Advance")
            driver_balance = (driver_amount - driver_advance) + subtract_total
            if "Driver Balance" in entries:
                entries["Driver Balance"].setText(show_int_amount(driver_balance))
            try:
                if row["entries"][4]:
                    row["entries"][4].setText(show_int_amount(driver_amount))
            except Exception:
                pass

        for i, field in enumerate(fields):
            label = QLabel(field + ":")
            label.setStyleSheet("color: black; font-weight: bold;")
            entry = QLineEdit()
            entry.setStyleSheet(
                "background-color: white; color: black; padding: 5px; border: 1px solid #ccc;"
            )
            entry.setText(row["detail_entries"].get(field, ""))
            if field in ("Driver Balance", "KM Travelled"):
                entry.setReadOnly(True)
            entries[field] = entry
            layout.addWidget(label, i, 0)
            layout.addWidget(entry, i, 1)

        def update_driver_amount_from_total():
            try:
                total = safe_float(entries["Total Trip Amount"].text())
                driver_amt = total * 0.11
                entries["Driver Amount"].setText(show_int_amount(driver_amt))
            except Exception:
                entries["Driver Amount"].setText("0")
            calculate_driver_balance()

        if "Total Trip Amount" in entries:
            entries["Total Trip Amount"].textChanged.connect(update_driver_amount_from_total)
        if "Start KM" in entries:
            entries["Start KM"].textChanged.connect(calculate_km)
        if "End KM" in entries:
            entries["End KM"].textChanged.connect(calculate_km)

        calc_fields = [
            "Driver Amount", "Driver Advance", "Pooja", "R.T.O & P.C", "Load Amount",
            "Unload Amount", "Others", "Cleaner Amount",
        ]
        for f in calc_fields:
            if f in entries:
                entries[f].textChanged.connect(calculate_driver_balance)

        calculate_km()
        calculate_driver_balance()
        update_driver_amount_from_total()

        def save_close():
            for f in fields:
                row["detail_entries"][f] = entries[f].text()
            total_val = safe_float(entries["Total Trip Amount"].text())
            try:
                if row["entries"][7]:
                    row["entries"][7].setText(show_int_amount(total_val))
            except Exception:
                pass

            expense_fields = [
                "Pooja", "Diesel", "R.T.O & P.C", "Toll", "Driver Amount",
                "Cleaner Amount", "Broker Amount", "Load Amount", "Unload Amount", "Others",
            ]
            expense_sum = 0.0
            for f in expense_fields:
                expense_sum += safe_float(row["detail_entries"].get(f, "0"))
            try:
                if row["entries"][6]:
                    row["entries"][6].setText(show_int_amount(expense_sum))
            except Exception:
                pass

            profit_val = total_val - expense_sum
            try:
                if row["entries"][5]:
                    row["entries"][5].setText(show_int_amount(profit_val))
            except Exception:
                pass

            self.update_summary()
            try:
                idx = self.rows.index(row)
                self.update_status_for_row(idx)
            except ValueError:
                pass

            popup.accept()
            self.expand_dialog = None

        btn_save = QPushButton("Save")
        btn_save.setStyleSheet(
            """
            QPushButton {
                background: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #219a52;
            }
            """
        )
        btn_save.clicked.connect(save_close)
        layout.addWidget(btn_save, len(fields) + 1, 0, 1, 2)
        popup.exec()
        self.expand_dialog = None

    def update_summary(self):
        total_profit = 0.0
        total_expense = 0.0
        total_sum = 0.0
        total_driver_amount = 0.0
        total_unpaid = 0.0
        for i in range(len(self.rows)):
            if i < self.table.rowCount() and self.table.isRowHidden(i):
                continue
            row = self.rows[i]
            try:
                total_profit += safe_float(row["entries"][5].text() if row["entries"][5] else 0)
            except Exception:
                pass
            try:
                total_expense += safe_float(row["entries"][6].text() if row["entries"][6] else 0)
            except Exception:
                pass
            try:
                total_sum += safe_float(row["entries"][7].text() if row["entries"][7] else 0)
            except Exception:
                pass
            try:
                total_driver_amount += safe_float(row["entries"][4].text() if row["entries"][4] else 0)
            except Exception:
                pass
            try:
                status = (row["entries"][8].text() if row["entries"][8] else "").strip().lower()
                if status == "unpaid":
                    total_trip = safe_float(row["entries"][7].text() if row["entries"][7] else 0)
                    trip_advance = safe_float(row["detail_entries"].get("Trip Advance", "0"))
                    broker_amount = safe_float(row["detail_entries"].get("Broker Amount", "0"))
                    unpaid = max(0, (total_trip - trip_advance) - broker_amount)
                    total_unpaid += unpaid
            except Exception:
                pass
        self.total_profit_var.setText(show_int_amount(total_profit))
        self.total_expense_var.setText(show_int_amount(total_expense))
        self.total_sum_var.setText(show_int_amount(total_sum))
        self.total_driver_amount_var.setText(show_int_amount(total_driver_amount))
        self.total_unpaid_var.setText(show_int_amount(total_unpaid))
        self._total_unpaid_cached = total_unpaid

    def update_status_for_row(self, row_idx):
        try:
            if row_idx < 0 or row_idx >= len(self.rows):
                return
            row = self.rows[row_idx]
            total_trip = safe_float(row["entries"][7].text() if row["entries"][7] else 0)
            trip_advance = safe_float(row["detail_entries"].get("Trip Advance", "0"))
            return_balance = safe_float(row["detail_entries"].get("Return Balance", "0"))
            broker_amount = safe_float(row["detail_entries"].get("Broker Amount", "0"))
            if total_trip <= (trip_advance + return_balance + broker_amount):
                status = "Paid"
            else:
                status = "Unpaid"
            if row["entries"][8]:
                row["entries"][8].setText(status)
        except Exception:
            pass

    def delete_row(self, row_idx):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this row?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if 0 <= row_idx < self.table.rowCount():
                self.table.removeRow(row_idx)
            if 0 <= row_idx < len(self.rows):
                del self.rows[row_idx]
            self.update_summary()

    def reset(self):
        self.vehicle_var.setText("")
        self.brokeroffice_var.setText("")
        self.status_filter.setCurrentText("All")
        self.date_option.setCurrentText("Filter")
        self.custom_range = (None, None)
        for i in range(self.table.rowCount()):
            self.table.setRowHidden(i, False)
        self.update_summary()

    def search(self):
        vehicle_filter = self.vehicle_var.text().strip().lower()
        broker_filter = self.brokeroffice_var.text().strip().lower()
        status_filter = self.status_filter.currentText().lower()
        option = self.date_option.currentText()

        today = datetime.today().date()
        start_date = end_date = None

        if option == "Last 1 Day":
            start_date = today - timedelta(days=1)
            end_date = today
        elif option == "Last Month":
            start_date = today - timedelta(days=30)
            end_date = today
        elif option == "Last 3 Months":
            start_date = today - timedelta(days=91)
            end_date = today
        elif option == "Last 6 Months":
            start_date = today - timedelta(days=183)
            end_date = today
        elif option == "Last Year":
            start_date = today - timedelta(days=365)
            end_date = today
        elif option == "Custom..." and all(self.custom_range):
            start_date, end_date = self.custom_range

        any_visible = False
        for i in range(min(self.table.rowCount(), len(self.rows))):
            try:
                date_str = (self.rows[i]["entries"][0].text() if self.rows[i]["entries"][0] else "")
                row_date = None
                if date_str:
                    try:
                        row_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except Exception:
                        row_date = None
            except Exception:
                row_date = None
            try:
                vehicle = (self.rows[i]["entries"][1].text().strip().lower() if self.rows[i]["entries"][1] else "")
            except:
                vehicle = ""
            try:
                broker = (self.rows[i]["entries"][3].text().strip().lower() if self.rows[i]["entries"][3] else "")
            except:
                broker = ""
            try:
                status = (self.rows[i]["entries"][8].text().strip().lower() if self.rows[i]["entries"][8] else "")
            except:
                status = ""

            visible = True
            if start_date and end_date and row_date:
                visible = start_date <= row_date <= end_date
            if vehicle_filter and vehicle_filter not in vehicle:
                visible = False
            if broker_filter and broker_filter not in broker:
                visible = False
            if status_filter != "all" and status_filter != status:
                visible = False

            self.table.setRowHidden(i, not visible)
            if visible:
                any_visible = True

        self.update_summary()
        if not any_visible:
            QMessageBox.information(self, "No Match", "No records found matching your criteria.")

    def set_date_option(self, option):
        if option == "Custom...":
            dialog = DateRangeDialog(self)
            if dialog.exec():
                self.custom_range = dialog.get_range()
                self.search()
            else:
                self.custom_range = (None, None)
                self.date_option.setCurrentText("Filter")
        else:
            self.custom_range = (None, None)
            if option != "Filter":
                self.search()

    def download_pdf(self):
        visible_rows = [row for i, row in enumerate(self.rows) if i < self.table.rowCount() and not self.table.isRowHidden(i)]
        if not visible_rows:
            QMessageBox.information(self, "No Data", "No visible rows to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        self._generate_pdf(path, visible_rows)
        QMessageBox.information(self, "PDF Saved", f"PDF saved to:\n{path}")
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Open file failed", str(e))

    def _generate_pdf(self, path, rows):
        pdf_columns = [
            "Date", "Vehicle No", "Location From - To", "Broker Office",
            "D.Amount", "Profit", "Expense", "Total", "Unpaid"
        ]

        data = [pdf_columns]
        for row in rows:
            row_data = [
                (row["entries"][0].text() if row["entries"][0] else ""),
                (row["entries"][1].text() if row["entries"][1] else ""),
                (row["entries"][2].text() if row["entries"][2] else ""),
                (row["entries"][3].text() if row["entries"][3] else ""),
                show_int_amount(row["entries"][4].text() if row["entries"][4] else ""),
                show_int_amount(row["entries"][5].text() if row["entries"][5] else ""),
                show_int_amount(row["entries"][6].text() if row["entries"][6] else ""),
                show_int_amount(row["entries"][7].text() if row["entries"][7] else "")
            ]
            try:
                total_trip = safe_float(row["entries"][7].text() if row["entries"][7] else 0)
                trip_advance = safe_float(row["detail_entries"].get("Trip Advance", "0"))
                broker_amount = safe_float(row["detail_entries"].get("Broker Amount", "0"))
                unpaid = max(0, (total_trip - trip_advance) - broker_amount)
            except:
                unpaid = 0.0
            row_data.append(show_int_amount(unpaid))
            data.append(row_data)

        data.append([
            "TOTAL", "", "", "", show_int_amount(self.total_driver_amount_var.text()),
            show_int_amount(self.total_profit_var.text()), show_int_amount(self.total_expense_var.text()),
            show_int_amount(self.total_sum_var.text()), show_int_amount(self.total_unpaid_var.text())
        ])

        c = canvas.Canvas(path, pagesize=landscape(letter))
        width, height = landscape(letter)
        margin = 24
        available_width = width - 2 * margin

        # Adjust column proportions to fit landscape better
        col_prop = [0.13, 0.13, 0.18, 0.13, 0.09, 0.09, 0.09, 0.09, 0.07]
        col_widths = [available_width * p for p in col_prop]

        t = Table(data, colWidths=col_widths, repeatRows=1)
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),  # Smaller font for better fit
            ("ALIGN", (4, 1), (7, -2), "RIGHT"),
            ("ALIGN", (8, 1), (8, -2), "RIGHT"),
            ("ALIGN", (0, 1), (3, -2), "LEFT"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f5b7b1")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ])
        t.setStyle(style)

        tw, th = t.wrap(available_width, height)
        t.drawOn(c, margin, height - th - 24)
        c.save()

    def download_excel(self):
        visible_rows = [row for i, row in enumerate(self.rows) if i < self.table.rowCount() and not self.table.isRowHidden(i)]
        if not visible_rows:
            QMessageBox.information(self, "No Data", "No visible rows to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"

        data = []
        for row in visible_rows:
            row_data = []
            for c, e in enumerate(row["entries"][:9]):
                if c in [4, 5, 6, 7]:
                    row_data.append(show_int_amount(e.text() if e else "0"))
                else:
                    row_data.append(e.text() if e else "")
            status = (row_data[8].strip().lower() if len(row_data) > 8 else "")
            try:
                total_trip = safe_float(row["entries"][7].text() if row["entries"][7] else 0)
                trip_advance = safe_float(row["detail_entries"].get("Trip Advance", "0"))
                broker_amount = safe_float(row["detail_entries"].get("Broker Amount", "0"))
                unpaid = 0 if status == "paid" else max(0, (total_trip - trip_advance) - broker_amount)
            except:
                unpaid = 0
            row_data.append(unpaid)
            data.append(row_data)

        columns = ["Date", "Vehicle No", "Location From - To", "Broker Office", "Driver Amount", "Profit", "Expense", "Total", "Status", "Unpaid Amount"]
        df = pd.DataFrame(data, columns=columns)

        total_driver_amount = safe_float(self.total_driver_amount_var.text())
        total_profit = safe_float(self.total_profit_var.text())
        total_expense = safe_float(self.total_expense_var.text())
        total_total = safe_float(self.total_sum_var.text())
        total_unpaid = safe_float(self.total_unpaid_var.text())

        total_row = ["TOTAL", "", "", "", total_driver_amount, total_profit, total_expense, total_total, "", total_unpaid]
        df = pd.concat([df, pd.DataFrame([total_row], columns=columns)], ignore_index=True)

        df.to_excel(path, index=False)

        QMessageBox.information(self, "Excel Saved", f"Excel saved to:\n{path}")
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Open file failed", str(e))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = TripManager()
    win.show()
    sys.exit(app.exec())
