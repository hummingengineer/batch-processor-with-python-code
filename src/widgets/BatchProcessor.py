from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QApplication,
    QStyle,
    QLineEdit,
    QGridLayout,
    QGroupBox,
    QComboBox,
    QPlainTextEdit,
    QProgressBar,
    QFileDialog,
    QMessageBox,
)


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__init_property()
        self.__init_ui()
        self.__connect_signal_to_slot()

    def __init_property(self):
        pass

    def __init_ui(self):
        # Directory Section
        self.__src_folder_btn = QPushButton(
            icon=QIcon(
                QApplication.style().standardIcon(QStyle.SP_FileDialogNewFolder)
            ),
            toolTip="Select the source folder.",
        )

        self.__src_folder_line_edit = QLineEdit(
            enabled=False, readOnly=True, toolTip="Source folder path"
        )

        self.__dst_folder_btn = QPushButton(
            icon=QIcon(
                QApplication.style().standardIcon(QStyle.SP_FileDialogNewFolder)
            ),
            toolTip="Select the destination folder.",
        )

        self.__dst_folder_line_edit = QLineEdit(
            enabled=False, readOnly=True, toolTip="Destination folder path"
        )

        dir_grid = QGridLayout()
        dir_grid.addWidget(self.__src_folder_btn, 0, 0)
        dir_grid.addWidget(self.__src_folder_line_edit, 0, 1)
        dir_grid.addWidget(self.__dst_folder_btn, 1, 0)
        dir_grid.addWidget(self.__dst_folder_line_edit, 1, 1)

        dir_gbox = QGroupBox(title="Directory Section")
        dir_gbox.setLayout(dir_grid)

        # Code Section
        self.__combo_box = QComboBox()
        self.__combo_box.addItems(
            [
                "New...",
                "Create folders from files",
                "Extract thumbnails from each folders",
            ]
        )

        self.__text_area = QPlainTextEdit()

        code_grid = QGridLayout()
        code_grid.addWidget(self.__combo_box, 0, 0)
        code_grid.addWidget(self.__text_area, 1, 0)

        code_gbox = QGroupBox(title="Code Section")
        code_gbox.setLayout(code_grid)

        # Progress Bar
        self.__pbar = QProgressBar(alignment=Qt.AlignCenter)

        # Run Button
        self.__run_btn = QPushButton(
            icon=QIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay)),
            toolTip="Execute your code.",
        )

        # Main UI
        grid = QGridLayout()
        grid.addWidget(dir_gbox, 0, 0)
        grid.addWidget(code_gbox, 1, 0)
        grid.addWidget(self.__pbar, 2, 0)
        grid.addWidget(self.__run_btn, 3, 0)

        self.setLayout(grid)

    def __connect_signal_to_slot(self):
        self.__src_folder_btn.clicked.connect(lambda: self.__select_folder("source"))
        self.__dst_folder_btn.clicked.connect(
            lambda: self.__select_folder("destination")
        )
        self.__combo_box.activated.connect(self.__select_combo_box_item)
        self.__run_btn.clicked.connect(self.__execute_code)

    # @Slot()
    def __select_folder(self, dir_type):
        if folder_path := QFileDialog.getExistingDirectory(
            caption=f"Select the {dir_type} folder",
            options=QFileDialog.ShowDirsOnly
            | QFileDialog.DontResolveSymlinks
            | QFileDialog.ReadOnly,
        ):
            if dir_type == "source":
                self.__src_folder_line_edit.setText(folder_path)
            elif dir_type == "destination":
                self.__dst_folder_line_edit.setText(folder_path)

    # @Slot()
    def __select_combo_box_item(self, idx):
        # New...
        if idx == 0:
            self.__text_area.clear()
        # Create folders from files
        elif idx == 1:
            self.__text_area.setPlainText(
                """try:
    self._Worker__signals.started.emit()

    from os import walk
    from pathlib import Path

    names = []

    for root, _, files in walk(top=self._Worker__src_folder_path):
        if not files:
            continue

        for name in files:
            names.append(Path(f"{root}/{name}").stem)

    # idx starts at 0, so (total count - 1)
    names_count = len(names) - 1

    self._Worker__signals.loaded.emit()

    for idx, name in enumerate(names):
        dst_file_path = Path(f"{self._Worker__dst_folder_path}/{name}")

        dst_file_path.mkdir(parents=True, exist_ok=True)

        percentage = int(((idx) / names_count) * 100.0)

        self._Worker__signals.progress.emit(percentage)
except Exception as e:
    self._Worker__log_error(e)
    self._Worker__signals.error.emit()
else:
    self._Worker__signals.success.emit()
finally:
    self._Worker__signals.finished.emit()
"""
            )
        # Extract thumbnails from each folders
        elif idx == 2:
            pass

    # @Slot()
    def __execute_code(self):
        if self.__check():
            self.__run_btn.setEnabled(False)
            self.__pbar.setValue(0)
            self.__pbar.setFormat("Loading...")

            from widgets.Worker import Worker

            worker = Worker(
                src_folder_path=self.__src_folder_line_edit.text(),
                dst_folder_path=self.__dst_folder_line_edit.text(),
                code=self.__text_area.toPlainText(),
            )
            worker.signals.loaded.connect(self.__pbar.resetFormat)
            worker.signals.progress.connect(self.__update_progress_bar)
            worker.signals.finished.connect(self.__enable_run_btn)

            QThreadPool.globalInstance().start(worker)

    def __check(self) -> bool:
        if not self.__src_folder_line_edit.text():
            QMessageBox.critical(self, "Error", "Select source folder path.")
            return False
        if not self.__dst_folder_line_edit.text():
            QMessageBox.critical(self, "Error", "Select destination folder path.")
            return False
        if not self.__text_area.toPlainText():
            QMessageBox.critical(self, "Error", "Write the code.")
            return False

        return True

    # @Slot()
    def __update_progress_bar(self, percentage):
        self.__pbar.setValue(percentage)

    # @Slot()
    def __enable_run_btn(self):
        self.__run_btn.setEnabled(True)


class BatchProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("Batch Processor")

        self.setCentralWidget(CentralWidget())

    def closeEvent(self, event):
        QThreadPool.globalInstance().waitForDone()
