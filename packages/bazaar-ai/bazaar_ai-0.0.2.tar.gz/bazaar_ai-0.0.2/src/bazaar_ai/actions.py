class Action:
    pass
    
from itertools import combinations
from terms import TAKE, TRADE, SELL, HERD, DIAMOND, GOLD, SILVER, CAMEL, ICONS

class Herd(Action):
    def __init__(self, requested):
        self.type = HERD
        self._requested = requested

    @property
    def requested(self):
      return self._requested

    def is_legal(self):
        return all(c.good_type == CAMEL for c in self.requested) and len(self.requested) > 0

    def __repr__(self):
        return f"Herd({len(self.requested)}x {ICONS[CAMEL]})"

    @staticmethod
    def get_all_actions(hand, market_observation):
      camels_in_market = [c for c in market_observation.goods if c.good_type == CAMEL]
      if camels_in_market:
          return [Herd(camels_in_market)]
      return []
      
class Sell(Action):
    def __init__(self, offered):
        self.type = SELL
        self._offered = offered

    @property
    def offered(self):
      return self._offered

    def is_legal(self):
        if not self.offered:
            return False
        good = self.offered[0].good_type
        if any(c.good_type != good for c in self.offered):
            return False
        if good == CAMEL:
            return False
        if good in (DIAMOND, GOLD, SILVER) and len(self.offered) < 2:
            return False
        return True

    def __repr__(self):
        return f"Sell({len(self.offered)}x {ICONS[self.offered[0].good_type]})"

    @staticmethod
    def get_all_actions(hand, market_observation):
      actions = []
      goods_by_type = {}
      for card in hand:
          if card.good_type == CAMEL:
              continue
          goods_by_type.setdefault(card.good_type, []).append(card)

      for cards in goods_by_type.values():
          for k in range(1, len(cards) + 1):
              candidate = cards[:k]
              action = Sell(candidate)
              if action.is_legal():
                  actions.append(action)
      return actions
      
class Take(Action):
    def __init__(self, requested):
        self.type = TAKE
        self.requested = requested  # a single non-camel card from market

    def is_legal(self):
        return self.requested.good_type != CAMEL

    @staticmethod
    def get_all_actions(hand, market_observation):
      actions = []
      for card in market_observation.goods:
          action = Take(card)
          if action.is_legal():
              actions.append(action)
      return actions

    def __repr__(self):
        return f"Take({ICONS[self.requested.good_type]})"

class Trade(Action):
    def __init__(self, offered, requested):
        self.type = TRADE
        self._offered = offered
        self._requested = requested

    @property
    def offered(self):
      return self._offered

    @property
    def requested(self):
      return self._requested

    def is_legal(self):
        if not self.offered or not self.requested:
            return False
        if len(self.offered) != len(self.requested):
            return False
        # make sure the trade does not include requesting any camels
        if any(c.good_type == CAMEL for c in self.requested):
            return False
        # make sure none of the types in requested match those in offered
        offered_types = {card.good_type for card in self.offered}
        requested_types = {card.good_type for card in self.requested}
        if not offered_types.isdisjoint(requested_types):
          return False

        return True

    def __repr__(self):
        return f"Trade(offered={self.offered}, requested={self.requested})"

    @staticmethod
    def get_all_actions(hand, market_observation):
      actions = []
      hand_goods = [c for c in hand if c.good_type != CAMEL]
      camels = [c for c in hand if c.good_type == CAMEL]

      max_trade_size = min(len(hand_goods) + len(camels), len(market_observation.goods))
      for size in range(1, max_trade_size + 1):
          requested_combos = list(combinations(market_observation.goods, size))
          offered_pool = hand_goods + camels
          offered_combos = list(combinations(offered_pool, size))

          for offered in offered_combos:
              for requested in requested_combos:
                  action = Trade(list(offered), list(requested))
                  if action.is_legal():
                      actions.append(action)
      return actions