if __name__ == "__main__":
    from sys import exit
    from PySide6.QtWidgets import QApplication
    from widgets.BatchProcessor import BatchProcessor

    app = QApplication([])

    batch_processor = BatchProcessor()
    batch_processor.show()

    exit(app.exec())
