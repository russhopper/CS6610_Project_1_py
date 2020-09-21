def dec_to_bin(num_dec, bit_len):
    b = f'{num_dec:b}'
    if bit_len - len(b) < 0:
        raise Exception("Bit length for conversion is less than binary number.")
    return f"{'0'*(bit_len-len(b))}{b}"

class instructionParser:
    def __init__(self, file_lines):
        self.__file_lines = file_lines
        self.__dataSection, self.__dataSectionSize = self.__getDataSection()
        self.__textSection, self.__textSectionSize = self.__getTextSection()
        self.__binaryRepresentation = self.__generateBinary()
        # self.__binaryRepresentation_lst = [self.__binaryRepresentation[i:i+32] for i in range(0,len(self.__binaryRepresentation), 32)]

    # def __instr_to_bin_funct_lookup(self, funct):
    #     funct_lkup = {
    #         'add' : lambda rd, rs, rt : f'000000{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{dec_to_bin(int(rd), 5)}00000100000',
    #         'addi' : lambda rt, rs, imm : f'001000{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{self.__dataSection[imm]}',
    #         'addiu' : lambda rt, rs, imm : f'001001{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{self.__dataSection[imm]}',
    #         'addu' : lambda rd, rs, rt : f'000000{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{dec_to_bin(int(rd), 5)}00000100001',
    #         'and' : lambda rd, rs, rt : f'000000{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{dec_to_bin(int(rd), 5)}00000100100',
    #         'andi' : lambda rt, rs, imm : f'001100{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{self.__dataSection[imm]}',
    #         'beq' : lambda rs, rt, ofst : f'000100{dec_to_bin(int(rs), 5)}{dec_to_bin(int(rt), 5)}{self.__dataSection[imm]}'

    #     }
    #     pass

    def __convertLaInstruction(self, line):
        # lui and possibly ori
        retInstructions = []
        funct, rt, lbl = line.split()
        lbl_adrs = self.__dataSection[lbl]
        lbl_adrs_dec = int(lbl_adrs, 16)
        lbl_adrs_bin = dec_to_bin(lbl_adrs_dec, 32)
        # make lui inst
        lui = f'\tlui\t{rt}, {lbl}'
        retInstructions.append(lui)
        if '1' in lbl_adrs_bin[16:]:
            # ? it seems like ori uses rt as both rs and rt parts
            ori = f'\tori\t{rt} {rt} {lbl}'
            retInstructions.append(ori)
        return retInstructions

    
    def __getDataSection(self):
        data_strt = '0x10000000'
        pc = 0
        ds = {}
        data_s, text_s = 0, 0
        for i, l in enumerate(self.__file_lines):
            if '.data' in l:
                data_s = i
            if '.text' in l:
                text_s = i
                break

        filteredDataLines = self.__file_lines[data_s + 1:text_s]
        for dataLine in filteredDataLines:
            if dataLine.find(':') != -1:
                lbl_split = dataLine.index(':')
                ds[dataLine[:lbl_split]] = hex(pc + int(data_strt, 16))
            pc += 4

        return ds, pc // 4

    def __getTextSection(self):
        text_strt = '0x400000'
        pc = 0
        ts = {}
        text_s = 0
        for i, l in enumerate(self.__file_lines):
            if '.text' in l:
                text_s = i
                break

        filteredTextLines = self.__file_lines[text_s + 1:]
        # replace la with lui/ori as needed
        for i, textLine1 in enumerate(filteredTextLines):
            #? TODO fix this later, could accidentally catch names 'balla', etc. needs improvement
            if 'la\t' in textLine1: 
                mrkr = text_s + 1 + i
                self.__file_lines[mrkr:mrkr + 1] = self.__convertLaInstruction(textLine1)

        for textLine2 in filteredTextLines:
            if ':' in textLine2:
                lbl_split = textLine2.index(':')
                ts[textLine2[:lbl_split]] = hex(pc + int(text_strt, 16))
            else:
                pc += 4
        return ts, pc // 4

    def __generateBinary(self):
        binStr = ''
        # header: sizes as bytes (*4)
        txtSize_bin = dec_to_bin(self.__textSectionSize * 4, 32)
        dtaSize_bin = dec_to_bin(self.__dataSectionSize * 4, 32)
        binStr += txtSize_bin + dtaSize_bin

        # 
        return binStr
    
    def __str__(self):
        return f'''
data section: {self.__dataSection}
text section: {self.__textSection}
data size: {self.__dataSectionSize}
text size: {self.__textSectionSize}
binary rep: {self.__binaryRepresentation}
'''