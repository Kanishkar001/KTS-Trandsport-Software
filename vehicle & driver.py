from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QGridLayout, QLineEdit, QDialog, QMessageBox,
    QFormLayout, QDateEdit, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QImageReader
import sys
import os

class VehicleDialog(QDialog):
    def __init__(self, parent=None, vehicle_name=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Vehicle Details" if vehicle_name else "Add New Vehicle")
        self.setMinimumSize(420, 180)
        self.vehicle_name = vehicle_name
        layout = QVBoxLayout(self)

        label = QLabel(f"Editing: {vehicle_name}" if vehicle_name else "Add New Vehicle")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        self.name_edit = QLineEdit(self)
        self.name_edit.setText(vehicle_name)
        self.name_edit.setPlaceholderText("Enter vehicle name")
        self.name_edit.setMinimumHeight(30)
        layout.addWidget(self.name_edit)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f4f8;
                color: #003366;
            }
            QPushButton {
                min-width: 80px;
                min-height: 30px;
                background-color: #007bff;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: #003366;
                padding: 5px;
                font-size: 16px;
            }
        """)

    def get_name(self):
        return self.name_edit.text().strip()

class VehicleWidget(QWidget):
    def __init__(self, name, on_edit, on_remove, on_details):
        super().__init__()
        self.name = name
        self.on_edit = on_edit
        self.on_remove = on_remove
        self.on_details = on_details

        self.details_data = {
            'vehicle_no': name,
            'registration_date': '',
            'fitness_upto': '',
            'tax_upto': '',
            'insurance_upto': '',
            'pucc_upto': '',
            'permit_upto': '',
            'national_permit_upto': '',
            'driver_name': '',
            'driver_contact': '',
            'driver_alt_contact': '',
            'driver_experience': '',
            'driver_adhar': '',
            'driver_license_path': '',
            'loan_total': '',
            'loan_paid': '',
            'loan_remaining': '',
            # Newly added fields
            'driver_date_of_joining': '',
            'driver_bank_account': ''
        }

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #e9f0fb;
                border-radius: 10px;
                padding: 12px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                font-size: 14px;
                padding: 6px 12px;
                border-radius: 6px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLabel#titleLabel {
                color: #003366;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#summaryLabel {
                color: #30475e;
                font-size: 11px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self.label = QLabel(self.name, self)
        self.label.setObjectName("titleLabel")
        layout.addWidget(self.label)

        self.details_summary = QLabel("(no details)", self)
        self.details_summary.setObjectName("summaryLabel")
        layout.addWidget(self.details_summary)

        btn_layout = QHBoxLayout()
        details_btn = QPushButton("Details", self)
        details_btn.clicked.connect(self.details_clicked)
        btn_layout.addWidget(details_btn)

        edit_btn = QPushButton("Edit", self)
        edit_btn.clicked.connect(self.edit_clicked)
        btn_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Remove", self)
        remove_btn.clicked.connect(self.remove_clicked)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setMinimumWidth(300)
        self.setMaximumWidth(380)

    def edit_clicked(self):
        self.on_edit(self)

    def remove_clicked(self):
        self.on_remove(self)

    def details_clicked(self):
        self.on_details(self)

    def update_name(self, new_name):
        self.name = new_name
        self.label.setText(new_name)
        self.details_data['vehicle_no'] = new_name

    def update_details_summary(self):
        d = self.details_data
        parts = []
        if d.get('registration_date'):
            parts.append(f"Reg: {d['registration_date']}")
        if d.get('fitness_upto'):
            parts.append(f"Fitness: {d['fitness_upto']}")
        if d.get('tax_upto'):
            parts.append(f"Tax: {d['tax_upto']}")
        if parts:
            self.details_summary.setText(" | ".join(parts))
        else:
            self.details_summary.setText("(no details)")

class VehicleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driver & Vehicle Management")
        self.setMinimumSize(900, 640)
        self.vehicles = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        add_btn = QPushButton("+ New Vehicle", self)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 8px 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        add_btn.clicked.connect(self.add_vehicle)
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(18)
        self.grid_layout.setContentsMargins(12, 12, 12, 12)
        self.scroll_area.setWidget(self.container)

        # Example vehicles for demonstration
        for i in range(3):
            self.create_vehicle(f"Vehicle {i+1}")

    def create_vehicle(self, name):
        vehicle_widget = VehicleWidget(name, self.edit_vehicle, self.remove_vehicle, self.show_vehicle_details)
        self.vehicles.append(vehicle_widget)
        vehicle_widget.update_details_summary()
        self.refresh_grid()

    def refresh_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)
        for idx, vehicle in enumerate(self.vehicles):
            row = idx // 2
            col = idx % 2
            self.grid_layout.addWidget(vehicle, row, col)
        self.grid_layout.setRowStretch((len(self.vehicles) + 1) // 2, 1)

    def add_vehicle(self):
        dlg = VehicleDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_name()
            if name:
                self.create_vehicle(name)
            else:
                QMessageBox.warning(self, "Warning", "Vehicle name cannot be empty.")

    def edit_vehicle(self, vehicle_widget):
        dlg = VehicleDialog(self, vehicle_widget.name)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_name = dlg.get_name()
            if new_name:
                vehicle_widget.update_name(new_name)
            else:
                QMessageBox.warning(self, "Warning", "Vehicle name cannot be empty.")

    def remove_vehicle(self, vehicle_widget):
        confirm = QMessageBox.question(
            self, "Confirm Remove", f"Remove {vehicle_widget.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.vehicles.remove(vehicle_widget)
            self.refresh_grid()

    def show_vehicle_details(self, vehicle_widget):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Vehicle Details - {vehicle_widget.name}")
        dlg.setMinimumSize(620, 780)
        layout = QVBoxLayout(dlg)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        def make_dateedit_from_str(date_str):
            d = QDate.currentDate()
            if date_str:
                qd = QDate.fromString(date_str, "yyyy-MM-dd")
                if qd.isValid():
                    d = qd
            de = QDateEdit()
            de.setCalendarPopup(True)
            de.setDate(d)
            return de

        vehicle_no_edit = QLineEdit()
        vehicle_no_edit.setText(vehicle_widget.details_data.get('vehicle_no', vehicle_widget.name))
        form.addRow("Vehicle No:", vehicle_no_edit)

        reg_de = make_dateedit_from_str(vehicle_widget.details_data.get('registration_date', ''))
        form.addRow("Registration Date:", reg_de)

        fitness_de = make_dateedit_from_str(vehicle_widget.details_data.get('fitness_upto', ''))
        form.addRow("Fitness Valid UpTo:", fitness_de)

        tax_de = make_dateedit_from_str(vehicle_widget.details_data.get('tax_upto', ''))
        form.addRow("Tax Valid UpTo:", tax_de)

        insurance_de = make_dateedit_from_str(vehicle_widget.details_data.get('insurance_upto', ''))
        form.addRow("Insurance Valid UpTo:", insurance_de)

        pucc_de = make_dateedit_from_str(vehicle_widget.details_data.get('pucc_upto', ''))
        form.addRow("PUCC Valid UpTo:", pucc_de)

        permit_de = make_dateedit_from_str(vehicle_widget.details_data.get('permit_upto', ''))
        form.addRow("Permit Valid UpTo:", permit_de)

        nat_permit_de = make_dateedit_from_str(vehicle_widget.details_data.get('national_permit_upto', ''))
        form.addRow("National Permit Valid UpTo:", nat_permit_de)

        driver_name_edit = QLineEdit()
        driver_name_edit.setText(vehicle_widget.details_data.get('driver_name', ''))
        form.addRow("Driver Name:", driver_name_edit)

        driver_contact_edit = QLineEdit()
        driver_contact_edit.setText(vehicle_widget.details_data.get('driver_contact', ''))
        form.addRow("Contact No:", driver_contact_edit)

        driver_alt_contact_edit = QLineEdit()
        driver_alt_contact_edit.setText(vehicle_widget.details_data.get('driver_alt_contact', ''))
        form.addRow("Alternative Number:", driver_alt_contact_edit)

        driver_experience_edit = QLineEdit()
        driver_experience_edit.setText(vehicle_widget.details_data.get('driver_experience', ''))
        form.addRow("Experience:", driver_experience_edit)

        driver_adhar_edit = QLineEdit()
        driver_adhar_edit.setText(vehicle_widget.details_data.get('driver_adhar', ''))
        form.addRow("Aadhaar Number:", driver_adhar_edit)

        # New fields: Date of Joining and Bank Account Number
        date_of_joining_de = make_dateedit_from_str(vehicle_widget.details_data.get('driver_date_of_joining', ''))
        form.addRow("Date of Joining:", date_of_joining_de)

        bank_account_edit = QLineEdit()
        bank_account_edit.setText(vehicle_widget.details_data.get('driver_bank_account', ''))
        form.addRow("Bank Account Number:", bank_account_edit)

        # License upload section
        license_layout = QVBoxLayout()
        license_button_layout = QHBoxLayout()
        license_upload_btn = QPushButton("Upload License")
        license_remove_btn = QPushButton("Remove License")
        license_remove_btn.setEnabled(bool(vehicle_widget.details_data.get('driver_license_path', '')))
        license_path_label = QLabel(vehicle_widget.details_data.get('driver_license_path', 'No file uploaded'))
        license_path_label.setStyleSheet("font-style: italic; color: #555555;")
        license_path_label.setMinimumWidth(300)
        license_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        license_button_layout.addWidget(license_upload_btn)
        license_button_layout.addWidget(license_remove_btn)
        license_button_layout.addWidget(license_path_label)
        license_button_layout.addStretch()
        license_layout.addLayout(license_button_layout)

        license_image_label = QLabel()
        license_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_image_label.setFixedSize(300, 200)
        license_image_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        license_layout.addWidget(license_image_label)
        form.addRow("License:", license_layout)

        def show_license_image(path):
            if path and os.path.isfile(path):
                supported_formats = [bytes(fmt).decode().lower() for fmt in QImageReader.supportedImageFormats()]
                ext = os.path.splitext(path)[1][1:].lower()
                if ext in supported_formats:
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            license_image_label.width(), license_image_label.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        license_image_label.setPixmap(scaled_pixmap)
                        return
            license_image_label.clear()

        show_license_image(vehicle_widget.details_data.get('driver_license_path', ''))

        def upload_license():
            fname, _ = QFileDialog.getOpenFileName(dlg, "Select License File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
            if fname:
                vehicle_widget.details_data['driver_license_path'] = fname
                license_path_label.setText(os.path.basename(fname))
                license_remove_btn.setEnabled(True)
                show_license_image(fname)

        def remove_license():
            confirm = QMessageBox.question(
                dlg,
                "Confirm Remove License",
                "Are you sure you want to remove the uploaded license image?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                vehicle_widget.details_data['driver_license_path'] = ''
                license_path_label.setText('No file uploaded')
                license_remove_btn.setEnabled(False)
                license_image_label.clear()

        license_upload_btn.clicked.connect(upload_license)
        license_remove_btn.clicked.connect(remove_license)

        # Loan details
        loan_total_edit = QLineEdit()
        loan_total_edit.setText(vehicle_widget.details_data.get('loan_total', ''))
        loan_total_edit.setPlaceholderText("Total amount")
        loan_paid_edit = QLineEdit()
        loan_paid_edit.setText(vehicle_widget.details_data.get('loan_paid', ''))
        loan_paid_edit.setPlaceholderText("Paid amount")
        loan_remaining_label = QLabel(vehicle_widget.details_data.get('loan_remaining', '0'))
        loan_remaining_label.setStyleSheet("font-weight: bold;")
        loan_remaining_label.setMinimumWidth(80)

        loan_layout = QHBoxLayout()
        loan_layout.addWidget(QLabel("Total:"))
        loan_layout.addWidget(loan_total_edit)
        loan_layout.addWidget(QLabel("Paid:"))
        loan_layout.addWidget(loan_paid_edit)
        loan_layout.addWidget(QLabel("Remaining:"))
        loan_layout.addWidget(loan_remaining_label)
        form.addRow("Loan:", loan_layout)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        def update_remaining():
            try:
                total = float(loan_total_edit.text())
            except ValueError:
                total = 0
            try:
                paid = float(loan_paid_edit.text())
            except ValueError:
                paid = 0
            remaining = max(total - paid, 0)
            loan_remaining_label.setText(f"{remaining:.2f}")

        loan_total_edit.textChanged.connect(update_remaining)
        loan_paid_edit.textChanged.connect(update_remaining)
        update_remaining()

        def on_save():
            vehicle_widget.details_data['vehicle_no'] = vehicle_no_edit.text().strip()
            vehicle_widget.details_data['registration_date'] = reg_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['fitness_upto'] = fitness_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['tax_upto'] = tax_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['insurance_upto'] = insurance_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['pucc_upto'] = pucc_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['permit_upto'] = permit_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['national_permit_upto'] = nat_permit_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['driver_name'] = driver_name_edit.text().strip()
            vehicle_widget.details_data['driver_contact'] = driver_contact_edit.text().strip()
            vehicle_widget.details_data['driver_alt_contact'] = driver_alt_contact_edit.text().strip()
            vehicle_widget.details_data['driver_experience'] = driver_experience_edit.text().strip()
            vehicle_widget.details_data['driver_adhar'] = driver_adhar_edit.text().strip()
            vehicle_widget.details_data['driver_date_of_joining'] = date_of_joining_de.date().toString("yyyy-MM-dd")
            vehicle_widget.details_data['driver_bank_account'] = bank_account_edit.text().strip()
            vehicle_widget.details_data['loan_total'] = loan_total_edit.text().strip()
            vehicle_widget.details_data['loan_paid'] = loan_paid_edit.text().strip()
            vehicle_widget.details_data['loan_remaining'] = loan_remaining_label.text()
            vehicle_widget.update_details_summary()
            QMessageBox.information(self, "Saved", f"Details saved for {vehicle_widget.name}")
            dlg.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)

        dlg.exec()
        self.refresh_grid()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #f0f4f8;
            color: #003366;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        QScrollArea {
            border: none;
            background-color: #f0f4f8;
        }
    """)
    window = VehicleApp()
    window.showMaximized()
    sys.exit(app.exec())
