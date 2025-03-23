class Coin:
    def __init__(self, good_type, value):
      self._good_type = good_type
      self._value = value

    @property
    def good_type(self):
      return self._good_type

    @property
    def value(self):
      return self._value

    def __repr__(self) -> str:
      return f"{self.value}"
      
      
class BonusCoin:
    def __init__(self, bonus_type, value):
      self._bonus_type = bonus_type
      self._value = value

    @property
    def bonus_type(self):
      return self._bonus_type

    @property
    def value(self):
      return self._value

    def __repr__(self) -> str:
      return f"{self.value}"