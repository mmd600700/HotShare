def generate_qr_code(target_size, text):
    exp = [0] * 512
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x <<= 1
        if (x & 0x100) != 0:
            x ^= 0x11D
    for i in range(255, 512):
        exp[i] = exp[i - 255]

    def gf_multiply(a, b):
        if a == 0 or b == 0:
            return 0
        return exp[log[a] + log[b]]

    def get_generator(degree):
        gen = [1]
        for i in range(degree):
            next_gen = [0] * (len(gen) + 1)
            next_gen[0] = gen[0]
            for j in range(1, len(gen)):
                next_gen[j] = gen[j] ^ gf_multiply(gen[j - 1], exp[i])
            next_gen[len(gen)] = gf_multiply(gen[-1], exp[i])
            gen = next_gen
        return gen

    def calculate_ecc(data, gen):
        msg = data + [0] * (len(gen) - 1)
        for i in range(len(data)):
            factor = msg[i]
            if factor == 0:
                continue
            for j in range(len(gen)):
                msg[i + j] ^= gf_multiply(gen[j], factor)
        return msg[len(data):]

    raw_data = text.encode('utf-8')
    if len(raw_data) > 62:
        raise ValueError()

    bits = [False] * 512
    bit_pos = 0

    bits[bit_pos] = False; bit_pos += 1
    bits[bit_pos] = True;  bit_pos += 1
    bits[bit_pos] = False; bit_pos += 1
    bits[bit_pos] = False; bit_pos += 1

    length = len(raw_data)
    for i in range(7, -1, -1):
        bits[bit_pos] = ((length >> i) & 1) == 1
        bit_pos += 1

    for b in raw_data:
        for i in range(7, -1, -1):
            bits[bit_pos] = ((b >> i) & 1) == 1
            bit_pos += 1

    terminator_limit = min(4, 512 - bit_pos)
    for i in range(terminator_limit):
        bits[bit_pos] = False
        bit_pos += 1

    while bit_pos % 8 != 0:
        bits[bit_pos] = False
        bit_pos += 1

    pad_switch = True
    while bit_pos < 512:
        pad_byte = 0xEC if pad_switch else 0x11
        for i in range(7, -1, -1):
            bits[bit_pos] = ((pad_byte >> i) & 1) == 1
            bit_pos += 1
        pad_switch = not pad_switch

    data_words = [0] * 64
    for i in range(64):
        b = 0
        for j in range(8):
            if bits[i * 8 + j]:
                b |= (1 << (7 - j))
        data_words[i] = b

    block1_data = data_words[0:32]
    block2_data = data_words[32:64]

    gen = get_generator(18)
    block1_ecc = calculate_ecc(block1_data, gen)
    block2_ecc = calculate_ecc(block2_data, gen)

    final_data = [0] * 100
    idx = 0
    for i in range(32):
        final_data[idx] = block1_data[i]; idx += 1
        final_data[idx] = block2_data[i]; idx += 1
    for i in range(18):
        final_data[idx] = block1_ecc[i]; idx += 1
        final_data[idx] = block2_ecc[i]; idx += 1

    matrix = [[-1 for _ in range(33)] for _ in range(33)]

    def draw_finder(start_x, start_y):
        for y in range(-1, 8):
            for x in range(-1, 8):
                cx = start_x + x
                cy = start_y + y
                if cx < 0 or cx >= 33 or cy < 0 or cy >= 33:
                    continue
                if x == -1 or x == 7 or y == -1 or y == 7:
                    matrix[cy][cx] = 0
                elif x == 0 or x == 6 or y == 0 or y == 6:
                    matrix[cy][cx] = 1
                elif x == 1 or x == 5 or y == 1 or y == 5:
                    matrix[cy][cx] = 0
                else:
                    matrix[cy][cx] = 1

    draw_finder(0, 0)
    draw_finder(26, 0)
    draw_finder(0, 26)

    for y in range(-2, 3):
        for x in range(-2, 3):
            is_black = (x == -2 or x == 2 or y == -2 or y == 2 or (x == 0 and y == 0))
            matrix[26 + y][26 + x] = 1 if is_black else 0

    for i in range(8, 25):
        matrix[6][i] = 1 if i % 2 == 0 else 0
        matrix[i][6] = 1 if i % 2 == 0 else 0

    matrix[25][8] = 1

    for i in range(9):
        if matrix[8][i] == -1: matrix[8][i] = 2
        if matrix[i][8] == -1: matrix[i][8] = 2
    for i in range(25, 33):
        if matrix[8][i] == -1: matrix[8][i] = 2
        if matrix[i][8] == -1: matrix[i][8] = 2

    bit_idx = 0
    dir_y = -1
    x = 32
    y = 32
    while x > 0:
        if x == 6: x -= 1
        while 0 <= y < 33:
            for i in range(2):
                cx = x - i
                if matrix[y][cx] == -1:
                    bit = False
                    if bit_idx < 800:
                        bit = ((final_data[bit_idx // 8] >> (7 - (bit_idx % 8))) & 1) == 1
                    mask_bit = ((y + cx) % 2 == 0)
                    matrix[y][cx] = 1 if (bit ^ mask_bit) else 0
                    bit_idx += 1
            y += dir_y
        dir_y = -dir_y
        y += dir_y
        x -= 2

    format_bits = [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1]
    xs1 = [8, 8, 8, 8, 8, 8, 8, 8, 7, 5, 4, 3, 2, 1, 0]
    ys1 = [0, 1, 2, 3, 4, 5, 7, 8, 8, 8, 8, 8, 8, 8, 8]
    xs2 = [8, 8, 8, 8, 8, 8, 8, 25, 26, 27, 28, 29, 30, 31, 32]
    ys2 = [32, 31, 30, 29, 28, 27, 26, 8, 8, 8, 8, 8, 8, 8, 8]

    for i in range(15):
        matrix[ys1[i]][xs1[i]] = format_bits[i]
        matrix[ys2[i]][xs2[i]] = format_bits[i]

    padding = 4
    total_modules = 33 + (2 * padding)
    scale = target_size / float(total_modules)
    new_size = int(round(scale * total_modules))

    scaled_matrix = [[0] * new_size for _ in range(new_size)]

    for yy in range(new_size):
        for xx in range(new_size):
            mx = int(xx / scale) - padding
            my = int(yy / scale) - padding
            
            if 0 <= mx < 33 and 0 <= my < 33:
                val = matrix[my][mx]
                if val == 2:
                    val = 0
                scaled_matrix[yy][xx] = 1 if val == 1 else 0
            else:
                scaled_matrix[yy][xx] = 0

    return scaled_matrix