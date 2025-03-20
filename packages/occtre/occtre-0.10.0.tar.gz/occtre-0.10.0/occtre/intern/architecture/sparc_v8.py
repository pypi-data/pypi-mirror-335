# SPDX-License-Identifier: GTDGmbH
# Copyright 2023 by GTD GmbH.
"""Class configuring the sparc v8 architecture."""

from .architecture import Architecture

# fmt: off
sparc_v8_Bicc_opcodes = [
    # conditional icc branch opcodes
    "ba", "bn", "bne", "be", "bg", "ble", "bge", "bl", "bgu", "bleu", "bcc",
    "bcs", "bpos", "bneg", "bvc", "bvs",
]

sparc_v8_FBfcc_opcodes = [
    # conditional fcc branch opcodes
    "fba", "fbn", "fbu", "fbg", "fbug", "fbl", "fbul", "fblg", "fbne", "fbe",
    "fbue", "fbge", "fbuge", "fble", "fbule", "fbo",
]

sparc_v8_CBfcc_opcodes = [
    # conditional coprocessor opcodes
    "cba", "cbn", "cb3", "cb2", "cb23", "cb1", "cb13", "cb12", "cb123", "cb0",
    "cb03", "cb02", "cb023", "cb01", "cb013", "cb012",
]

sparc_v8_Ticc_opcodes = [
    # condictional traps on icc
    "ta", "tn", "tne", "te", "tg", "tle", "tge", "tl", "tgu", "tleu", "tcc",
    "tcs", "tpos", "tneg", "tvc", "tvs",
]

sparc_v8_Load_opcodes = [
    # load opcodes
    "ld", "ldsb", "ldsh", "ldub", "lduh", "ldd", "ldf", "lddf", "ldfsr", "ldc", "lddc", "ldcsr",
]

sparc_v8_Store_opcodes = [
    # store opcodes
    "st", "stb", "sth", "std", "stf", "stdf", "stfsr", "stdfq", "stc", "stdc", "stcsr", "stdcq",
]

sparc_v8_branch_cond_delay_opcodes = [
    f"{x},a" for x in
    sparc_v8_Bicc_opcodes +
    sparc_v8_FBfcc_opcodes +
    sparc_v8_CBfcc_opcodes
]

sparc_v8_remaining_jump_opcodes = [
    "jmpl", "ret",  # "call", not regarded currently
]

sparc_v8_delayed_opcodes = sparc_v8_Bicc_opcodes + \
                           sparc_v8_FBfcc_opcodes + \
                           sparc_v8_CBfcc_opcodes + \
                           sparc_v8_branch_cond_delay_opcodes + \
                           sparc_v8_remaining_jump_opcodes

sparc_v8_branch_opcodes = sparc_v8_Bicc_opcodes + \
                          sparc_v8_FBfcc_opcodes + \
                          sparc_v8_CBfcc_opcodes + \
                          sparc_v8_Ticc_opcodes + \
                          sparc_v8_branch_cond_delay_opcodes + \
                          sparc_v8_remaining_jump_opcodes

sparc_v8_memory_access_opcodes = sparc_v8_Load_opcodes + \
                                 sparc_v8_Store_opcodes


# fmt: on


class SparcV8Architecture(Architecture):
    """Sparc V8 Architecture."""

    name: str = "SparcV8"

    def is_jump(self, opcode: str = "") -> bool:
        return opcode in sparc_v8_branch_opcodes

    def get_delay(self, opcode: str = "") -> int:
        if opcode in sparc_v8_delayed_opcodes:
            return 1
        return 0

    def is_memory_access(self, opcode: str = "") -> bool:
        return opcode in sparc_v8_memory_access_opcodes
