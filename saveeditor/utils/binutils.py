def h2i(hex_string):
    hex_str = "".join(hex_string.split(" ")[::-1])
    return int(hex_str, 16)


def i2h(num, n_digits=8):
    hex_string = hex(num)[2:].upper().zfill(n_digits)
    hex_with_spaces = " ".join(
        hex_string[i : i + 2] for i in range(0, len(hex_string), 2)
    )
    hex_with_spaces = " ".join(hex_with_spaces.split(" ")[::-1])
    return hex_with_spaces


def get_offseted(data, offset, length):
    offset *= 2
    length *= 2
    offset_data = data[offset : offset + length]
    return [offset_data[i : i + 2] for i in range(0, len(offset_data), 2)]


def set_offseted(data, offset, new_data):
    offset *= 2
    new_data = "".join(new_data)
    data = data[:offset] + new_data + data[offset + len(new_data) :]
    return data
