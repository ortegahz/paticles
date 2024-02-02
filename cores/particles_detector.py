from data.data import DataRT


class ParticlesDetector:
    def __init__(self):
        self.db = DataRT()

    def infer(self):
        if int(self.db.db['pm025'][-1]) > 1000:
            self.db.db['alarm'][-1] = 4096
