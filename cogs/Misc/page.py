class Page:

    def __init__(self, start: int, end: int, step: int):
        self.last_start = start
        self.start = start
        self.end = end
        self.step = step

    def next(self):
        self.start += self.step
        if self.start < self.start + self.step > self.end:
            self.start = self.end - self.step

        old_start = self.last_start
        self.last_start = self.start
        return self.start, old_start

    def last(self):
        self.start -= self.step
        if self.start < self.start + self.step < self.step:
            self.start = 0

        old_start = self.last_start
        self.last_start = self.start
        return self.start, old_start
