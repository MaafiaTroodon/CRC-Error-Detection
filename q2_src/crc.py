# crc.py
# Simple CRC helper functions — no input/output. 
# Handles polynomial division, sender frame creation, and receiver validation.

def _is_binary_string(s: str) -> bool:
    # Check if string contains only 0s and 1s
    return len(s) > 0 and all(c in "01" for c in s)

def _validate_poly(G: str) -> None:
    # Make sure generator polynomial is valid
    if not _is_binary_string(G):
        raise ValueError("G must be a non-empty binary string.")
    if G[0] != '1':
        raise ValueError("G must start with '1' (highest degree term).")
    if len(G) < 2:
        raise ValueError("G must be at least degree 1 (length >= 2).")

def _validate_bits(M: str) -> None:
    # Make sure message/frame input is a binary string
    if not _is_binary_string(M):
        raise ValueError("Input message/frame must be a non-empty binary string.")

def crc_divide(bits: str, poly: str) -> str:
    """
    Perform CRC long division (mod 2) and return remainder.
    bits: the data to divide
    poly: the generator polynomial
    """
    _validate_bits(bits)
    _validate_poly(poly)

    # Convert to integer lists for XOR math
    w = [int(b) for b in bits]
    p = [int(b) for b in poly]
    plen = len(p)

    # XOR divide like in manual CRC calculation
    for i in range(len(w) - plen + 1):
        if w[i] == 1:
            for j in range(plen):
                w[i + j] ^= p[j]

    # Remainder is the last (len(G)-1) bits
    r = plen - 1
    return ''.join(str(x) for x in (w[-r:] if r > 0 else []))

def crc_send(M: str, G: str) -> str:
    """
    Sender side: append remainder to message (P = M || R).
    """
    _validate_bits(M)
    _validate_poly(G)
    r = len(G) - 1
    remainder = crc_divide(M + '0' * r, G)
    return M + remainder

def crc_check(frame: str, G: str) -> bool:
    """
    Receiver side: true if remainder is all zeros (no error found).
    """
    _validate_bits(frame)
    _validate_poly(G)
    rem = crc_divide(frame, G)
    return set(rem) <= {'0'}
