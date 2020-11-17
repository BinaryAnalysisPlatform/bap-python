import unittest
import bap

class TestLowLevelInterface(unittest.TestCase):

    def test_low_level_interface(self):
        asm_str = '\n'.join(insn.asm for insn in bap.disasm(b"\x48\x83\xec\x08"))
        self.assertIsNotNone(asm_str)
        self.assertIn("\tdecl\t%eax", asm_str)
        self.assertIn("\tsubl\t$0x8, %esp", asm_str)

if __name__ == "__main__":
    unittest.main()