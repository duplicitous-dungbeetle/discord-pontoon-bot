import random


class Player:
    def __init__(self, name, id, total_money, ended=False):
        self.name = name
        self.id = id
        self.total_money = total_money
        self.hands = {}
        self.bets = []
        self.ended = ended
        self.money_change = 0
        self.bet_multipliers = 1
        self.split = False
        self.split_results = [False, False]
        self.split_money_change = [0, 0]
        self.split_bet_multipliers = [1, 1]
        self.doubled = [False, False]
        self.insurance = -1
        self.surrender = False

    def show_hands(self):
        answer = {}
        for hand_index in self.hands:
            actual_hand = self.hands[hand_index]
            hand_answer = []
            for card in actual_hand:
                hand_answer.append(card.card_string)
            answer[hand_index] = hand_answer
        return answer

    def hands_values(self):
        hand_values = []
        for hand_index in self.hands:
            actual_hand = self.hands[hand_index]
            val = 0
            num_of_ace = 0
            for card in actual_hand:
                if card.value == 11:
                    num_of_ace += 1
                val += card.value
            while val > 21 and num_of_ace > 0:
                val -= 10
                num_of_ace -= 1
            hand_values.append(val)
        return hand_values


class Card:
    def __init__(self, card_string, ace_is_one=False):
        self.ace_is_one = ace_is_one
        self.card_string = card_string
        self.suit = card_string.split(" of ")[1]
        self.num = card_string.split(" of ")[0]
        special = ["\u2664", "\u2661", "\u2662", "\u2667"]
        if self.num in ["Jack", "Queen", "King", "Ace"]:
            self.pic = f"{self.num[0]} "
        else:
            self.pic = f"{self.num} "
        if self.suit == "Clubs":
            self.pic += str(special[3])
        elif self.suit == "Hearts":
            self.pic += str(special[1])
        elif self.suit == "Spades":
            self.pic += str(special[0])
        else:
            self.pic += str(special[2])
        if self.num in ["Jack", "Queen", "King"]:
            self.value = 10
        elif self.num == "Ace":
            if self.ace_is_one:
                self.value = 1
            else:
                self.value = 11
        else:
            self.value = int(self.num)

    def __str__(self):
        return self.card_string


class Decks:
    def __init__(self, no_of_decks):
        self.no_of_decks = no_of_decks
        self.deck = []
        suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        nums = ["Ace", 2, 3, 4, 5, 6, 7, 8, 9, "Jack", "Queen", "King"]
        for deck_number in range(self.no_of_decks):
            for suit in suits:
                for num in nums:
                    card_string = f"{num} of {suit}"
                    self.deck.append(Card(card_string))

    def print_no_of_decks(self):
        print(self.no_of_decks)

    def draw_a_card(self):
        random_card = random.choice(self.deck)
        self.deck.remove(random_card)
        return random_card

    def total_no_of_cards(self):
        return len(self.deck)

