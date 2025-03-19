END = b'\xC0'
ESC = b'\xDB'
ESC_END = b'\xDC'
ESC_ESC = b'\xDD'

__decode_state = {
    'started': False,
    'escaped': False,
    'data': bytearray(),
    'pending_end': False,
    'junk': bytearray()
}

def decode(chunk: bytes) -> list:
    """
    SLIP decoder. Returns a list of decoded byte strings.
    :param chunk: A byte string to decode.
    :return: A list of bytes.
    """
    result = []
    data = __decode_state['data']
    junk = __decode_state['junk']
    started = __decode_state['started']
    escaped = __decode_state['escaped']
    pending_end = __decode_state['pending_end']

    for char in chunk:
        if escaped:
            if char == ord(ESC_END):
                data.append(ord(END))
            elif char == ord(ESC_ESC):
                data.append(ord(ESC))
            else:
                data.clear()
                junk.clear()
                started = False
                pending_end = False
                escaped = False
                return []
            escaped = False

        elif char == ord(ESC):
            escaped = True

        elif char == ord(END):
            if pending_end:
                if started and len(data) > 0:
                    result.append(bytes(data))
                    data.clear()
                else:
                    junk.clear()
                started = True
                pending_end = False

            elif started:
                result.append(bytes(data))
                data.clear()
                started = False
                pending_end = True

            else:
                started = True
                pending_end = True

        else:
            if pending_end:
                started = True
                data.append(char)
                pending_end = False
            elif started:
                data.append(char)
            else:
                junk.append(char)

    __decode_state['started'] = started
    __decode_state['escaped'] = escaped
    __decode_state['pending_end'] = pending_end

    return tuple(result)
    
def encode(payload: bytes) -> bytes:
    """
    SLIP encoder. Returns a byte string.
    :param payload: A byte string to encode.
    :return: A byte string.
    """
    return (
        END
        + payload.replace(ESC, ESC + ESC_ESC).replace(END, ESC + ESC_END)
        + END
    )
