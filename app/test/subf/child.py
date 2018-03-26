class Child:
    def __init__(self, path):
        self.path = path

    def write(self):
        with open(self.path, 'w') as f:
            f.write('Coool \n')
        pass

ch = Child('test.txt')
ch.write()