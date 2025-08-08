class Cell:
    def __init__(self, options, elevation=None):
        self.collapsed = False
        self.options = options[:]
        self.elevation = elevation