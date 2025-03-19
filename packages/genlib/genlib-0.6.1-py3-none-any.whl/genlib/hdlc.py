HDLC_FLAG = b'\x7E'     # Byte used for HDLC frame boundary (0x7E)
HDLC_ESC  = b'\x7D'     # Escape byte (0x7D)
ESC_FLAG  = b'\x5E'     # 0x7E ^ 0x20 => 0x5E
ESC_ESC   = b'\x5D'     # 0x7D ^ 0x20 => 0x5D

__decode_state = {
    'started': False,      # Indicates whether a frame (message) has started
    'escaped': False,      # Indicates if the previous byte was the escape byte (0x7D)
    'data': bytearray(),   # Buffer for storing the currently received message
    'pending_end': False,  # State right after seeing a FLAG (indicating the end)
    'junk': bytearray()    # Temporary storage for data before a frame starts
}

def decode(chunk: bytes) -> list[bytes]:
    """
    Decodes the given byte stream (chunk) using HDLC flag (0x7E) and escape (0x7D) rules.

    - Multiple chunks may arrive in sequence, and this function can be called repeatedly
      until a complete message is obtained.
    - Collects junk data that appears before an actual frame. If no valid frame appears,
      the junk is discarded and only valid messages are returned in the result list.
    """
    result = []
    data = __decode_state['data']
    junk = __decode_state['junk']
    started = __decode_state['started']
    escaped = __decode_state['escaped']
    pending_end = __decode_state['pending_end']

    for char in chunk:
        if escaped:
            # If the previous byte was ESC (0x7D), interpret the current byte
            if char == ESC_FLAG[0]:
                data.append(HDLC_FLAG[0])  # Restore 0x7E
            elif char == ESC_ESC[0]:
                data.append(HDLC_ESC[0])   # Restore 0x7D
            else:
                # If it's not a known escape sequence, consider it a receive failure and reset
                data.clear()
                junk.clear()
                started = False
                pending_end = False
                escaped = False
                return []
            escaped = False

        elif char == HDLC_ESC[0]:
            # If we encounter an ESC byte, prepare to escape the next byte
            escaped = True

        elif char == HDLC_FLAG[0]:
            # If we encounter the HDLC flag (0x7E)
            if pending_end:
                # Another FLAG right after one has ended:
                # finalize the previous message ONLY if it has actual data
                if started and len(data) > 0:
                    result.append(bytes(data))
                    data.clear()
                else:
                    junk.clear()
                # Now consider this FLAG as a new start
                started = True
                pending_end = False

            elif started:
                # If a message has already started and we see another FLAG, the message ends here
                result.append(bytes(data))
                data.clear()
                started = False
                pending_end = True

            else:
                # If a FLAG is found when no message has started yet, prepare to start a new message
                started = True
                pending_end = True

        else:
            # Handle a normal byte
            if pending_end:
                # If we're right after seeing a FLAG, start a new message
                started = True
                data.append(char)
                pending_end = False
            elif started:
                data.append(char)
            else:
                # If we haven't started a message yet, store it in junk
                junk.append(char)

    # Preserve the state
    __decode_state['started'] = started
    __decode_state['escaped'] = escaped
    __decode_state['pending_end'] = pending_end

    return tuple(result)


def encode(payload: bytes) -> bytes:
    """
    Encodes the given byte stream (payload) in HDLC style by
    adding start/end flags (0x7E) and escaping any 0x7E or 0x7D in the payload.
    """
    # 1) Byte replacement: 0x7D -> 0x7D 0x5D, 0x7E -> 0x7D 0x5E
    escaped_payload = (
        payload
        .replace(HDLC_ESC, HDLC_ESC + ESC_ESC)      # 0x7D -> 0x7D 0x5D
        .replace(HDLC_FLAG, HDLC_ESC + ESC_FLAG)    # 0x7E -> 0x7D 0x5E
    )

    # 2) Surround the payload with FLAG (0x7E) to form a frame
    return HDLC_FLAG + escaped_payload + HDLC_FLAG
