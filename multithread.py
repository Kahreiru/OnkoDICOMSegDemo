from PySide6.QtCore import (
    QRunnable,
    Slot,
    Signal,
    QObject,
)

class WorkerSignals(QObject):
    finished = Signal()

class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        # Create object containing signals
        self.signals = WorkerSignals()


    @Slot()
    def run(self):
        """Initialise the runner function with passed args, kwargs."""
        print('Processing...Please Wait')
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit()
        print('Process Complete')