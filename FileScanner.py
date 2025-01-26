import os
import sys
import hashlib
import shutil  # Add this import
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QFileDialog, QHeaderView, QProgressBar, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class FileScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileScanner v1.0")

        # Gérer le chemin de l'icône pour qu'elle fonctionne avec PyInstaller
        if getattr(sys, 'frozen', False):  # Si packagé avec PyInstaller
            icon_path = os.path.join(sys._MEIPASS, "FileScanner.ico")
        else:
            icon_path = "FileScanner.ico"

        self.setWindowIcon(QIcon(icon_path))

        self.setGeometry(200, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f2f5;")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Dashboard Header
        header_layout = QHBoxLayout()
        self.files_scanned_label = self.create_stat_card("Files Scanned", "0")
        self.duplicates_found_label = self.create_stat_card("Duplicate Groups", "0")
        self.duplicate_files_label = self.create_stat_card("Duplicate Files", "0")
        header_layout.addWidget(self.files_scanned_label)
        header_layout.addWidget(self.duplicates_found_label)
        header_layout.addWidget(self.duplicate_files_label)
        main_layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                text-align: center;
                height: 20px;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #4caf50; /* Green */
                border-radius: 8px;
            }
        """)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Table to show selected folders
        self.folder_table = QTableWidget(0, 1)
        self.folder_table.setHorizontalHeaderLabels(["Selected Folders"])
        self.folder_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.folder_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                font-size: 14px;
                border-radius: 8px;
                gridline-color: #dee2e6;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border-radius: 0;
            }
        """)
        self.folder_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.folder_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.folder_table.setFixedHeight(150)
        self.folder_table.verticalHeader().setVisible(False)  # Hide row numbers
        main_layout.addWidget(self.folder_table)

        # Buttons to manage folders
        folder_buttons_layout = QHBoxLayout()
        self.select_folders_button = QPushButton("Add Folder")
        self.select_folders_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px; border-radius: 8px;")
        self.select_folders_button.clicked.connect(self.select_folders)
        folder_buttons_layout.addWidget(self.select_folders_button)

        self.remove_folder_button = QPushButton("Remove Selected Folder")
        self.remove_folder_button.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; border-radius: 8px;")
        self.remove_folder_button.clicked.connect(self.remove_selected_folder)
        folder_buttons_layout.addWidget(self.remove_folder_button)

        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 8px;")
        self.start_scan_button.clicked.connect(self.scan_folders)
        folder_buttons_layout.addWidget(self.start_scan_button)

        main_layout.addLayout(folder_buttons_layout)

        # Table for duplicate files
        self.table = QTableWidget(0, 5)  # Adding a column for checkboxes
        self.table.setHorizontalHeaderLabels(["", "ID", "File Name", "Path", "Size"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                font-size: 14px;
                border-radius: 8px;
                gridline-color: #dee2e6;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border-radius: 0;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Select
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # File Name
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Path
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Size
        self.table.verticalHeader().setVisible(False)  # Hide row numbers
        main_layout.addWidget(self.table)

        # Buttons for duplicate actions
        duplicate_buttons_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; border-radius: 8px;")
        self.delete_button.clicked.connect(self.delete_selected_files)
        duplicate_buttons_layout.addWidget(self.delete_button)

        self.move_button = QPushButton("Move Selected")
        self.move_button.setStyleSheet("background-color: #FF7F00; color: white; padding: 10px; border-radius: 8px;")
        self.move_button.clicked.connect(self.move_selected_files)
        duplicate_buttons_layout.addWidget(self.move_button)

        main_layout.addLayout(duplicate_buttons_layout)

        # Footer with links
        footer_links = QLabel()
        footer_links.setAlignment(Qt.AlignCenter)
        footer_links.setText(
            '<a href="https://github.com/RomainGOSSELIN/FileScanner" style="color: black; text-decoration: none;">GitHub</a> | '
            '<a href="https://www.linkedin.com/in/romaingosselin/" style="color: black; text-decoration: none;">LinkedIn</a>'
        )
        footer_links.setOpenExternalLinks(True)
        footer_links.setStyleSheet("margin-top: 20px; font-size: 12px;")
        main_layout.addWidget(footer_links)

        # List to store folder paths
        self.folder_paths = []

    def create_stat_card(self, title, value):
        card = QWidget()
        card.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 10px;"
        )
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #343a40;")
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet("color: #007bff;")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        layout.addWidget(value_label, alignment=Qt.AlignCenter)
        card.setLayout(layout)
        return card

    def update_stat_card(self, label, value):
        layout = label.layout()
        value_label = layout.itemAt(1).widget()
        value_label.setText(value)

    def select_folders(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_paths.append(folder_path)
            self.folder_table.insertRow(self.folder_table.rowCount())
            folder_item = QTableWidgetItem(folder_path)
            folder_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.folder_table.setItem(self.folder_table.rowCount() - 1, 0, folder_item)

    def remove_selected_folder(self):
        selected_row = self.folder_table.currentRow()
        if selected_row >= 0:
            self.folder_paths.pop(selected_row)
            self.folder_table.removeRow(selected_row)

    def scan_folders(self):
        if not self.folder_paths:
            QMessageBox.warning(self, "No Folders Selected", "Please select at least one folder to scan.")
            return

        self.progress_bar.setValue(0)
        self.file_hashes = {}
        self.duplicates = {}
        self.files_scanned = 0
        self.total_files = sum(len(files) for folder in self.folder_paths for _, _, files in os.walk(folder))
        self.total_duplicate_files = 0

        self.scan_thread = ScanThread(self.folder_paths)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.result.connect(self.process_scan_result)
        self.scan_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def process_scan_result(self, file_hash, file_path):
        self.files_scanned += 1
        if file_hash:
            if file_hash not in self.duplicates:
                self.duplicates[file_hash] = []
            self.duplicates[file_hash].append(file_path)

        if self.files_scanned == self.total_files:
            self.total_duplicate_files = sum(len(file_list) - 1 for file_list in self.duplicates.values() if len(file_list) > 1)  # Fix calculation

            self.populate_table(self.duplicates)
            self.update_stat_card(self.files_scanned_label, str(self.files_scanned))
            self.update_stat_card(self.duplicates_found_label, str(len([g for g in self.duplicates.values() if len(g) > 1])))
            self.update_stat_card(self.duplicate_files_label, str(self.total_duplicate_files))  # Adjust counter
            QMessageBox.information(self, "Scan Complete", "The scan has completed successfully.")

    def populate_table(self, duplicates):
        self.table.setRowCount(0)
        colors = ["#8A4F7D", "#7EBDC2", "#679436", "#BA2D0B"]
        group_id = 1

        for file_hash, files in duplicates.items():
            if len(files) > 1:  # Only display groups with more than one file
                color = colors[(group_id - 1) % len(colors)]
                for file_path in files:
                    row_idx = self.table.rowCount()
                    self.table.insertRow(row_idx)

                    checkbox_widget = QWidget()
                    checkbox_layout = QHBoxLayout(checkbox_widget)
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    checkbox = QCheckBox()
                    checkbox.setStyleSheet("QCheckBox::indicator { width: 50%; height: 50%; }")
                    checkbox_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                    self.table.setCellWidget(row_idx, 0, checkbox_widget)

                    id_item = QTableWidgetItem(str(group_id))
                    id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_idx, 1, id_item)

                    file_item = QTableWidgetItem(os.path.basename(file_path))
                    file_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_idx, 2, file_item)

                    path_item = QTableWidgetItem(file_path)
                    path_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_idx, 3, path_item)

                    size_item = QTableWidgetItem(f"{os.path.getsize(file_path) // 1024} KB")
                    size_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_idx, 4, size_item)

                    for col_idx in range(1, 5):
                        self.table.item(row_idx, col_idx).setBackground(QColor(color))
                group_id += 1

    def delete_selected_files(self):
        if not self.any_files_selected():
            QMessageBox.warning(self, "No Files Selected", "Please select files to delete.")
            return

        deleted_files_count = 0
        for row_idx in reversed(range(self.table.rowCount())):
            cell_widget = self.table.cellWidget(row_idx, 0)
            if cell_widget is None or cell_widget.layout().count() == 0:
                continue

            checkbox = cell_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                file_path = self.table.item(row_idx, 3).text()
                try:
                    os.remove(file_path)
                    deleted_files_count += 1
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
                self.table.removeRow(row_idx)

        QMessageBox.information(
            self,
            "Files Deleted",
            f"Successfully deleted {deleted_files_count} files."
        )

    def move_selected_files(self):
        if not self.any_files_selected():
            QMessageBox.warning(self, "No Files Selected", "Please select files to move.")
            return

        target_folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if not target_folder:
            return

        moved_files_count = 0
        for row_idx in reversed(range(self.table.rowCount())):
            cell_widget = self.table.cellWidget(row_idx, 0)
            if cell_widget is None or cell_widget.layout().count() == 0:
                continue

            checkbox = cell_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                file_path = self.table.item(row_idx, 3).text()
                try:
                    new_path = os.path.join(target_folder, os.path.basename(file_path))
                    shutil.move(file_path, new_path)
                    moved_files_count += 1
                except Exception as e:
                    print(f"Error moving file {file_path}: {e}")
                self.table.removeRow(row_idx)

        QMessageBox.information(
            self,
            "Files Moved",
            f"Successfully moved {moved_files_count} files."
        )

    def any_files_selected(self):
        for row_idx in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row_idx, 0)
            if cell_widget is None or cell_widget.layout().count() == 0:
                continue

            checkbox = cell_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                return True
        return False


class ScanThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str, str)

    def __init__(self, folder_paths):
        super().__init__()
        self.folder_paths = folder_paths

    def run(self):
        files_scanned = 0
        total_files = sum(len(files) for folder in self.folder_paths for _, _, files in os.walk(folder))

        for folder in self.folder_paths:
            for root, _, files in os.walk(folder):
                for file in files:
                    files_scanned += 1
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = self.get_file_hash(file_path)
                        self.result.emit(file_hash, file_path)
                    except OSError as e:
                        print(f"Error processing file {file_path}: {e}")
                    progress = int((files_scanned / total_files) * 100)
                    self.progress.emit(progress)

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return None


if __name__ == "__main__":
    app = QApplication([])
    dashboard = FileScanner()
    dashboard.show()
    app.exec()
