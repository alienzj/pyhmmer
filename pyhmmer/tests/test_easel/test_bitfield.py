import pickle
import unittest
import sys

from pyhmmer import easel


class TestBitfield(unittest.TestCase):

    @unittest.skipIf(sys.implementation.name == "pypy", "`getsizeof` not supported on PyPY")
    def test_sizeof(self):
        bitfield = easel.Bitfield(8)
        self.assertGreater(sys.getsizeof(bitfield), 0)

    def test_buffer_protocol(self):
        bitfield = easel.Bitfield(8)
        self.assertEqual(memoryview(bitfield).tobytes()[0], 0b00000000)
        bitfield[0] = bitfield[2] = bitfield[3] = True
        self.assertEqual(memoryview(bitfield).tobytes()[0], 0b00001101)
        bitfield2 = easel.Bitfield(256)
        self.assertEqual(memoryview(bitfield2).shape[0], 4)

    def test_index_error(self):
        bitfield = easel.Bitfield(8)
        with self.assertRaises(IndexError):
            bitfield[9] = 1
        with self.assertRaises(IndexError):
            bitfield[-9] = 1

    def test_eq(self):
        b1 = easel.Bitfield(8)
        self.assertNotEqual(b1, object())

        b2 = easel.Bitfield(8)
        self.assertEqual(b1, b2)

        b3 = easel.Bitfield(7)
        self.assertNotEqual(b1, b3)

        b1.toggle(0)
        self.assertNotEqual(b1, b2)
        b2.toggle(0)
        self.assertEqual(b1, b2)

    def test_pickle(self):
        b1 = easel.Bitfield(8)
        b1[2] = b1[4] = True

        b2 = pickle.loads(pickle.dumps(b1))
        self.assertEqual(b1, b2)

        b3 = easel.Bitfield(8)
        self.assertNotEqual(b2, b3)

    def test_getstate(self):
        b1 = easel.Bitfield(8)
        b1[2] = b1[4] = True

        b2 = easel.Bitfield(8)
        b2[2] = b2[4] = True

        self.assertEqual(b1.__getstate__(), b2.__getstate__())
