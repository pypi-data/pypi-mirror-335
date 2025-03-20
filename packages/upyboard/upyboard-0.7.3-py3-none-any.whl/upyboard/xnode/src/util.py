import sys
import time
import uos
import machine

from micropython import const


class ANSIEC:
    class FG:
        BLACK = "\u001b[30m"
        RED = "\u001b[31m"
        GREEN = "\u001b[32m"
        YELLOW = "\u001b[33m"
        BLUE = "\u001b[34m"
        MAGENTA = "\u001b[35m"
        CYAN = "\u001b[36m"
        WHITE = "\u001b[37m"
        BRIGHT_BLACK= "\u001b[30;1m"
        BRIGHT_RED = "\u001b[31;1m"
        BRIGHT_GREEN = "\u001b[32;1m"
        BRIGHT_YELLOW = "\u001b[33;1m"
        BRIGHT_BLUE = "\u001b[34;1m"
        BRIGHT_MAGENTA = "\u001b[35;1m"
        BRIGHT_CYAN = "\u001b[36;1m"
        BRIGHT_WHITE = "\u001b[37;1m"
                
        @classmethod
        def rgb(cls, r, g, b): return "\u001b[38;2;{};{};{}m".format(r, g, b)

    class BG:
        BLACK = "\u001b[40m"
        RED = "\u001b[41m"
        GREEN = "\u001b[42m"
        YELLOW = "\u001b[43m"
        BLUE = "\u001b[44m"
        MAGENTA = "\u001b[45m"
        CYAN = "\u001b[46m"
        WHITE = "\u001b[47m"
        BRIGHT_BLACK= "\u001b[40;1m"
        BRIGHT_RED = "\u001b[41;1m"
        BRIGHT_GREEN = "\u001b[42;1m"
        BRIGHT_YELLOW = "\u001b[43;1m"
        BRIGHT_BLUE = "\u001b[44;1m"
        BRIGHT_MAGENTA = "\u001b[45;1m"
        BRIGHT_CYAN = "\u001b[46;1m"
        BRIGHT_WHITE = "\u001b[47;1m"
                
        @classmethod
        def rgb(cls, r, g, b): return "\u001b[48;2;{};{};{}m".format(r, g, b)

    class OP:
        RESET = "\u001b[0m"
        BOLD = "\u001b[1m"
        UNDER_LINE = "\u001b[4m"
        REVERSE = "\u001b[7m"
        CLEAR = "\u001b[2J"
        CLEAR_LINE = "\u001b[2K"
        TOP = "\u001b[0;0H"

        @classmethod
        def up(cls, n):
            return "\u001b[{}A".format(n)

        @classmethod
        def down(cls, n):
            return "\u001b[{}B".format(n)

        @classmethod
        def right(cls, n):
            return "\u001b[{}C".format(n)

        @classmethod
        def left(cls, n):
            return "\u001b[{}D".format(n)
        
        @classmethod
        def next_line(cls, n):
            return "\u001b[{}E".format(n)

        @classmethod
        def prev_line(cls, n):
            return "\u001b[{}F".format(n)
                
        @classmethod
        def to(cls, row, colum):
            return "\u001b[{};{}H".format(row, colum)

def sqrt(x, epsilon=1e-10):
    guess = x / 2.0

    op_limit = 5
    while abs(guess * guess - x) > epsilon and op_limit:
        guess = (guess + x / guess) / 2.0
        op_limit -= 1

    return guess

def abs(x):
    return x if x >= 0 else -x

def rand(size=4):
    return int.from_bytes(uos.urandom(size), "big")

def map(x, min_i, max_i, min_o, max_o):
    return (x - min_i) * (max_o - min_o) / (max_i - min_i) + min_o

def intervalChecker(interval):
    current_tick = time.ticks_us()   
    
    def check_interval():
        nonlocal current_tick
        
        if time.ticks_diff(time.ticks_us(), current_tick) >= interval * 1000:
            current_tick = time.ticks_us()
            return True
        return False
    
    return check_interval

def WDT(timeout):
    return machine.WDT(0, timeout)

def i2cdetect(bus=1, decorated=True):
    i2c = machine.I2C(bus)
    devices = i2c.scan()

    if decorated:
        output = "     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f"
        for i in range(0, 8):
            output += ANSIEC.FG.YELLOW + "\n{:02x}:".format(i*16) + ANSIEC.OP.RESET
            for j in range(0, 16):
                address = i * 16 + j
                if address in devices:
                    output += " {:02x}".format(address)
                else:
                    output += " --"
    else:
        output = devices
    
    return output

END = b'\xC0'
ESC = b'\xDB'
ESC_END = b'\xDC'
ESC_ESC = b'\xDD'


class Slip:
    __decode_state = {'started': False, 'escaped': False, 'data': bytearray(), 'pending_end': False, 'junk': bytearray()}
    
    @staticmethod
    def decode(chunk: bytes) -> list:
        """
        SLIP decoder. Returns a list of decoded byte strings.
        :param chunk: A byte string to decode.
        :return: A list of bytes.
        """
        result = []
        data = Slip.__decode_state['data']
        junk = Slip.__decode_state['junk']
        started = Slip.__decode_state['started']
        escaped = Slip.__decode_state['escaped']
        pending_end = Slip.__decode_state['pending_end']

        for char in chunk:
            if escaped:
                if char == ord(ESC_END):
                    data.append(ord(END))
                elif char == ord(ESC_ESC):
                    data.append(ord(ESC))
                else:
                    data.clear()
                    started = False
                    pending_end = False
                    return []
                escaped = False
            elif char == ord(ESC):
                escaped = True
            elif char == ord(END):
                if pending_end:
                    if started:
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

        Slip.__decode_state['started'] = started
        Slip.__decode_state['escaped'] = escaped
        Slip.__decode_state['pending_end'] = pending_end

        return result
    
    @staticmethod
    def encode(payload: bytes) -> bytes:
        """
        SLIP encoder. Returns a byte string.
        :param payload: A byte string to encode.
        :return: A byte string.
        """
        return END + payload.replace(ESC, ESC + ESC_ESC).replace(END, ESC + ESC_END) + END


class ReplUart:
    def __init__(self, timeout=None):
        self.timeout = timeout
    
    @property
    def timeout(self):
        return self.__timeout
    
    @timeout.setter
    def timeout(self, n):
        self.__timeout = n
    
    def read(self, size=1):        
        if self.timeout is None:
            assert size > 0, "size must be greater than 0"
            return sys.stdin.buffer.read(size)
        elif self.timeout is not None and self.timeout == 0:
            return sys.stdin.buffer.read(-1)
        elif self.timeout is not None and self.timeout > 0:
            rx_buffer = b''
            t0 = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), t0) / 1000 < self.timeout:
                b = sys.stdin.buffer.read(-1)
                if b:
                    rx_buffer += b
                    if len(rx_buffer) >= size:
                        break
            return rx_buffer
        
    def read_until(self, expected=b'\n', size=None):
        rx_buffer = bytearray()
        expected_len = len(expected)

        t0 = time.ticks_ms() if (self.timeout is not None and self.timeout > 0) else None 
        while True:
            if t0 is not None:
                ellipsis = time.ticks_diff(time.ticks_ms(), t0) / 1000
                if ellipsis >= self.timeout:
                    break  # Timeout

            try:
                b = sys.stdin.buffer.read(-1)
                if self.timeout is not None and self.timeout == 0:
                    return b if b else b''
            except Exception as e:
                return
                
            if not b: 
                continue

            rx_buffer.extend(b)

            if size is not None and len(rx_buffer) >= size:
                return bytes(rx_buffer[:size])

            if len(rx_buffer) >= expected_len and rx_buffer[-expected_len:] == expected:
                return bytes(rx_buffer)
        
        return bytes(rx_buffer) # Timeout occurred, return what's read so far
                    
    def write(self, data:bytes) -> int:
        assert isinstance(data, bytes), "data must be a byte type"
        
        ret = sys.stdout.write(data)
                
        return ret
