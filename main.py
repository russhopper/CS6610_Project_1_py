from fileScanner import fileScanner
from instructionParser import instructionParser
from test import test
import re
from os import listdir
from os.path import isfile, join

mypath = r'input'
inputFiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
inputFilesApp = [f"input/{fn}" for fn in inputFiles]
f_lines = []

for fn in inputFilesApp:
    fs = fileScanner(fn) 
    f_lines = fs.getLinesAsArray()
    inst_prs = instructionParser(f_lines)
    print(f'Filename: {fn} ----------')
    f = open(f'{re.sub(r"input", "output", fn)[:-2]}.o', 'w')
    f.write(inst_prs.binaryRepresentation)
    f.close()

test()
