import enum

# Type1 is a base class with a method
class Type1:
    """ 
    This is a docstring for Type1 class.
    """

    # __init__ is a constructor method
    def __init__(self, value):
        """
        This is a docstring for the __init__ method.
        """
        self.value = value 

    # method1 is a regular method
    def method1(self):
        """
        This is a docstring for method1.
        """
        ...


# Type2 is a subclass of Type1
class Type2(Type1):
    """
    This is a docstring for Type2 class.
    """
    ... 

# Type3 is an enum class
class Type3(enum.Enum):
    """
    This is a docstring for Type3 class.
    """
    TYPE1 = 1
    TYPE2 = 2 
    TYPE3 = 3 


# static_function is a static method
def static_function():
    """
    This is a docstring for static_function.
    """
    ...
