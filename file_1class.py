class file:
    def __init__(self, name):
        self.name = name

    def read(self):
        with open(self.name, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self.name, 'w') as f:
            f.write(content)