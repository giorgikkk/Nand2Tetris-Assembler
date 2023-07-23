from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Assembler:
    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        COMP_DICT = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "M": "1110000",
            "!D": "0001101",
            "!A": "0110001",
            "!M": "1110001",
            "-D": "0001111",
            "-A": "0110011",
            "-M": "1110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "M+1": "1110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "M-1": "1110010",
            "D+A": "0000010",
            "D+M": "1000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&A": "0000000",
            "D&M": "1000000",
            "D|A": "0010101",
            "D|M": "1010101",
        }

        DEST_DICT = {
            "": "000",
            "M=": "001",
            "D=": "010",
            "MD=": "011",
            "A=": "100",
            "AM=": "101",
            "AD=": "110",
            "AMD=": "111",
        }

        JUMP_DICT = {
            "": "000",
            ";JGT": "001",
            ";JEQ": "010",
            ";JGE": "011",
            ";JLT": "100",
            ";JNE": "101",
            ";JLE": "110",
            ";JMP": "111",
        }

        assembly = list(assembly)
        hack = []
        labels_dict = {}
        line_counter = 0
        register_counter = 16

        # Remove comments if present
        for i in range(len(assembly)):
            assembly_line = assembly[i]
            if assembly_line.__contains__("//"):
                space_index = assembly_line.index(" ")
                assembly[i] = assembly_line[:space_index]
        # Save number of first unused lines
        lines_to_remove = 0
        for i in range(len(assembly)):
            assembly_line = assembly[i]
            if assembly_line.startswith("//") or len(assembly_line) < 1:
                lines_to_remove += 1
        # Filter from first unused lines
        assembly = assembly[lines_to_remove:]

        # Save indexes of labels
        for assembly_line in assembly:
            if assembly_line[0] == "(":
                label_end_index = assembly_line.index(")")
                label = assembly_line[1:label_end_index]
                labels_dict[label] = line_counter
            else:
                line_counter += 1
        temp_labels_dict = labels_dict.copy()

        # Replace labels with digits
        for i in range(len(assembly)):
            assembly_line = assembly[i]

            if assembly_line[0] == "@" and assembly_line[1:] == "SCREEN":
                assembly[i] = "@" + str(16384)
            elif assembly_line[0] == "@" and assembly_line[1:] == "KBD":
                assembly[i] = "@" + str(24576)
            elif assembly_line[0] == "@" and assembly_line[1:] == "SP":
                assembly[i] = "@" + str(0)
            elif assembly_line[0] == "@" and assembly_line[1:] == "LCL":
                assembly[i] = "@" + str(1)
            elif assembly_line[0] == "@" and assembly_line[1:] == "ARG":
                assembly[i] = "@" + str(2)
            elif assembly_line[0] == "@" and assembly_line[1:] == "THIS":
                assembly[i] = "@" + str(3)
            elif assembly_line[0] == "@" and assembly_line[1:] == "THAT":
                assembly[i] = "@" + str(4)
            elif assembly_line[0] == "@" and temp_labels_dict.__contains__(
                assembly_line[1:]
            ):
                assembly[i] = "@" + str(temp_labels_dict[assembly_line[1:]])
            elif (
                assembly_line[0] == "@"
                and not temp_labels_dict.__contains__(assembly_line[1:])
                and assembly_line.__contains__("R")
            ):
                assembly[i] = assembly_line.replace("R", "")
            elif (
                assembly_line[0] == "@"
                and not temp_labels_dict.__contains__(assembly_line[1:])
                and not assembly_line.__contains__("R")
                and not assembly_line[1].isdigit()
            ):
                temp_labels_dict[assembly_line[1:]] = register_counter
                assembly[i] = "@" + str(register_counter)
                register_counter += 1
        # Delete labels
        for label_line in labels_dict.values():
            del assembly[label_line]
        # Translate assembly into hack binary
        for assembly_line in assembly:
            hack_line = ""
            if assembly_line[0] == "@":
                hack_line += "0"
                decimal_value = int(assembly_line[1:])
                binary_str = format(decimal_value, "016b")[1:]
                hack_line += binary_str
            else:
                hack_line += "1"
                hack_line += "11"
                if assembly_line.__contains__(";"):
                    comp_index = assembly_line.index(";")
                    curr_comp = assembly_line[:comp_index]
                    hack_line += COMP_DICT[curr_comp]

                    hack_line += DEST_DICT[""]

                    curr_jump = assembly_line[comp_index:]
                    hack_line += JUMP_DICT[curr_jump]
                else:
                    if assembly_line.__contains__(" "):
                        comp_start_index = assembly_line.index("=") + 1
                        comp_end_index = assembly_line.index(" ")
                        curr_comp = assembly_line[comp_start_index:comp_end_index]
                        hack_line += COMP_DICT[curr_comp]
                    else:
                        comp_start_index = assembly_line.index("=") + 1
                        curr_comp = assembly_line[comp_start_index:]
                        hack_line += COMP_DICT[curr_comp]
                    dest_end_index = comp_start_index
                    curr_dest = assembly_line[:dest_end_index]
                    hack_line += DEST_DICT[curr_dest]

                    hack_line += JUMP_DICT[""]
            hack.append(hack_line)
        return hack
