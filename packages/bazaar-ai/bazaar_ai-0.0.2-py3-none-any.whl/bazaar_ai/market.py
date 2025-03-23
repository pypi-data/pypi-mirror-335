import random
from pieces.coins import Coin, BonusCoin
from pieces.card import Card
from terms import THREE, FOUR, FIVE, TAKE, TRADE, SELL, HERD, ICONS
from copy import deepcopy

# formatting
bold = "\033[1m"
reset = "\033[0m"
fg_white = "\033[38;2;255;255;255m"
bg_black = "\033[48;2;0;0;0m"

class Market:
    def __init__(self, SEED, COIN_STACKS, BONUS_COIN_STACKS, DECK, CAMEL_BONUS):
        # use this for random operations
        self._rng = random.Random(SEED)
        
        self._camel_bonus = CAMEL_BONUS

        self._coin_stack = {}
        self._bonus_stack = {}
        self._deck = []
        self._goods = []
        self._sold_cards = []

        self.setup_coins(COIN_STACKS)
        self.setup_bonus_coins(BONUS_COIN_STACKS)
        self.setup_cards(DECK)
        self.refill_market()
    
    @property
    def camel_bonus(self):
      return self._camel_bonus
      
    @property
    def rng(self):
      return self._rng

    @property
    def coin_stack(self):
      return self._coin_stack

    @property
    def bonus_stack(self):
      return self._bonus_stack

    @property
    def deck(self):
      return self._deck

    @property
    def goods(self):
      return self._goods

    @property
    def sold_cards(self):
      return self._sold_cards

    def observe_market(self):
      goods_copy = self.goods
      coin_stack_copy = deepcopy(self.coin_stack)
      bonus_coins_stack_counts = deepcopy({f"{bonus_type}": len(self.bonus_stack[bonus_type]) for bonus_type in self.bonus_stack.keys()})
      market_observation = MarketObservation(goods_copy, len(self.deck), coin_stack_copy, bonus_coins_stack_counts)
      return market_observation

    def setup_coins(self, COIN_STACKS):
      for good_type, values in COIN_STACKS.items():
        self.coin_stack[good_type] = [Coin(good_type, value) for value in values]

    def setup_bonus_coins(self, BONUS_COIN_STACKS):
      for bonus_type, values in BONUS_COIN_STACKS.items():
        self.bonus_stack[bonus_type] = [BonusCoin(bonus_type, value) for value in values]
        random.shuffle(self.bonus_stack[bonus_type])

    def setup_cards(self, DECK):
      for good_type, count in DECK.items():
        for _ in range(count):
          self.deck.append(Card(good_type))
      # shuffle the deck
      self.rng.shuffle(self.deck)

    def remove_coins(self, good_type, count):
      removed_coins = []
      for i in range(count):
        if len(self.coin_stacks[good_type]) > 0:
          removed_coins.append(self.coin_stacks[good_type].pop())
      return removed_coins

    def apply_action(self, player, action):

        if action.type == TAKE:
            player.hand.append(action.requested)
            self.goods.remove(action.requested)
            self.refill_market()

        if action.type == SELL:
            for card in action.offered:
                player.hand.remove(card)
                self.sold_cards.append(card)
            for card in action.offered:
              if not self.coin_stack[card.good_type]:
                break
              coin = self.coin_stack[card.good_type].pop()
              player.purse.add_coin(coin)
            if len(action.offered) == 3 and self.bonus_stack[THREE]:
              coin = self.bonus_stack[THREE].pop()
              player.purse.add_bonus_coin(coin)
            if len(action.offered) == 4 and self.bonus_stack[FOUR]:
              coin = self.bonus_stack[FOUR].pop()
              player.purse.add_bonus_coin(coin)
            if len(action.offered) == 5 and self.bonus_stack[FIVE]:
              coin = self.bonus_stack[FIVE].pop()
              player.purse.add_bonus_coin(coin)
            self.refill_market()

        if action.type == TRADE:
            for card in action.offered:
                player.hand.remove(card)
                self.goods.append(card)
            for card in action.requested:
                player.hand.append(card)
                self.goods.remove(card)

        if action.type == HERD:
            for card in action.requested:
                self.goods.remove(card)
                player.hand.append(card)
            self.refill_market()

    def refill_market(self):
        while len(self.goods) < 5:
            if self.deck:
                self.goods.append(self.deck.pop())
            else:
                break

    def is_market_closed(self):
      if len(self.goods) < 5 and len(self.deck) == 0:
        return True
      coin_stacks_exhausted_count = sum(len(stack) == 0 for stack in self.coin_stack.values())
      if coin_stacks_exhausted_count >= 3:
        return True
      return False

    def __repr__(self):
        s = f"{bg_black}{fg_white}{bold}Market:{reset}\n"
        s += f"{bold}Goods Left:{reset} " + str(len(self.deck)) + "\n"
        s += f"{bold}Goods:{reset}\n" + str(self.goods) + f"\n{bold}Coins:{reset}\n"
        max_len = max(len(good) for good in self.coin_stack.keys())
        for good_type in self.coin_stack.keys():
            s += f"{ICONS[good_type]}: {self.coin_stack[good_type]}\n"
        s += f"{bold}Bonus Coins:{reset}\n"
        for bonus_type in self.bonus_stack.keys():
            s += f"{ICONS[bonus_type]}: {len(self.bonus_stack[bonus_type])} "
        return s

    def summary(self):
        s = f"{bg_black}{fg_white}{bold}Market:{reset}\n"
        s += f"{bold}Goods Left:{reset} " + str(len(self.deck)) + "\n"
        s += f"{bold}Goods:{reset}\n" + str(self.goods) + f"\n{bold}Coins:{reset}"
        return s
        
class MarketObservation:
    def __init__(self, goods, goods_remaining_count, coins_stack, bonus_coins_stack_counts):
        self._goods = goods
        self._goods_remaining_count = goods_remaining_count
        self._coins_stack = coins_stack
        self._bonus_coins_stack_counts = bonus_coins_stack_counts

    @property
    def goods(self):
      return self._goods

    @property
    def goods_remaining_count(self):
      return self._goods_remaining_count

    @property
    def coins_stack(self):
      return self._coins_stack