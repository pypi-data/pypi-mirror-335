from terms import ICONS

class Card:
    def __init__(self, good_type):
        self._good_type = good_type

    @property
    def good_type(self):
        return self._good_type

    def as_string(self):
      return f"Card({self.good_type})"

    def __repr__(self):
        return ICONS[self.good_type]