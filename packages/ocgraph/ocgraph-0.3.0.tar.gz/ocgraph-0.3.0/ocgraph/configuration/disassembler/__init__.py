"""The main file of the disassembler module."""

from .disassembler import Disassembler as Disassembler
from .disassembler import ObjdumpDisassembler as ObjdumpDisassembler
from .gdb_default import GdbDisassembler as GdbDisassembler
from .objdump_arm import ObjDumpArmDisassembler as ObjDumpArmDisassembler
from .objdump_msp430 import ObjDumpMsp430Disassembler as ObjDumpMsp430Disassembler
from .objdump_ppc import ObjDumpPpcDisassembler as ObjDumpPpcDisassembler
from .objdump_sparc import ObjDumpSparcDisassembler as ObjDumpSparcDisassembler
from .objdump_x86 import ObjDumpx86Disassembler as ObjDumpx86Disassembler
