def encode_hamming74(d_int: int):
    d = [(d_int >> (3 - i)) & 1 for i in range(4)]
    d1, d2, d3, d4 = d[0], d[1], d[2], d[3]
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]

def decode_hamming74(r_bits):
    r = list(r_bits)
    s1 = r[0] ^ r[2] ^ r[4] ^ r[6]
    s2 = r[1] ^ r[2] ^ r[5] ^ r[6]
    s3 = r[3] ^ r[4] ^ r[5] ^ r[6]
    syndrome = (s3 << 2) | (s2 << 1) | s1
    corrected_pos = 0
    if syndrome != 0:
        corrected_pos = syndrome
        r[corrected_pos - 1] ^= 1
    data_bits = [r[2], r[4], r[5], r[6]]
    nibble_val = (data_bits[0] << 3) | (data_bits[1] << 2) | (data_bits[2] << 1) | data_bits[3]
    return syndrome, corrected_pos, r, nibble_val

errors = []
# 1. round trip with no noise for all 16 possible nibbles
for n in range(16):
    codeword = encode_hamming74(n)
    syn, pos, corrected, val = decode_hamming74(codeword)
    if syn != 0 or val != n:
        errors.append(("no-noise", n, codeword, syn, pos, val))

# 2. single-bit-flip correction for all 16 nibbles x all 7 positions
for n in range(16):
    codeword = encode_hamming74(n)
    for flip_pos in range(7):
        noisy = codeword[:]
        noisy[flip_pos] ^= 1
        syn, pos, corrected, val = decode_hamming74(noisy)
        if pos != flip_pos + 1 or val != n or corrected != codeword:
            errors.append(("single-flip", n, flip_pos, codeword, noisy, syn, pos, corrected, val))

print("Total errors found:", len(errors))
for e in errors[:20]:
    print(e)
