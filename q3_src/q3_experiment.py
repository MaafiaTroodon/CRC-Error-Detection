# q3_experiment.py
# Tests how well CRC-32 detects burst errors of different lengths.
# Runs 50 trials for burst sizes 1 to 64 bits on 1520-byte random messages.

from crc32_bits import rand_bits, crc32_send, crc32_check
import random

MSG_BYTES = 1520
MSG_BITS = MSG_BYTES * 8
TRIALS = 50  # how many times we test each burst length

def force_span(bits: str, start: int, L: int, val: str) -> str:
    """
    Flip a chunk of bits (make all 0 or all 1) — simulates a burst error.
    """
    b = list(bits)
    end = min(start + L, len(b))
    for i in range(start, end):
        b[i] = val
    return ''.join(b)

if __name__ == "__main__":
    # Set a random seed so results are repeatable
    random.seed(4171)

    rows = []
    for L in range(1, 65):
        detected = 0  # how many bursts were caught
        for _ in range(TRIALS):
            # Generate a random 1520-byte message
            msg = rand_bits(MSG_BITS)

            # Sender computes the CRC and adds remainder
            frame = crc32_send(msg)

            # Randomly choose where to insert a burst error
            start = random.randint(0, len(frame) - L)
            forced_bit = random.choice(['0', '1'])
            corrupted = force_span(frame, start, L, forced_bit)

            # Receiver checks if error is detected
            if not crc32_check(corrupted):
                detected += 1

        # Calculate detection rate as a percentage
        rate = 100.0 * detected / TRIALS
        rows.append((L, TRIALS, detected, rate))

    # Write final results to a file (plain text table)
    with open("q3_results.txt", "w") as f:
        f.write("Burst Length (bits)\tTrials\tErrors Detected\tDetection Rate (%)\n")
        for L, T, D, R in rows:
            f.write(f"{L}\t{T}\t{D}\t{R:.1f}\n")

    print("Wrote q3_results.txt")  # simple completion message
