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
        
        def branch(funct, rs, rt, tgt_lbl, pc):
            f = {'beq' : '000100', 'bne' : '000101'}[funct]
            # conversion calculation part 1. (pc_target - pc_current) / 4
            # I subtracted -4 to get a positive instead of negative result
            target_pc = int(self.__textSection[tgt_lbl], 16) - int('0x400000', 16)
            target_minus_pc = (target_pc - pc) // 4
            target_minus_pc -= 1
            bin_target = ''
            was_negative = False
            if target_minus_pc < 0:
                was_negative = True
                # minus one, only if negative
                target_minus_pc += 1
                # flip bits
                target_minus_pc *= -1
                # convert to bin
                bin_target = dec_to_bin(target_minus_pc, 8)
                bin_target = ''.join(['0' if b == '1' else '1' for b in bin_target])
            else:
                bin_target = dec_to_bin(target_minus_pc, 8)
            extension = '0xFF' if was_negative else '0x00'
            offset = dec_to_bin(int(extension, 16), 8) + bin_target
            return f'{f}{dec_to_bin(rs, 5)}{dec_to_bin(rt, 5)}{offset}'
        
        def r_type(funct, rd, rs, rt):
            b_rs = dec_to_bin(rs, 5)
            b_rt = dec_to_bin(rt, 5)
            b_rd = dec_to_bin(rd, 5)
            funct_bin = {
                'add' : '100000',
                'addu' : '100001',
                'and' : '100100',
                'nor' : '100111',
                'or' : '100101',
                'sltu' : '101011',
                'subu' : '100011'
            }[funct]
            return f'000000{b_rs}{b_rt}{b_rd}00000{funct_bin}'

        def i_type(funct, rt, rs, imm):
            b_rt = dec_to_bin(rt, 5)
            b_rs = dec_to_bin(rs, 5)
            b_imm = dec_to_bin(imm, 16)
            funct_bin = {
                'addi' : '001000',
                'addiu' : '001001',
                'andi' : '001100',
                'ori' : '001101',
                'sltiu' : '001011'
            }[funct]
            return f'{funct_bin}{b_rs}{b_rt}{b_imm}'

        def lwsw_type(funct, rt, offset, base):
            f = {'lw' : '100011', 'sw' : '101011'}[funct]
            d_base = dec_to_bin(base, 5)
            d_rt = dec_to_bin(rt, 5)
            d_offset = dec_to_bin(offset, 16)
            return f'{f}{d_base}{d_rt}{d_offset}'

        
        funct_lkup = {
            'add' : r_type,
            'addi' : i_type,
            'addiu' : i_type,
            'addu' : r_type,
            'and' : r_type,
            'andi' : i_type,
            'beq' : branch, 
            'bne' : branch,
            'j' : lambda funct, target_lbl : f'0000100000{dec_to_bin(int(self.__textSection[target_lbl], 16), 24)[:-2]}',
            'jal' : lambda funct, target_lbl : f'0000100000{dec_to_bin(int(self.__textSection[target_lbl], 16), 24)[:-2]}',
            'jr' : lambda funct, rs : f'000000{dec_to_bin(rs, 5)}000000000000000001000',
            'lui' : lambda funct, rt, imm : f'00111100000{dec_to_bin(rt, 5)}{dec_to_bin(imm, 16)}',
            'lw' : lwsw_type,
            'nor' : r_type,
            'or' : r_type,
            'ori' : i_type,
            'sll' : lambda funct, rd, rt, sa : f'00000000000{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}{dec_to_bin(sa, 5)}000000',
            'sltiu' : i_type,
            'sltu' : r_type,
            'srl' : lambda funct, rd, rt, sa : f'00000000000{dec_to_bin(rt, 5)}{dec_to_bin(rd, 5)}{dec_to_bin(sa, 5)}000010',
            'subu' : r_type,
            'sw' : lwsw_type,
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
        lui = f'\tlui\t{rt} {int(lbl_adrs_bin[:16], 2)}'
        retInstructions.append(lui)
        if '1' in lbl_adrs_bin[16:]:
            # ? it seems like ori uses rt as both rs and rt parts
            ori = f'\tori\t{rt} {rt} {int(lbl_adrs_bin[16:], 2)}'
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

        
        filteredTextLines = self.__file_lines[text_s + 1:]
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
        line_to_pc = {}
        text_s = 0
        counter = 0
        for i, l in enumerate(self.__file_lines):
            if '.text' in l:
                text_s = i

        filteredTextLines = [l for l in self.__file_lines[text_s + 1:] if ':' not in l]
        
        for pc, textLine in enumerate(filteredTextLines):
            parts = [p for p in re.split('\s|,|, |\$|\(|\)|\t', textLine) if p and p not in ['', ' ']]
            parts_conv = [self.__hexDec_to_int(c) if c.isdigit() else c for c in parts]
            # if the last element in parts_conv is a label, find the address and pass that in instead
            if parts_conv[-1] in self.__dataSection.keys():
                parts_conv[-1] = self.__hexDec_to_int(self.__dataSection[parts_conv[-1]])
            if parts_conv[0] in ['bne', 'beq']:
                parts_conv.append(pc*4)
            if '0x' in str(parts_conv[-1]):
                parts_conv[-1] = self.__hexDec_to_int(parts_conv[-1])
            if parts_conv[0] == 'lw':
                a = 1
            bin_rep_of_instr = self.__instr_to_bin_funct_lookup(parts_conv[0])(*parts_conv)
            print(f'{textLine} : {bin_rep_of_instr}')
            binStr += bin_rep_of_instr
        print('\n\n')
        
        # append data section
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
            # if dataLine has data at the end hex/dec, then append as 32-bit str binary
            data_sp = dataLine.split()
            if data_sp[-1].isdigit() or '0x' in data_sp[-1]:
                converted_data = self.__hexDec_to_int(data_sp[-1])
                binStr += dec_to_bin(converted_data, 32)

        return binStr

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