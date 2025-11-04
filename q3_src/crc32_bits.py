# crc32_bits.py  
# Fast table-driven version of CRC-32 (non-reflected, MSB-first).
# Uses the standard Ethernet polynomial 0x04C11DB7.
# This handles all the math for computing and checking CRC remainders.

import random

POLY = 0x04C11DB7  # official CRC-32 generator polynomial
R = 32  # number of CRC remainder bits

# ---------- Build lookup table (makes it faster) ----------
def _make_table():
    # This precomputes 256 possible byte results so we can process data faster
    tbl = []
    for i in range(256):
        c = i << 24
        for _ in range(8):
            # Shift left and XOR with the polynomial if MSB is 1
            if c & 0x80000000:
                c = ((c << 1) & 0xFFFFFFFF) ^ POLY
            else:
                c = (c << 1) & 0xFFFFFFFF
        tbl.append(c)
    return tbl

_TBL = _make_table()

def _update_crc_msb(crc: int, byte: int) -> int:
    # Update CRC with one byte (MSB-first)
    idx = ((crc >> 24) ^ byte) & 0xFF
    return (_TBL[idx] ^ ((crc << 8) & 0xFFFFFFFF)) & 0xFFFFFFFF

# ---------- Helper functions ----------
def _is_bin(s: str) -> bool:
    # Quick check — make sure it's a binary string (only 0s and 1s)
    return s and set(s) <= {"0", "1"}

def _bits_to_bytes(bits: str) -> bytes:
    # Convert bit string (like "1010...") to real bytes for faster math
    if len(bits) % 8 != 0:
        raise ValueError("bitstring length must be a multiple of 8")
    return int(bits, 2).to_bytes(len(bits) // 8, "big")

def _bits_len_ok(n: int):
    # CRC works on whole bytes only — this just checks that
    if n % 8 != 0:
        raise ValueError("bit length must be multiple of 8")

# ---------- Core CRC functions ----------
def crc_divide(bits: str, poly: str) -> str:
    """
    Simulates dividing 'bits' by the polynomial.
    Returns remainder as binary string (len(G)-1 bits).
    """
    if not _is_bin(bits):
        raise ValueError("bits must be a non-empty binary string.")
    if not _is_bin(poly) or poly[0] != "1" or len(poly) < 2:
        raise ValueError("poly must start with '1' and have degree >= 1.")
    rlen = len(poly) - 1

    # Start with CRC = 0, then process byte by byte
    data = _bits_to_bytes(bits)
    crc = 0
    for b in data:
        crc = _update_crc_msb(crc, b)

    # Convert numeric CRC back to a binary string
    return f"{crc:0{rlen}b}" if rlen > 0 else ""

def crc32_send(payload_bits: str) -> str:
    """
    Sender side: calculate the CRC remainder and append it to the message.
    Basically P = M + R (like M * x^32 mod G).
    """
    if not _is_bin(payload_bits):
        raise ValueError("payload_bits must be binary.")
    _bits_len_ok(len(payload_bits))

    # Start CRC at 0 and process message bytes
    data = _bits_to_bytes(payload_bits)
    crc = 0
    for b in data:
        crc = _update_crc_msb(crc, b)

    # Simulate appending 32 zero bits (x^32)
    for _ in range(4):
        crc = _update_crc_msb(crc, 0x00)

    # Add the remainder to the end of the frame
    rem_bits = f"{crc:032b}"
    return payload_bits + rem_bits

def crc32_check(frame_bits: str) -> bool:
    """
    Receiver side: checks if the received frame gives a remainder of zero.
    If yes → no error detected.
    """
    if not _is_bin(frame_bits):
        raise ValueError("frame_bits must be binary.")
    _bits_len_ok(len(frame_bits))

    data = _bits_to_bytes(frame_bits)
    crc = 0
    for b in data:
        crc = _update_crc_msb(crc, b)

    # If remainder = 0 → message passed the check
    return crc == 0

def rand_bits(n: int) -> str:
    # Generate a random n-bit message (used for experiments)
    _bits_len_ok(n)
    return format(random.getrandbits(n), "b").zfill(n)
