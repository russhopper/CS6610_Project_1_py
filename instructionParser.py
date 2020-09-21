import re

def dec_to_bin(num_dec, bit_len):
    num_dec = int(num_dec)
    b = f'{num_dec:0{bit_len}b}'[:bit_len]
    return b

class instructionParser:

    def __init__(self, file_lines):
        self.__data_start, self.__text_start = '0x10000000', '0x400000'
        self.__file_lines = file_lines
        self.__dataSection, self.__dataSectionSize = self.__getDataSection()
        self.__textSection, self.__textSectionSize = self.__getTextSection()
        self.__binaryRepresentation = self.__generateBinary()
        self.__binaryRepresentation_lst = [self.__binaryRepresentation[i:i+32] for i in range(0,len(self.__binaryRepresentation), 32)]

    def __instr_to_bin_funct_lookup(self, funct):
        def beq(rs, rt, tgt_lbl, pc):
            # conversion calculation part 1. (pc_target - pc_current) / 4
            # I subtracted -4 to get a positive instead of negative result
            target_minus_pc = int(self.__textSection[tgt_lbl], 16) - int(self.__text_start, 16) // -4
            # subtract one and flip bits to get two's complement representing the actual (negative) answer
            bin_t_m_p = dec_to_bin(target_minus_pc - 1, 8)
            twos_complement = ''.join([{'0':'1','1':'0'}[b] for b in bin_t_m_p])
            offset = dec_to_bin(int(f'0xFF', 16), 8) + twos_complement
            return f'000100{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{offset}'
            
        def bne(rs, rt, tgt_lbl, pc):
            # conversion calculation part 1. (pc_target - pc_current) / 4
            # I subtracted -4 to get a positive instead of negative result
            target_minus_pc = int(self.__textSection[tgt_lbl], 16) - int(self.__text_start, 16) // -4
            # subtract one and flip bits to get two's complement representing the actual (negative) answer
            bin_t_m_p = dec_to_bin(target_minus_pc - 1, 8)
            twos_complement = ''.join([{'0':'1','1':'0'}[b] for b in bin_t_m_p])
            offset = dec_to_bin(int(f'0xFF', 16), 8) + twos_complement
            return f'000100{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{offset}'
        
        funct_lkup = {
            'add' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100000',
            'addi' : lambda rt, rs, imm : f'001000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'addiu' : lambda rt, rs, imm : f'001001{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'addu' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100001',
            'and' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100100',
            'andi' : lambda rt, rs, imm : f'001100{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'beq' : beq, 
            'bne' : bne,
            'j' : lambda target_lbl : f'00001000{dec_to_bin(int(self.__textSection[target_lbl], 16), 24)[:-2]}',
            'jal' : lambda target_lbl : f'00001000{dec_to_bin(int(self.__textSection[target_lbl], 16), 24)[:-2]}',
            'jr' : lambda rs : f'000000{dec_to_bin(rs, 5)}000000000000000001000',
            'lui' : lambda rt, imm : f'00111100000{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'lw' : lambda rt, offset, base : f'100011{dec_to_bin(base, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(offset, 16)}',
            'nor' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100111',
            'or' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100101',
            'ori' : lambda rt, rs, imm : f'001101{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'sll' : lambda rd, rt, sa : f'00000000000{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}{dec_to_bin(sa, 5)}000000',
            'sltiu' : lambda rt, rs, imm : f'001011{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'sltu' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000101011',
            'srl' : lambda rd, rt, sa : f'00000000000{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}{dec_to_bin(sa, 5)}000010',
            'subu' : lambda rd, rs, rt : f'000000{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}00000100011',
            'sw' : lambda rt, offset, base : f'101011{dec_to_bin(base, 5)}{dec_to_bin(rt, 5)}{dec_to_bin(offset, 16)}',
            }
    
        return funct_lkup[funct]

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
                ds[dataLine[:lbl_split]] = hex(pc + int(self.__data_start, 16))
            pc += 4

        return ds, pc // 4

    def __getTextSection(self):
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
                ts[textLine2[:lbl_split]] = hex(pc + int(self.__text_start, 16))
            else:
                pc += 4
        return ts, pc // 4

    def __hexDec_to_int(self, n):
        if 'x' in n:
            return int(n, 16)
        return int(n)

    def __generateBinary(self):
        binStr = ''
        # header: sizes as bytes (*4)
        txtSize_bin = dec_to_bin(self.__textSectionSize * 4, 32)
        dtaSize_bin = dec_to_bin(self.__dataSectionSize * 4, 32)
        binStr += txtSize_bin + dtaSize_bin

        # for each instruction in .text, generate binary
        pc = 0
        instr_bin_lines = []
        text_s = 0
        for i, l in enumerate(self.__file_lines):
            if '.text' in l:
                text_s = i
                break

        filteredTextLines = [l for l in self.__file_lines[text_s + 1:] if ':' not in l]
        
        for textLine in filteredTextLines:
            parts = [p for p in re.split('\s|,|, |\$|\(|\)|\t', textLine) if p and p not in ['', ' ']]
            parts_conv = [self.__hexDec_to_int(c) if c.isdigit() else c for c in parts]
            # if the last element in parts_conv is a label, find the address and pass that in instead
            if parts_conv[-1] in self.__dataSection.keys():
                parts_conv[-1] = self.__hexDec_to_int(self.__dataSection[parts_conv[-1]])
            if parts_conv[0] in ['bne', 'beq']:
                parts_conv.append(pc)
            if '0x' in str(parts_conv[-1]):
                parts_conv[-1] = self.__hexDec_to_int(parts_conv[-1])
            instr_bin_lines.append(self.__instr_to_bin_funct_lookup(parts_conv[0])(*parts_conv[1:]))
            pc += 4

        

        return binStr + ''.join(instr_bin_lines)

    @property
    def binaryRepresentation(self):
        return self.__binaryRepresentation
    
    def __str__(self):
        return f'''
data section: {self.__dataSection}
text section: {self.__textSection}
data size: {self.__dataSectionSize}
text size: {self.__textSectionSize}
binary rep: {self.__binaryRepresentation}
'''