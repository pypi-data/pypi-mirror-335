def string_to_hex(string: str) -> str:
    """
    >>> string_to_hex("hi")
    '\\\\x68\\\\x69'

    """
    return ''.join(f'\\x{ord(s):02x}' for s in string)


def hex_to_string(hex_string: str) -> str:
    """
    >>> hex_to_string("\\\\x68\\\\x69")
    'hi'

    """
    hex_pairs = [hex_string[i:i + 4] for i in range(0, len(hex_string), 4)]
    return ''.join(chr(int(pair[2:], 16)) for pair in hex_pairs if pair.startswith('\\x'))
