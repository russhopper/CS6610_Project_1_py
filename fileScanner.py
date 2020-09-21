import re

class fileScanner:
    def __init__(self, filename):
        self.__filename = filename

    def getLinesAsArray(self):
        r = re.compile(r'\w')
        with open(self.__filename, 'r') as f:
            return [f for f in f.read().split('\n') if r.search(f)]
