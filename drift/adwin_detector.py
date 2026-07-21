from river.drift import ADWIN

class DriftDetector:
    def __init__(self):
        # delta=0.002 is the standard production setting.
        # Lower delta = stricter = fewer false positives on stable data.
        self.adwin = ADWIN(delta=0.002)

    def update(self, value):
        self.adwin.update(value)
        return self.adwin.drift_detected