import utime
import uos
import machine


class ANSIEC:
    """
    Class that generates ANSI Escape Codes strings 
    """
    
    class FG:
        """
        Foreground Colors
        """
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
        def rgb(cls, r:int, g:int, b:int) -> str: 
            """
            Returns ANSI code for foreground color as rgb value
            
            :param r: red value
            :param g: green value
            :param b: blue value
            
            :return: Returns ANSI code for foreground color
            """

    class BG:
        """
        Background Colors
        """
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
        def rgb(cls, r:int, g:int, b:int) -> str:
            """
            Returns ANSI code for background color as rgb value
            
            :param r: red value
            :param g: green value
            :param b: blue value
            
            :return: Returns ANSI code for background color
            """

    class OP:
        """
        Operations
        """
        RESET = "\u001b[0m"
        BOLD = "\u001b[1m"
        UNDER_LINE = "\u001b[4m"
        REVERSE = "\u001b[7m"
        CLEAR = "\u001b[2J"
        CLEAR_LINE = "\u001b[2K"
        TOP = "\u001b[0;0H"

        @classmethod
        def up(cls, n:int) -> str:
            """
            Move cursor up
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor up
            """

        @classmethod
        def down(cls, n:int) -> str:
            """
            Move cursor down
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor down
            """
            
        @classmethod
        def right(cls, n:int) -> str:
            """
            Move cursor right
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor right
            """

        @classmethod
        def left(cls, n:int) -> str:
            """
            Move cursor left
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor left
            """
           
        @classmethod
        def next_line(cls, n:int) -> str:
            """
            Move cursor to the next line
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor to the next line
            """

        @classmethod
        def prev_line(cls, n:int) -> str:
            """
            Move cursor to the previous line
            
            :param n: Number of moves
            
            :return: Returns the ANSI Escape code to move the cursor to the previous line
            """
        
        @classmethod
        def to(cls, row, colum) -> str:
            """
            Move the cursor to that location
            
            :param row: Number of rows moved
            :param colum: Number of columns moved
            
            :return: Returns the ANSI Escape code to move the cursor
            """
            
def sqrt(x:int, epsilon:float=1e-10) -> float:
    """
    Newton's method for square root
    
    :param x: number to find square root
    :param epsilon: tolerance
    
    :return: square root of x
    """

def abs(x:int) -> int:
    """
    Absolute value
    
    :param x: number
    
    :return: absolute value of x
    """

def rand(size: int=4) -> int:
    """
    Generate random number
    
    :param size: size of random number
    
    :return: random number
    """

def map(x:float, min_i:float, max_i:float, min_o:float, max_o:float) -> float:
    """
    Map a number from one range to another
    
    :param x: number to map
    :param min_i: minimum value of input range
    :param max_i: maximum value of input range
    :param min_o: minimum value of output range
    :param max_o: maximum value of output range
    
    :return: mapped number
    """

def intervalChecker(interval:int) -> function:
    """
    Non-blogging interval checker
    
    :param interval: interval in milliseconds
    
    :return: function to check interval
    """

def WDT(timeout:int) -> machine.WDT:
    """
    Watchdog timer
        
    :param timeout: timeout in milliseconds
    """

def i2cdetect(bus:int=1, decorated:bool=True) -> str | list:
    """
    I2C device scanner
    
    :param bus: I2C bus number
    :param decorated: decorated output
    
    :return: I2C devices. 
    If decorated parameter is True, returns a string, otherwise returns a list.
    """
 
class Slip:
    """
    Class that handles SLIP protocol
    """

    @staticmethod
    def decode(chunk: bytes) -> list:
        """
        SLIP decoder. Returns a list of decoded byte strings.
        
        :param chunk: A byte string to decode.
        
        :return: A list of bytes.
        """
        
    @staticmethod
    def encode(payload: bytes) -> bytes:
        """
        SLIP encoder. Returns a byte string.
        
        :param payload: A byte string to encode.
        
        :return: A byte string.
        """
 
class ReplUart:
    """
    Class that handles UART communication
    """
    
    @property
    def timeout(self) -> None | int:
        """
        Get timeout
        
        :return: timeout
        """

    @timeout.setter
    def timeout(self, n:None|int):
        """
        Set timeout
        
        :param n: timeout
        """
        
    def read(self, size:int=1) -> bytes:
        """
        Read data from UART
        
        :param size: number of bytes to read. Default is 1
        
        :return: data
        """
        
    def read_until(self, expected:bytes=b'\n', size:None|int=None) -> bytes:
        """
        Read data from UART until expected data is received
        
        :param expected: expected data
        :param size: number of bytes to read
        
        :return: data
        """
        
    def write(self, data:bytes) -> int:
        """
        Write data to UART
        
        :param data: data to write  
        
        :return: number of bytes written
        """