from fileScanner import fileScanner
from instructionParser import instructionParser

inputFiles = ["example1.s", "example2_mod.s", "example3.s", "example4.s", "example5.s"]
inputFilesApp = [f"input/{fn}" for fn in inputFiles]
f_lines = []

for fn in inputFilesApp:
    fs = fileScanner(fn) 
    f_lines = fs.getLinesAsArray()
    inst_prs = instructionParser(f_lines)
    print(f'Filename: {fn} ----------')
    print(inst_prs)
    # input('continue?')

