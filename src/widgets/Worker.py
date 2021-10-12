from PySide6.QtCore import QObject, Signal, QRunnable, QDateTime, Qt


class WorkerSignals(QObject):
    __started = Signal()
    __loaded = Signal()
    __progress = Signal(int)
    __result = Signal(object)
    __error = Signal()
    __success = Signal()
    __finished = Signal()

    @property
    def started(self):
        return self.__started

    @property
    def loaded(self):
        return self.__loaded

    @property
    def progress(self):
        return self.__progress

    @property
    def result(self):
        return self.__result

    @property
    def error(self):
        return self.__error

    @property
    def success(self):
        return self.__success

    @property
    def finished(self):
        return self.__finished


class Worker(QRunnable):
    def __init__(self, **kwargs: dict):
        super().__init__()
        self.__init_property(kwargs)

    @property
    def signals(self):
        return self.__signals

    def __init_property(self, kwargs: dict):
        self.__src_folder_path = kwargs["src_folder_path"]
        self.__dst_folder_path = kwargs["dst_folder_path"]
        self.__code = kwargs["code"]
        self.__signals = WorkerSignals()

    # @Slot()
    def run(self):
        exec(self.__code)

    def __log_error(self, e: Exception, comment=None):
        import sys
        from pathlib import Path
        from traceback import format_exc

        app_path = (
            Path(sys.executable)
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
            else Path(__file__)
        )

        with open(app_path.parent / "ErrorLogs.txt", "a", encoding="utf8") as f:
            logs = [
                "===\n",
                format_exc(),
                f"Date: {QDateTime.currentDateTime().toString(Qt.ISODate)}\n",
                f"Src_Folder_Path: {self.__src_folder_path}\n",
                f"Dst_Folder_Path: {self.__dst_folder_path}\n",
            ]

            if comment:
                logs.append(f"{comment}\n")

            logs.append("===\n\n")

            f.writelines(logs)
