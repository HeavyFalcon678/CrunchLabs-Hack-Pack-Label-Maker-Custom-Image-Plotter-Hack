import pytest
import numpy as np
from label_image.label_image import pack_bitmap

def test_pack_bitmap_2x2():
    matrix = [
        [1, 0],
        [0, 1]
    ]
    expected_bytes = [0b00000101]
    assert pack_bitmap(matrix, 2) == expected_bytes

def test_pack_bitmap_4x4():
    matrix = [
        [1, 0, 1, 1],
        [0, 1, 1, 0],  # Serpentine: right to left
        [1, 0, 0, 1],
        [1, 1, 0, 0]   # Serpentine: right to left
    ]
    expected_bytes = [0b01101101, 0b11001001]  # Packed output
    assert pack_bitmap(matrix, 4) == expected_bytes

def test_pack_bitmap_8x8_all_ones():
    matrix = np.ones((8, 8), dtype=int).tolist()  # 8x8 all 1s
    expected_bytes = [0xFF] * 8  # 8 bytes, each 0xFF (11111111)
    assert pack_bitmap(matrix, 8) == expected_bytes

def test_pack_bitmap_8x8_all_zeros():
    matrix = np.zeros((8, 8), dtype=int).tolist()  # 8x8 all 0s
    expected_bytes = [0x00] * 8  # 8 bytes, each 0x00 (00000000)
    assert pack_bitmap(matrix, 8) == expected_bytes

def test_pack_bitmap_5x5():
    matrix = [
        [1, 0, 1, 1, 0],
        [0, 1, 1, 0, 1],  # Serpentine
        [1, 0, 0, 1, 1],
        [1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1],
    ]
    expected_bytes = [0b10101101, 0b01100101, 0b10001110, 0b00000001]
    assert pack_bitmap(matrix, 5) == expected_bytes
