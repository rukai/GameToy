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

    def __add__(self, value):
        if type(value) == RegisterByte:
            return RegisterByte(self.value + int(value))
        return self.value + value

    def __iadd__(self, value):
        self.value += value
        assert(value <= 0xFF)
        return self

    def __eq__(self, value):
        return self.value == value

    def __int__(self):
        return self.value
    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'RegisterByte(' + hex(self.value) + ')'

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
