class RegisterByte:
    def __init__(self, value, name="Nameless"):
        assert(value <= 0xFF)
        self.value = int(value)
        self.name = name

    def set(self, value):
        assert(value <= 0xFF)
        self.value = int(value) 

    def getName(self):
        return self.name

    def setBit(self, pos, bit):
        """
        >>> a = RegisterFlag(0xFF)
        >>> a.setBit(7, True)
        >>> hex(int(a))
        '0xff'
        >>> a = RegisterFlag(0)
        >>> a.setBit(7, False)
        >>> int(a)
        0
        >>> a = RegisterFlag(0b11111111)
        >>> a.setBit(7, False)
        >>> bin(int(a))
        '0b1111111'
        >>> a = RegisterFlag(0b11011111)
        >>> a.setBit(0, False)
        >>> bin(int(a))
        '0b11011110'
        >>> a = RegisterFlag(0b11000010)
        >>> a.setBit(4, True)
        >>> bin(int(a))
        '0b11010010'
        >>> a = RegisterFlag(0)
        >>> a.setBit(0, True)
        >>> int(a)
        1
        """
        self.value = (self.value & (~(1 << pos))) | (int(bit) << pos)

    def getBit(self, pos):
        """
        >>> a = RegisterFlag(0xff)
        >>> a.getBit(7)
        True
        >>> a = RegisterFlag(0)
        >>> a.getBit(7)
        False
        >>> a = RegisterFlag(0b1111111)
        >>> a.getBit(7)
        False
        >>> a = RegisterFlag(0b11011110)
        >>> a.getBit(0)
        False
        >>> a = RegisterFlag(0b11010010)
        >>> a.getBit(4)
        True
        >>> a = RegisterFlag(1)
        >>> a.getBit(0)
        True
        """
        return bool(self.value & (1 << pos))

    def __add__(self, value):
        if type(value) == RegisterByte:
            return RegisterByte(self.value + int(value))
        return self.value + value

    def __iadd__(self, value):
        self.value += value
        assert(self.value <= 0xFF)
        return self

    def __isub__(self, value):
        self.value -= value
        assert(self.value >= 0)
        return self

    def __eq__(self, value):
        return self.value == value

    def __int__(self):
        return self.value
    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'RegisterByte(' + hex(self.value) + ')'

class RegisterFlag(RegisterByte):
    def set(self, value):
        assert(value < 0xFF)
        self.value = int(value) & 0xFFFF0000 # The lowest four bits should always read zero

    def setZero(self, value):
        self.setBit(7, value)

    def setSubtract(self, value):
        self.setBit(6, value)

    def setHalfCarry(self, value):
        self.setBit(5, value)

    def setCarry(self, value):
        self.setBit(4, value)

    def getZero(self):
        return self.getBit(7)

    def getSubtract(self):
        return self.getBit(6)

    def getHalfCarry(self):
        return self.getBit(5)
        
    def getCarry(self):
        return self.getBit(4)

class RegisterWord:
    def __init__(self, r1, r2, name="Nameless"):
        self.r1 = r1 # Most significant
        self.r2 = r2 # Least significant
        self.name = name

    @classmethod
    def fromValue(cls, value, name="Nameless"):
        """
        >>> RegisterWord.fromValue(0x0)
        RegisterWord(0x0)
        >>> RegisterWord.fromValue(0xf)
        RegisterWord(0xf)
        >>> RegisterWord.fromValue(0xf).r2
        RegisterByte(0xf)
        >>> RegisterWord.fromValue(0xff)
        RegisterWord(0xff)
        >>> RegisterWord.fromValue(0x100)
        RegisterWord(0x100)
        >>> print(RegisterWord.fromValue(555))
        555
        """
        register = cls(RegisterByte(0), RegisterByte(0))
        register.set(value)
        register.name = name
        return register

    def set(self, value):
        self.r1.set(value >> 8)
        self.r2.set(value & 0x00FF)

    def getName(self):
        return self.name

    def __add__(self, value):
        if type(value) == RegisterWord:
            return RegisterWord(int(self) + int(value))
        return int(self) + value

    def __iadd__(self, value):
        self.set(int(self) + value)
        assert(int(self) < 0xFFFF)
        return self

    def __isub__(self, value):
        self.set(int(self) - value)
        assert(int(self) >= 0)
        return self

    def __int__(self):
        return (int(self.r1) << 8) + int(self.r2)

    def __eq__(self, value):
        return int(self) == value
    
    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return 'RegisterWord(' + hex(int(self)) + ')'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
