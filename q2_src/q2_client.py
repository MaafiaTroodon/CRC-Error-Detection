# q2_client.py
# Small demo that shows CRC sender and receiver in action.

from crc import crc_send, crc_check, _is_binary_string

def flip_bit(s: str, idx: int) -> str:
    # Flip a single bit in the given position
    b = list(s)
    b[idx] = '1' if b[idx] == '0' else '0'
    return ''.join(b)

def read_binary(prompt: str) -> str:
    # Ask user for a binary string until they give a valid one
    while True:
        v = input(prompt).strip()
        if _is_binary_string(v):
            return v
        print("✗ Please enter a non-empty binary string (only 0/1).")

if __name__ == "__main__":
    print("=== CRC Demo (Q2) ===")

    # Get message and generator input from user
    M = read_binary("Enter M (binary): ")
    G = read_binary("Enter G (binary, starts with 1): ")

    # Sender computes transmitted frame
    try:
        P = crc_send(M, G)
    except Exception as e:
        print("Error:", e)
        raise SystemExit(1)

    print("Transmitted frame (P):", P)

    # Receiver input (can manually change or use same frame)
    recv = input("Enter received frame (blank = use P): ").strip() or P

    # Validate that it's a proper binary string
    if not _is_binary_string(recv):
        print("✗ Received frame must be a binary string (only 0/1).")
        raise SystemExit(1)

    # Optionally flip a bit to simulate an error
    inject = input("Flip one bit? (y/n): ").strip().lower()
    if inject == 'y':
        n = len(recv)
        while True:
            try:
                k = int(input(f"Bit index to flip [0..{n-1}]: ").strip())
                if 0 <= k < n:
                    break
                print(f"✗ Index must be in [0..{n-1}].")
            except ValueError:
                print("✗ Enter an integer.")
        recv = flip_bit(recv, k)
        print("Modified received frame:", recv)

    # Receiver checks for errors
    try:
        ok = crc_check(recv, G)
    except Exception as e:
        print("Error:", e)
        raise SystemExit(1)

    # Final output of validation result
    print("Validation:", "NO ERROR DETECTED" if ok else "ERROR DETECTED")
