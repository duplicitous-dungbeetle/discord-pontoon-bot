import discord
from discord.ext import commands
import random
import time
import math
from pontoon_classes import Player, Decks, Card
import os
import json


my_token = "your_discord_bot_token_here"
bot = commands.Bot(command_prefix='!!')
hEmoji = u"\U0001F1ED"
sEmoji = u"\U0001F1F8"
dEmoji = u"\U0001F1E9"
yEmoji = u"\U0001F1FE"
nEmoji = u"\U0001F1F3"
global_pause_time = 1.5
game_queue = []


def name_from_id(id):
    return bot.get_user(id).name


@bot.event
async def on_ready():
    print("Ready!")
    print("-----")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!!help"))


bot.remove_command('help')
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Pontoon Bot", description="Based off the pontoon game in casinoes. List of commands:", color="orange")

    embed.add_field(name="!!help", value="Opens this.", inline=False)
    embed.add_field(name="!!rules", value="How to play Pontoon.", inline=False)
    embed.add_field(name="!!stats", value="To see your current stats.", inline=False)
    embed.add_field(name="!!join", value="Joins/leaves the queue for Pontoon.", inline=False)
    embed.add_field(name="!!check_queue", value="Sees who is in the game queue", inline=False)
    embed.add_field(name="!!start", value="Starts a game of Pontoon.", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def rules(ctx):
    embed = discord.Embed(title="Rules", description="https://www.cra.gov.sg/docs/default-source/game-rule-documents/rws/rws-game-rules---pontoon-v3.pdf", color=0xeee657)
    embed.add_field(name="Game settings", value="6 decks of Spanish playing cards (no 10's)\n"
                                                "Game will use a new deck when less than 1 deck worth of cards left \n"
                                                "Dealer stops drawing on hard 17, soft 18 \n"
                                                "Doubling only permitted if you have 2 cards", inline=False)
    embed.add_field(name="How to Play:", value="Similar to blackjack, put a wager and compete against the dealer to "
                                               "see who can get closer to 21 points, without exceeding 21.\n"
                                               "If you have two cards of the same value, you can split into two "
                                               "separate and independent hands.\n"
                                               "If your hand has two cards, you can choose to 'double', which is to "
                                               "increase your bet amount up to 1x the original and draw just one more card.\n"
                                               "Players take turn to draw cards as they wish, while trying to keep the "
                                               "value of their hand at 21 or below.\n"
                                               "After every player has finished his turn, the dealer draws cards.\n"
                                               "Players win if their card value hasn't bust (exceeded 21) and if their "
                                               "card value is greater than that of the dealer's.", inline=False)
    embed.add_field(name="Insurance", value="If the dealer's first card is an Ace, a player may place an insurance "
                                            "wager, of not more than half his initial wager, that the dealer's second "
                                            "card will have a value of 10. Insurance pays 2 to 1.", inline=False)
    embed.add_field(name="Surrender", value="If the dealer's first card is an Ace or picture card, a player may choose "
                                            "to 'surrender', which is to forfeit half his initial bet, and subsequently"
                                            " no cards will be dealt to him. If the dealer pontoons, the surrender is "
                                            "void and the player loses his entire initial bet.", inline=False)
    embed.add_field(name="Payouts", value="Pontoon (2 cards totaling 21 points) pays 3 to 2\n"
                                                  "5 card 21 pays 3 to 2\n"
                                                  "6 card 21 pays 2 to 1\n"
                                                  "7 cards or more 21 pays 3 to 1\n"
                                                  "6, 7, 8 mixed suits pays 3 to 2\n"
                                                  "6, 7, 8 same suits (except Spades) pays 2 to 1\n"
                                                  "6, 7, 8, all spades pays 3 to 1\n"
                                                  "7, 7, 7 mixed suits pays 3 to 2\n"
                                                  "7, 7, 7 same suit (except Spades) pays 2 to 1\n"
                                                  "7, 7, 7 all spades pays 3 to 1\n"
                                                  "All other winning wagers pays 1 to 1\n"
                                          "**All winning double wagers shall be paid at odds of 1 to 1 and shall not be "
                                          "eligible for payout odds and Super Bonus odds**", inline=False)
    embed.add_field(name="Super Bonus Payout", value="7, 7, 7 same suit and dealer first card 7 (any suit) pays:\n"
                                                     "$1000 if player bet is $5 to $24\n"
                                                     "$5000 if player bet is $25 or greater", inline=False)
    embed.add_field(name="Minimum Wager", value="$5", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def stats(ctx):
    await ctx.send(f"Name: {ctx.message.author.name}")
    await ctx.send(f"ID: {ctx.message.author.id}")
    await ctx.send(f"Full name: {ctx.message.author}")
    with open("records.json", "r") as f:
        records = json.load(f)
    try:
        records[str(ctx.message.author.id)]
    except KeyError:
        await ctx.send(f"{ctx.message.author.name}, you have no record with the bank and hence no money. Start a game of Pontoon to "
                       f"earn $2000 as a welcoming gift!")
    else:
        await ctx.send(f"Money: ${records[str(ctx.message.author.id)][0]}")
        await ctx.send(f"Games Played: {records[str(ctx.message.author.id)][1]}")



@bot.command()
async def join(ctx):
    if ctx.message.author.id not in game_queue:
        game_queue.append(ctx.message.author.id)
        await ctx.send(f"{ctx.message.author.name} has joined the game queue.")
    else:
        game_queue.remove(ctx.message.author.id)
        await ctx.send(f"{ctx.message.author.name} has left the queue.")


@bot.command()
async def check_queue(ctx):
    if len(game_queue) != 0:
        await ctx.send(f"Players in queue:")
        for id in game_queue:
            await ctx.send(f"{name_from_id(id)}")
    else:
        await ctx.send(f"Nobody is in queue.")


@bot.command()
async def start(ctx):

    def results_format(player_class):
        if len(player_class.hands) == 1:
            line1cards = ""
            for card in player_class.hands["hand1"]:
                line1cards += "|" + card.pic + "| "
            line1cards = line1cards[:-1]
            line1space = round((48 - len(line1cards)) / 2)
            line1 = " " * line1space + line1cards

            line2space = round((48 - len(str(player_class.bets[0])) - 3.2 - 2) / 2)
            line2 = f"{' ' * line2space}🏵 {player_class.bets[0]} 🏵"

            line3space = round((48 - len(str(player_class.name))) / 2)
            line3 = " " * line3space + str(player_class.name)

            return "```" + line1 + "\n" + line2 + "\n" + line3 + "```"

        if len(player_class.hands) == 2:
            line1cards = ""
            for card in player_class.hands["hand1"]:
                line1cards += "|" + card.pic + "| "
            line1cards += "   "
            for card in player_class.hands["hand2"]:
                line1cards += "|" + card.pic + "| "
            line1cards = line1cards[:-1]
            line1space = round((48 - len(line1cards)) / 2)
            line1 = " " * line1space + line1cards

            hand1spacediff = 6.6*len(player_class.hands["hand1"]) + 1 - 3.2 - 2 - len(str(player_class.bets[0]))
            hand1leftspace = line1space + hand1spacediff/2

            hand2spacediff = (6.6*len(player_class.hands["hand2"]) + 1) - 3.2 - 2 - len(str(player_class.bets[1]))
            hand2rightspace = line1space + hand2spacediff / 2

            hand1betbit = " " * round(hand1leftspace) + "🏵" + str(player_class.bets[0]) + "🏵"
            hand2betbit = "🏵" + str(player_class.bets[1]) + "🏵" + " " * round(hand2rightspace)
            spaceinbetween = " " * (48 - len(hand1betbit) - len(hand2betbit))
            line2 = hand1betbit + spaceinbetween + hand2betbit

            line3space = round((48 - len(str(player_class.name))) / 2)
            line3 = " " * line3space + str(player_class.name)

            return "```" + line1 + "\n" + line2 + "\n" + line3 + "```"

    def dealer_results_format():
        dealer = f'''

                     __
                   <(o )___
                    ( ._> /
                     `---'
                     DEALER
        '''
        tt = len(dealer_cards)
        totl = 48
        needed = math.ceil(6.6 * tt - 1)
        side = math.floor((totl-needed) / 2)
        sidestring = " " * side
        for card in dealer_cards:
            sidestring += "|" + card.pic + "| "
        sidestring = sidestring[:-1]
        return "```" + dealer + "\n" + sidestring + "```"

    def check_name_and_int(author):
        def inner_check(message):
            try:
                if message.author.name == author and "." not in message.content and int(message.content) >= 0:
                    return True
                else:
                    return False
            except ValueError:
                return False
        return inner_check

    async def delete_multiple_msgs(list_of_msgs):
        for msg in list_of_msgs:
            await discord.Message.delete(msg)

    async def add_multiple_reactions(msg, list_of_reactions):
        for rxn in list_of_reactions:
            await discord.Message.add_reaction(msg, rxn)

    async def clear_multiple_reactions(msg, list_of_reactions):
        for rxn in list_of_reactions:
            await discord.Message.clear_reaction(msg, rxn)

    # Starts game with 6 decks
    decks_number = 6
    apd = Decks(decks_number)
    end_game = False

    # Uncomment to let first player of queue choose how many decks.
    # while True:
    #     await ctx.send(f"{name_from_id(game_queue[0])}, how many decks of cards do you want to use? ")
    #     decks_number_msg_in = await bot.wait_for("message", check=check_name_and_int(name_from_id(game_queue[0])))
    #     decks_number = int(decks_number_msg_in.content)
    #     if decks_number != 0:
    #         apd = Decks(decks_number)
    #         break

    if ctx.message.author.id not in game_queue:
        await ctx.send(f"{ctx.message.author.name}, you are not in the queue. Type !!join to join the queue.")
        end_game = True

    while not end_game and len(game_queue) > 0:
        image = r"""
                      __
                _..-''--'----_.
              ,''.-''| .---/ _`-._
            ,' \ \  ;| | ,/ / `-._`-.
          ,' ,',\ \( | |// /,-._  / /
          ;.`. `,\ \`| |/ / |   )/ /
         / /`_`.\_\ \| /_.-.'-''/ /
        / /_|_:.`. \ |;'`..')  / /
        `-._`-._`.`.;`.\  ,'  / /
            `-._`.`/    ,'-._/ /
              : `-/     \`-.._/
              |  :      ;._ (
              :  |      \  ` \
               \         \   |
                :        :   ;
                |           /
                ;         ,'
               /         /
              /         /
                       /
        """
        await ctx.send("```" + image + "```")

        # holds the class objects for each player
        queueClasses = []

        final_game_queue = game_queue.copy()

        # For player in final queue, give $2000 or retrieve their total money.
        # Also initialise an instance of Player class, append to queueClass
        with open("records.json", "r") as f:
            temp_records = json.load(f)

        for player_id in final_game_queue:
            try:
                temp_records[str(player_id)]
            except KeyError:
                temp_records[str(player_id)] = [2000, 0]
                player_money = 2000
                print(f"{name_from_id(player_id)} given $2000 to start with.")
                await ctx.send(f"{name_from_id(player_id)}, you have been give $2000 to start with.")
            else:
                player_money = int(temp_records[str(player_id)][0])
                if player_money == 0:
                    print(f"{name_from_id(player_id)} bankrupt.")
                    await ctx.send(f"{name_from_id(player_id)}, you are bankrupt. Here's another $2000...")
                    temp_records[str(player_id)][0] = 2000
                    player_money = 2000

            a_player = Player(name_from_id(player_id), player_id, player_money)
            queueClasses.append(a_player)
            print(f"{name_from_id(player_id)} initialised as Player class.")
            await ctx.send(f"**{name_from_id(player_id)}**, you have **${player_money}**.")

        #  Will reset decks when less than 1 deck worth of cards left
        if decks_number > 1:
            if len(apd.deck) < 48:
                await ctx.send("Less than 48 cards in the deck now.")
                apd = Decks(decks_number)
                await ctx.send(f"Retrieving new decks...")
                time.sleep(global_pause_time)
        else:  # if 1 deck used
            if len(apd.deck) < 13:  # arbitrary
                await ctx.send("Less than 13 cards in the deck now.")
                apd = Decks(1)
                await ctx.send(f"Retrieving new deck...")
                time.sleep(global_pause_time)

        # Gets the bet of each player
        for player_class in queueClasses:
            player_name = player_class.name
            while len(player_class.bets) == 0 or player_class.bets[0] > player_class.total_money:

                prompt_amount_msg_out = await ctx.send(f"**{player_name}**, how much do you want to bet? Minimum wager is $5, please enter an integer.")
                bet_amount_msg_in = await bot.wait_for("message", check=check_name_and_int(player_name))
                print(f"Asked {player_name} for bet amount")
                try:
                    int(bet_amount_msg_in.content)
                except ValueError:
                    pass
                else:
                    if int(bet_amount_msg_in.content) < 5:
                        await ctx.send(f"**{player_name}**, minimum wager is $5.")
                    if player_class.total_money >= int(bet_amount_msg_in.content) >= 5:
                        player_class.bets.append(int(bet_amount_msg_in.content))
                        print(f"{player_name} has bet ${int(bet_amount_msg_in.content)}.")
                        await ctx.send(f"**{player_name}** has bet **${int(bet_amount_msg_in.content)}**.")
                        await delete_multiple_msgs([bet_amount_msg_in, prompt_amount_msg_out])

        await ctx.send("Dealing cards...")
        time.sleep(global_pause_time)

        # Deals 1 card to each player
        for player_class in queueClasses:
            player_name = player_class.name
            player_class.hands["hand1"] = []
            first_card = apd.draw_a_card()
            player_class.hands["hand1"].append(first_card)
            await ctx.send(results_format(player_class))
            time.sleep(global_pause_time)
        print("Dealt 1 card to all players")

        dealer_cards = []
        dealer_value = 0

        # Deals 1 card to dealer
        dealer_card_1 = apd.draw_a_card()
        dealer_cards.append(dealer_card_1)
        dealer_value += dealer_card_1.value
        await ctx.send(dealer_results_format())
        if dealer_card_1.num == "Ace":
            await ctx.send("Dealer draws an Ace, players can buy insurance or surrender.")
        if dealer_card_1.value == 10:
            await ctx.send(f"Dealer draws a {dealer_card_1.num}, players can surrender.")
        time.sleep(global_pause_time)
        print("Dealt one card to dealer")

        # Deals second card to each player
        for player_class in queueClasses:
            player_name = player_class.name
            second_card = apd.draw_a_card()
            player_class.hands["hand1"].append(second_card)
            await ctx.send(results_format(player_class))
            time.sleep(global_pause_time)

            if dealer_card_1.num == "Ace":
                prompt_insurance_msg_out = await ctx.send(f"**{player_name}**, do you want to buy insurance? Type 0 if you don't. Maximum insurance is half your bet amount, which is half of {player_class.bets[0]}.")
                insurance_amount_msg_in = await bot.wait_for("message", check=check_name_and_int(player_name))
                print(f"Asked {player_name} for insurance")
                while player_class.insurance < 0:
                    try:
                        int(insurance_amount_msg_in.content)
                    except ValueError:
                        pass
                    else:
                        if int(insurance_amount_msg_in.content) > player_class.bets[0] / 2:
                            await ctx.send(f"Cannot bet more than half your initial bet amount.")
                            await delete_multiple_msgs([insurance_amount_msg_in, prompt_insurance_msg_out])
                        else:
                            player_class.insurance = int(insurance_amount_msg_in.content)
                            await delete_multiple_msgs([insurance_amount_msg_in, prompt_insurance_msg_out])

            if dealer_card_1.num == "Ace" or dealer_card_1.value == 10:
                prompt_surrender_msg_out = await ctx.send(f"**{player_name}**, do you want to surrender (and give up half your bet)?")
                await add_multiple_reactions(prompt_surrender_msg_out, [yEmoji, nEmoji])
                surrenderreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                while str(surrenderreaction) not in [yEmoji, nEmoji]:
                    surrenderreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                    time.sleep(global_pause_time)

                # Continue
                if str(surrenderreaction) == yEmoji:
                    await ctx.send(f"{player_name} surrenders.")
                    await clear_multiple_reactions(prompt_surrender_msg_out, [yEmoji, nEmoji])
                    player_class.surrender = True
                    player_class.ended = True
                    time.sleep(global_pause_time)
                    print(f"{player_name} surrenders")

                if str(surrenderreaction) == nEmoji:
                    await ctx.send(f"{player_name} doesn't surrender.")
                    await clear_multiple_reactions(prompt_surrender_msg_out, [yEmoji, nEmoji])
                    time.sleep(global_pause_time)
                    print(f"{player_name} doesn't surrender'.")

        print("Dealt second card to each player")

        # Checks if anyone pontoons
        for player_class in queueClasses:
            if not player_class.ended:
                player_name = player_class.name
                if player_class.hands["hand1"][0].num + player_class.hands["hand1"][1].num == 21:
                    await ctx.send(results_format(player_class))
                    await ctx.send(f"**{player_name}** pontoons!")
                    await ctx.send(f"**{player_name}** won **${player_class.bets[0]}** with payout odds 3 to 2!")
                    player_class.ended = True
                    player_class.bet_multipliers = 1.5
                    player_class.money_change = player_class.bets[0] * player_class.bet_multipliers
                    print(f"{player_name} immediately 21. ")

        print("Finished checking if anyone immediately pontoons")

        # Now, every player takes turns to do their actions
        for player_class in queueClasses:
            if not player_class.ended:
                player_name = player_class.name

                # If the player's first (and only) hand's 1st and 2nd card have the same value, offer the split option
                if player_class.hands["hand1"][0].num == player_class.hands["hand1"][1].num:
                    split_decision_msg_out = await ctx.send(f"**{player_name}**, do you want to split?")
                    await add_multiple_reactions(split_decision_msg_out, [yEmoji, nEmoji])
                    splitornosplitreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                    print(f"{player_name} can split")

                    while str(splitornosplitreaction) not in [yEmoji, nEmoji]:
                        splitornosplitreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                        time.sleep(global_pause_time)

                    if str(splitornosplitreaction) == yEmoji:  # if split
                        await clear_multiple_reactions(split_decision_msg_out, [yEmoji, nEmoji])
                        await ctx.send(f"**{player_name}** splits!")
                        print(f"{player_name} splits")

                        # The magical split
                        player_class.split = True
                        player_class.hands["hand2"] = [player_class.hands["hand1"][1]]
                        del player_class.hands["hand1"][1]
                        if player_class.bets[0] * 2 > player_class.total_money:
                            await ctx.send(f"**{player_name}**, you do not have enough money to bet ${player_class.bets[0]} on each split. Betting ${0.5* player_class.bets[0]} on each split.")
                            player_class.bets[0] = 0.5 * player_class.bets[0]
                            player_class.bets.append(player_class.bets[0])
                        else:
                            player_class.bets.append(player_class.bets[0])

                        time.sleep(global_pause_time)

                        for i in range(len(player_class.hands)):
                            if i == 0:
                                aa = "first"
                            if i == 1:
                                aa = "second"
                            hand_name = "hand" + str(i+1)  # hand1 or hand2
                            split_second_card = apd.draw_a_card()
                            player_class.hands[hand_name].append(split_second_card)
                            await ctx.send(results_format(player_class))
                            time.sleep(global_pause_time)

                            if player_class.hands_values()[i] == 21:  # Pontoon, 2 cards
                                await ctx.send(f"**{player_name}** got 21 on his {aa} split!")
                                await ctx.send(f"**{player_name}** won ${player_class.bets[i]}!")
                                player_class.split_results[i] = True
                                player_class.split_bet_multipliers[i] = 1
                                player_class.split_money_change[i] = player_class.bets[i] * player_class.split_bet_multipliers[i]
                                print(f"{player_name}'s {aa} split immediately 21, not counted as pontoon. ")

                            if player_class.hands_values()[i] != 21:
                                if player_class.hands[hand_name][0].num == "Ace" or player_class.hands[hand_name][1].num == "Ace":
                                    split_hsd_message_out = await ctx.send(f"**{player_name}**, for your {aa} split, hit, stand or double?\n "
                                        f"Note that an Ace in the initial point total of any double shall have a value of one and not eleven\n"
                                                                       f"If doubling with two Aces in the initial deal, point total is 2 not 12.")

                                else:
                                    if player_class.hands_values()[i] >= 12:
                                        split_hsd_message_out = await ctx.send(f"**{player_name}**, for your {aa} split, hit, stand or double?\n")
                                        await add_multiple_reactions(split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                                    else:
                                        split_hsd_message_out = await ctx.send(f"**{player_name}**, for your {aa} split, hit or double?\n")
                                        await add_multiple_reactions(split_hsd_message_out, [hEmoji, dEmoji])

                                splithsdreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                                while str(splithsdreaction) not in [hEmoji, sEmoji, dEmoji]:
                                    splithsdreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                                    time.sleep(global_pause_time)

                                # After 2 cards, hit to ask for 3rd card
                                if str(splithsdreaction) == hEmoji:
                                    await clear_multiple_reactions(split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                                    await ctx.send(f"**{player_name}** hits.")
                                    print(f"{player_name}'s {aa} split hits for 3rd card")

                                    third_card = apd.draw_a_card()
                                    player_class.hands[hand_name].append(third_card)
                                    await ctx.send(dealer_results_format())
                                    await ctx.send(results_format(player_class))
                                    time.sleep(global_pause_time)

                                    # While player's xth hand hasn't bust, after having 3 cards
                                    while player_class.hands_values()[i] < 21:
                                        print(f"{player_name}'s {aa} split has 3 or more cards, hasn't bust, hit/stand")

                                        # Offer hit or stand only if > 11
                                        if player_class.hands_values()[i] > 11:
                                            split_hs_decision_message_out = await ctx.send(f"**{player_name}**, for your {aa} split, hit or stand?")
                                            await add_multiple_reactions(split_hs_decision_message_out, [hEmoji, sEmoji])
                                            splithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                                        else:
                                            split_hs_decision_message_out = await ctx.send(f"**{player_name}**, for your {aa} split, you can only hit since your hand value hasn't reached 12.")
                                            await discord.Message.add_reaction(split_hs_decision_message_out, hEmoji)
                                            splithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                                        while str(splithsreaction) not in [hEmoji, sEmoji]:
                                            splithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                                            time.sleep(global_pause_time)

                                        # If hit
                                        if str(splithsreaction) == hEmoji:
                                            await clear_multiple_reactions(split_hs_decision_message_out, [hEmoji, sEmoji])
                                            await ctx.send(f"**{player_name}** hits.")
                                            time.sleep(global_pause_time)

                                            # Draw a further card
                                            further_card = apd.draw_a_card()
                                            player_class.hands[hand_name].append(further_card)
                                            await ctx.send(dealer_results_format())
                                            await ctx.send(results_format(player_class))
                                            time.sleep(global_pause_time)
                                            print(f"{player_name}'s {aa} split has 3 or more cards, hasn't bust, hit")

                                        # If stand
                                        if str(splithsreaction) == sEmoji:
                                            await clear_multiple_reactions(split_hs_decision_message_out, [hEmoji, sEmoji])
                                            await ctx.send(f"**{player_name}** stands.")
                                            time.sleep(global_pause_time)
                                            print(f"{player_name}'s {aa} split has 3 or more cards, hasn't bust, stand")
                                            break

                                # After 2 cards, stand and don't get a 3rd card
                                if str(splithsdreaction) == sEmoji:
                                    await clear_multiple_reactions(split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                                    await ctx.send(f"**{player_name}** stands.")
                                    time.sleep(global_pause_time)
                                    print(f"{player_name}'s {aa} split stands, doesn't get 3rd card")

                                # After 2 cards, double and get a 3rd and final card
                                if str(splithsdreaction) == dEmoji:
                                    await clear_multiple_reactions(split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                                    await ctx.send(f"**{player_name}** doubles.")
                                    time.sleep(global_pause_time)
                                    print(f"{player_name}'s {aa} split doubles for 3rd and last card")

                                    while True:
                                        split_double_message_out = await ctx.send(f"**{player_name}**, how much more do you wish to wager? Maximum is your current bet amount of {player_class.bets[i]}")
                                        split_double_amount_message_in = await bot.wait_for("message", check=check_name_and_int(player_name))
                                        print(f"Asked {player_name} for double amount")
                                        try:
                                            int(split_double_amount_message_in.content)
                                        except ValueError:
                                            pass
                                        else:
                                            if int(split_double_amount_message_in.content) > player_class.bets[i] \
                                                    or int(split_double_amount_message_in.content) < 0:
                                                await ctx.send(f"Please key in a valid amount.")
                                                await delete_multiple_msgs([split_double_amount_message_in, split_double_message_out])
                                            elif (int(split_double_amount_message_in.content) + player_class.bets[0]
                                                  + player_class.bets[1]) > player_class.total_money:
                                                await ctx.send(f"You don't have enough money to wager an additional ${int(split_double_amount_message_in.content)}. Remember how much money you have!")
                                                await delete_multiple_msgs([split_double_amount_message_in, split_double_message_out])
                                            else:
                                                player_class.bets[i] += int(split_double_amount_message_in.content)
                                                player_class.doubled[i] = True
                                                await delete_multiple_msgs([split_double_amount_message_in, split_double_message_out])
                                                break

                                    # If aces in play, their value is 1 not 11
                                    for card in player_class.hands[hand_name]:
                                        if card.value == 11:
                                            card.ace_is_one = True

                                    # Draw 3rd and last card
                                    third_doubled_card = apd.draw_a_card()
                                    player_class.hands[hand_name].append(third_doubled_card)
                                    await ctx.send(dealer_results_format())
                                    await ctx.send(results_format(player_class))
                                    time.sleep(global_pause_time)

                                print(f"{player_name}'s {aa} split, after hit, stand or double")
                                # After hit, stand, or double, if busted
                                if player_class.hands_values()[i] > 21:
                                    await ctx.send(f"**{player_name}** busted!")
                                    await ctx.send(f"**{player_name}** lost ${player_class.bets[i]}")
                                    player_class.split_results[i] = True
                                    player_class.split_money_change[i] = 0 - player_class.bets[i]
                                    print(f"{player_name}'s {aa} split busted")

                                # After hit, stand, or double, if 21

                                # Now player_class.hands looks like this
                                # {'hand1': [<__main__.Card object at 0x03903C28>], 'hand2': [<__main__.Card object
                                # at 0x03912748>]}
                                # Doing player_class.show_hands() gets this
                                # {'hand1': ['King of Hearts'], 'hand2': ['9 of Diamonds']}
                                if player_class.hands_values()[i] == 21 and not player_class.doubled[i]:
                                    split_special_payout = False
                                    split_super_bonus_payout = False

                                    if len(player_class.hands[hand_name]) == 5:
                                        # 5 cards 3 to 2
                                        await ctx.send(f"**{player_name}** has hit 21 with 5 cards on his {aa} split!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 2!")
                                        player_class.split_bet_multipliers[i] = 1.5
                                        print(f"{player_name}'s {aa} split got 21 on 5, payout 3 to 2")
                                        split_special_payout = True

                                    if len(player_class.hands[hand_name]) == 6:
                                        # 6 cards 2 to 1
                                        await ctx.send(f"**{player_name}** has hit 21 with 6 cards on his {aa} split!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 2 to 1!")
                                        player_class.split_bet_multipliers[i] = 2
                                        print(f"{player_name}'s {aa} split got 21 on 6, payout 2 to 1")
                                        split_special_payout = True

                                    if len(player_class.hands[hand_name]) >= 7:
                                        # 7 or more cards 3 to 1
                                        await ctx.send(f"**{player_name}** has hit 21 with 7 or more cards on his {aa} split!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 1!")
                                        player_class.split_bet_multipliers[i] = 3
                                        print(f"{player_name}'s {aa} split got 21 on 7 or more, payout 3 to 1")
                                        split_special_payout = True

                                    if len(player_class.hands[hand_name]) == 3:
                                        values = []
                                        suits = []
                                        for card in player_class.hands[hand_name]:
                                            values.append(card.value)
                                            suits.append(card.suit)

                                        if 6 in values and 7 in values and 8 in values:

                                            if suits[0] != suits[1] and suits[0] != suits[2] and suits[1] != suits[2]:
                                                # 6 7 8 mixed suits 3 to 2
                                                await ctx.send(f"**{player_name}** has hit 21 with mixed 6-7-8 on his {aa} split!")
                                                await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 2!")
                                                player_class.split_bet_multipliers[i] = 1.5
                                                print(f"{player_name}'s {aa} split got 21 with mixed 6-7-8, payout 3 to 2")
                                                split_special_payout = True

                                            if suits[0] == suits[1] and suits[0] == suits[2] and suits[1] == suits[2]:
                                                # 6 7 8 same suit
                                                if suits[0] in ["Clubs", "Hearts", "Diamonds"]:  # non spades 2 to 1
                                                    await ctx.send(f"**{player_name}** has hit 21 with 6-7-8 {suits[0]} on his {aa} split!")
                                                    await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 2 to 1!")
                                                    player_class.split_bet_multipliers[i] = 2
                                                    print(f"{player_name}'s {aa} split got 21 with non-spades same-suited {(suits[0])} 6-7-8, payout 2 to 1")
                                                    split_special_payout = True

                                                if suits[0] == "Spades":  # spades 3 to 1
                                                    await ctx.send(f"**{player_name}** has hit 21 with 6-7-8 {suits[0]} on his {aa} split!")
                                                    await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 1!")
                                                    player_class.split_bet_multipliers[i] = 3
                                                    print(f"{player_name}'s {aa} split got 21 with non-spades same-suited {(suits[0])} 6-7-8, payout 3 to 1")
                                                    split_special_payout = True

                                        if values[0] == values[1] and values[1] == values[2] and values[0] == values[2]:
                                            if values[0] == 7:  #extra checks to make sure triple 7

                                                if suits[0] != suits[1] and suits[0] != suits[2] and suits[1] != suits[2]:
                                                    # 7 7 7 mixed suits 3 to 2
                                                    await ctx.send(f"**{player_name}** has hit 21 with mixed 7-7-7 on his {aa} split!")
                                                    await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 2!")
                                                    player_class.split_bet_multipliers[i] = 1.5
                                                    print(f"{player_name}'s {aa} split got 21 with mixed 7-7-7, payout 3 to 2")
                                                    split_special_payout = True

                                                if suits[0] == suits[1] and suits[0] == suits[2] and suits[1] == suits[2]:
                                                    # 7 7 7 same suit
                                                    if suits[0] in ["Clubs", "Hearts", "Diamonds"]:  # non spades 2 to 1

                                                        if dealer_card_1.value != 7:
                                                            await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} on his {aa} split!")
                                                            await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 2 to 1!")
                                                            player_class.split_bet_multipliers[i] = 2
                                                            print(f"{player_name}'s {aa} split got 21 with non-spades same-suited {(suits[0])} 7-7-7, payout 2 to 1")
                                                            split_special_payout = True

                                                        if dealer_card_1.value == 7:  # Super bonus 777 same suit, dealer 7
                                                            # if player bet $5-$24, pays 1000, $25 onwards pays 5000
                                                            await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} on his {aa} split AND DEALER HAS 7!")
                                                            if 5 <= player_class.bets[i] <= 24:
                                                                await ctx.send(f"**{player_name}** won $1000!")
                                                                print(f"{player_name}'s {aa} split 777 with dealer 7, pays 1000 cos bet of {player_class.bets[i]} between 5 and 24")
                                                                split_special_payout = True
                                                                player_class.split_money_change[i] = 1000
                                                                split_super_bonus_payout = True

                                                            if player_class.bets[i] >= 25:
                                                                await ctx.send(f"**{player_name}** won $5000!")
                                                                print(f"{player_name}'s {aa} split 777 with dealer 7, pays 5000 cos bet of {player_class.bets[i]} between 5 and 24")
                                                                split_special_payout = True
                                                                player_class.split_money_change[i] = 1000
                                                                split_super_bonus_payout = True

                                                    if suits[0] == "Spades":  # spades 3 to 1
                                                        if dealer_card_1.value != 7:
                                                            await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} on his {aa} split!")
                                                            await ctx.send(f"**{player_name}** won ${player_class.bets[i]}, with payout odds 3 to 1!")
                                                            player_class.split_bet_multipliers[i] = 3
                                                            print(f"{player_name}'s {aa} split got 21 with non-spades same-suited {(suits[0])} 7-7-7, payout 3 to 1")
                                                            split_special_payout = True

                                                        if dealer_card_1.value == 7:  # Super bonus 777 same suit,
                                                            # dealer 7
                                                            # if player bet $5-$24, pays 1000, $25 onwards pays 5000
                                                            await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} on his {aa} split AND DEALER HAS 7!")
                                                            if 5 <= player_class.bets[i] <= 24:
                                                                await ctx.send(f"**{player_name}** won $1000!")
                                                                print(f"{player_name}'s {aa} split 777 with dealer 7, pays 1000 cos bet of {player_class.bets[i]} between 5 and 24")
                                                                split_special_payout = True
                                                                player_class.split_money_change[i] = 1000
                                                                split_super_bonus_payout = True

                                                            if player_class.bets[i] >= 25:
                                                                await ctx.send(f"**{player_name}** won $5000!")
                                                                print(
                                                                    f"{player_name}'s {aa} split 777 with dealer 7, "
                                                                    f"pays 5000 cos bet of {player_class.bets[i]} "
                                                                    f"between 5 and 24")
                                                                split_special_payout = True
                                                                player_class.split_money_change[i] = 1000
                                                                split_super_bonus_payout = True

                                    if not split_special_payout:
                                        await ctx.send(f"**{player_name}** has hit 21 on his {aa} split!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[i]}.")
                                        print(f"{player_name}'s {aa} split got 21, no special payout.")

                                    player_class.split_results[i] = True
                                    if not split_super_bonus_payout:
                                        player_class.split_money_change[i] = player_class.bets[i] * player_class.split_bet_multipliers[i]

                    if str(splitornosplitreaction) == nEmoji:  # if no split, break
                        await clear_multiple_reactions(split_decision_msg_out, [yEmoji, nEmoji])
                        await ctx.send(f"**{player_name}** doesn't split.")
                        print(f"{player_name} doesn't split")
                        time.sleep(global_pause_time)

                if player_class.split:
                    break

                print("Code runs here if player didn't split")
                # If first two cards hit 21
                if player_class.hands_values()[0] == 21:
                    await ctx.send(f"**{player_name}** pontoons!")
                    await ctx.send("--------------------------------------------------------------")
                    await ctx.send(results_format(player_class))
                    await ctx.send(f"**{player_name}** won ${player_class.bets[0]} with payout odds 3 to 2!")
                    player_class.ended = True
                    player_class.bet_multipliers = 1.5
                    player_class.money_change = player_class.bets[0] * player_class.bet_multipliers
                    print(f"{player_name} immediately 21. ")

                # If cannot split or no split, offer hit, stand or double
                if player_class.hands_values()[0] != 21:
                    print(f"{player_name} didn't get 21 immediately, offering HSD")
                    await ctx.send("--------------------------------------------------------------")
                    await ctx.send(dealer_results_format())
                    await ctx.send(results_format(player_class))

                    if player_class.hands["hand1"][0].num == "Ace" or player_class.hands["hand1"][1].num == "Ace":
                        no_split_hsd_message_out = await ctx.send(
                            f"**{player_name}**, hit, stand or double?\n "
                            f"Note that an Ace in the initial point total of "
                            f"any double shall have a value of one and not eleven\n"
                            f"If doubling with two Aces in the initial deal, point total is 2 not 12.")
                        await add_multiple_reactions(no_split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                    else:
                        if player_class.hands_values()[0] >= 12:
                            no_split_hsd_message_out = await ctx.send(f"**{player_name}**, hit, stand or double?\n")
                            await add_multiple_reactions(no_split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                        else:
                            no_split_hsd_message_out = await ctx.send(f"**{player_name}**, hit or double?\n")
                            await add_multiple_reactions(no_split_hsd_message_out, [hEmoji, dEmoji])

                    nosplithsdreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                    print(f"{player_name} didn't get 21 immediately, offered HSD")
                    while str(nosplithsdreaction) not in [hEmoji, sEmoji, dEmoji]:
                        nosplithsdreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                        time.sleep(global_pause_time)

                    # After 2 cards, hit to ask for 3rd card
                    if str(nosplithsdreaction) == hEmoji:
                        await clear_multiple_reactions(no_split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                        await ctx.send(f"**{player_name}** hits.")
                        print(f"{player_name} hits for HSD")

                        third_card = apd.draw_a_card()
                        player_class.hands["hand1"].append(third_card)
                        await ctx.send("--------------------------------------------------------------")
                        await ctx.send(dealer_results_format())
                        await ctx.send(results_format(player_class))
                        time.sleep(global_pause_time)
                        print(f"{player_name} hits for HSD, draws card 3")

                        # While player's first (and only) hand hasn't bust, after having 3 cards
                        while player_class.hands_values()[0] < 21:

                            print(f"**{player_name}** hits for HSD, draws card 3, didn't bust, hit/stand for card 4 onwards.")

                            # Offer hit or stand only if > 12
                            if player_class.hands_values()[0] > 11:
                                no_split_hs_decision_message_out = await ctx.send(f"**{player_name}**, hit or stand?")
                                await add_multiple_reactions(no_split_hs_decision_message_out, [hEmoji, sEmoji])
                                nosplithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                            else:
                                no_split_hs_decision_message_out = await ctx.send(f"**{player_name}**, you can only hit since your hand value hasn't reached 12.")
                                await discord.Message.add_reaction(no_split_hs_decision_message_out, hEmoji)
                                nosplithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

                            while str(nosplithsreaction) not in [hEmoji, sEmoji]:
                                nosplithsreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                                time.sleep(global_pause_time)

                            # If hit
                            if str(nosplithsreaction) == hEmoji:
                                await clear_multiple_reactions(no_split_hs_decision_message_out, [hEmoji, sEmoji])
                                await ctx.send(f"**{player_name}** hits.")
                                time.sleep(global_pause_time)
                                print(f"{player_name} hits for HSD, draws card 3, didn't bust, hits for card 4 onwards.")

                                # Draw a further card
                                further_card = apd.draw_a_card()
                                player_class.hands["hand1"].append(further_card)
                                await ctx.send("--------------------------------------------------------------")
                                await ctx.send(dealer_results_format())
                                await ctx.send(results_format(player_class))
                                time.sleep(global_pause_time)

                            # If stand
                            if str(nosplithsreaction) == sEmoji:
                                await clear_multiple_reactions(no_split_hs_decision_message_out, [hEmoji, sEmoji])
                                await ctx.send(f"{player_name} stands.")
                                time.sleep(global_pause_time)
                                print(f"{player_name} hits for HSD, draws card 3, didn't bust, stands for card 4 onwards.")
                                break

                    # After 2 cards, stand and don't get a 3rd card
                    if str(nosplithsdreaction) == sEmoji:
                        await clear_multiple_reactions(no_split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                        await ctx.send(f"{player_name} stands.")
                        time.sleep(global_pause_time)
                        print(f"{player_name} stands for HSD")

                    # After 2 cards, double and get a 3rd and final card
                    if str(nosplithsdreaction) == dEmoji:
                        await clear_multiple_reactions(no_split_hsd_message_out, [hEmoji, sEmoji, dEmoji])
                        await ctx.send(f"{player_name} doubles.")
                        time.sleep(global_pause_time)
                        print(f"{player_name} doubles for HSD")

                        while True:
                            double_message_out = await ctx.send(f"**{player_name}**, how much more do you wish to wager? Maximum is your current bet amount of {player_class.bets[0]}")
                            double_amount_message_in = await bot.wait_for("message", check=check_name_and_int(player_name))
                            print(f"Asked {player_name} for double amount")
                            try:
                                int(double_amount_message_in.content)
                            except ValueError:
                                pass
                            else:
                                if int(double_amount_message_in.content) > player_class.bets[0] \
                                        or int(double_amount_message_in.content) < 0:
                                    await ctx.send(f"Please key in a valid amount.")
                                    await delete_multiple_msgs([double_amount_message_in, double_message_out])
                                elif int(double_amount_message_in.content) + player_class.bets[0] > player_class.total_money:
                                    await ctx.send(f"You don't have enough money to wager an additional {int(double_amount_message_in.content)}. Remember how much money you have!")
                                    await delete_multiple_msgs([double_amount_message_in, double_message_out])
                                else:
                                    player_class.bets[0] += int(double_amount_message_in.content)
                                    player_class.doubled[0] = True
                                    await delete_multiple_msgs([double_amount_message_in, double_message_out])
                                    break

                        # If aces in play, their value is 1 not 11
                        for card in player_class.hands["hand1"]:
                            if card.value == 11:
                                card.ace_is_one = True

                        # Draw 3rd and last card
                        third_doubled_card = apd.draw_a_card()
                        player_class.hands["hand1"].append(third_doubled_card)
                        await ctx.send("--------------------------------------------------------------")
                        await ctx.send(dealer_results_format())
                        await ctx.send(results_format(player_class))
                        time.sleep(global_pause_time)
                        print(f"{player_name} doubles for HSD and got his card")

                    # After hit, stand, or double, if busted
                    if player_class.hands_values()[0] > 21:
                        await ctx.send(f"**{player_name}** busted!")
                        await ctx.send(f"**{player_name}** lost ${player_class.bets[0]}")
                        player_class.ended = True
                        player_class.money_change = 0-player_class.bets[0]
                        print(f"{player_name} busted after HSD")

                    # After hit, stand, or double, if 21
                    if player_class.hands_values()[0] == 21:
                        await ctx.send(f"**{player_name}** has hit 21!")
                        await ctx.send(f"**{player_name}** won ${player_class.bets[0]}")
                        player_class.ended = True
                        player_class.money_change = player_class.bets[0]
                        print(f"{player_name} got 21 after HSD")

                    # After hit, stand, or double, if 21

                    # Now player_class.hands looks like this
                    # {'hand1': [<__main__.Card object at 0x03903C28>], 'hand2': [<__main__.Card object
                    # at 0x03912748>]}
                    # Doing player_class.show_hands() gets this
                    # {'hand1': ['King of Hearts'], 'hand2': ['9 of Diamonds']}
                    if player_class.hands_values()[0] == 21 and not player_class.doubled[0]:
                        special_payout = False
                        super_bonus_payout = False

                        if len(player_class.hands["hand1"]) == 5:
                            # 5 cards 3 to 2
                            await ctx.send(f"**{player_name}** has hit 21 with 5 cards!")
                            await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 2!")
                            player_class.bet_multipliers = 1.5
                            print(f"{player_name} got 21 on 5, payout 3 to 2")
                            special_payout = True

                        if len(player_class.hands["hand1"]) == 6:
                            # 6 cards 2 to 1
                            await ctx.send(f"**{player_name}** has hit 21 with 6 cards!")
                            await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 2 to 1!")
                            player_class.bet_multipliers = 2
                            print(f"{player_name} got 21 on 6, payout 2 to 1")
                            special_payout = True

                        if len(player_class.hands["hand1"]) >= 7:
                            # 7 or more cards 3 to 1
                            await ctx.send(f"**{player_name}** has hit 21 with 7 or more cards!")
                            await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 1!")
                            player_class.bet_multipliers = 3
                            print(f"{player_name} got 21 on 7 or more, payout 3 to 1")
                            special_payout = True

                        if len(player_class.hands["hand1"]) == 3:
                            values = []
                            suits = []
                            for card in player_class.hands["hand1"]:
                                values.append(card.value)
                                suits.append(card.suit)

                            if 6 in values and 7 in values and 8 in values:

                                if suits[0] != suits[1] and suits[0] != suits[2] and suits[1] != suits[2]:
                                    # 6 7 8 mixed suits 3 to 2
                                    await ctx.send(f"**{player_name}** has hit 21 with mixed 6-7-8!")
                                    await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 2!")
                                    player_class.bet_multipliers = 1.5
                                    print(f"{player_name} got 21 with mixed 6-7-8, payout 3 to 2")
                                    special_payout = True

                                if suits[0] == suits[1] and suits[0] == suits[2] and suits[1] == suits[2]:
                                    # 6 7 8 same suit
                                    if suits[0] in ["Clubs", "Hearts", "Diamonds"]:  # non spades 2 to 1
                                        await ctx.send(f"**{player_name}** has hit 21 with 6-7-8 {suits[0]}!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 2 to 1!")
                                        player_class.bet_multipliers = 2
                                        print(f"{player_name} got 21 with non-spades same-suited {(suits[0])} 6-7-8, payout 2 to 1")
                                        special_payout = True

                                    if suits[0] == "Spades":  # spades 3 to 1
                                        await ctx.send(f"**{player_name}** has hit 21 with 6-7-8 {suits[0]}!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 1!")
                                        player_class.bet_multipliers = 3
                                        print(f"{player_name} got 21 with non-spades same-suited {(suits[0])} 6-7-8, payout 3 to 1")
                                        special_payout = True

                            if values[0] == values[1] and values[1] == values[2] and values[0] == values[2]:
                                if values[0] == 7:  # extra checks to make sure triple 7

                                    if suits[0] != suits[1] and suits[0] != suits[2] and suits[1] != suits[2]:
                                        # 7 7 7 mixed suits 3 to 2
                                        await ctx.send(f"**{player_name}** has hit 21 with mixed 7-7-7!")
                                        await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 2!")
                                        player_class.bet_multipliers = 1.5
                                        print(f"{player_name} got 21 with mixed 7-7-7, payout 3 to 2")
                                        special_payout = True

                                    if suits[0] == suits[1] and suits[0] == suits[2] and suits[1] == suits[2]:
                                        # 7 7 7 same suit
                                        if suits[0] in ["Clubs", "Hearts", "Diamonds"]:  # non spades 2 to 1

                                            if dealer_card_1.value != 7:
                                                await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]}!")
                                                await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 2 to 1!")
                                                player_class.bet_multipliers = 2
                                                print(f"{player_name} got 21 with non-spades same-suited {(suits[0])} 7-7-7, payout 2 to 1")
                                                special_payout = True

                                            if dealer_card_1.value == 7:  # Super bonus 777 same suit, dealer 7
                                                # if player bet $5-$24, pays 1000, $25 onwards pays 5000
                                                await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} AND DEALER HAS 7!")
                                                if 5 <= player_class.bets[0] <= 24:
                                                    await ctx.send(f"**{player_name}** won $1000!")
                                                    print(f"{player_name} 777 with dealer 7, pays 1000 cos bet of {player_class.bets[0]} between 5 and 24")
                                                    special_payout = True
                                                    player_class.money_change = 1000
                                                    super_bonus_payout = True

                                                if player_class.bets[0] >= 25:
                                                    await ctx.send(f"**{player_name}** won $5000!")
                                                    print(f"{player_name}'s {aa} split 777 with dealer 7, pays 5000 cos bet of {player_class.bets[0]} between 5 and 24")
                                                    special_payout = True
                                                    player_class.money_change = 5000
                                                    super_bonus_payout = True

                                        if suits[0] == "Spades":  # spades 3 to 1

                                            if dealer_card_1.value != 7:
                                                await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]}!")
                                                await ctx.send(f"**{player_name}** won ${player_class.bets[0]}, with payout odds 3 to 1!")
                                                player_class.bet_multipliers = 3
                                                print(f"{player_name} got 21 with non-spades same-suited {(suits[0])} 7-7-7, payout 3 to 1")
                                                special_payout = True

                                            if dealer_card_1.value == 7:
                                                await ctx.send(f"**{player_name}** has hit 21 with 7-7-7 {suits[0]} AND DEALER HAS 7!")
                                                if 5 <= player_class.bets[0] <= 24:
                                                    await ctx.send(f"**{player_name}** won $1000!")
                                                    print(f"{player_name} 777 with dealer 7, pays 1000 cos bet of {player_class.bets[0]} between 5 and 24")
                                                    special_payout = True
                                                    player_class.money_change = 1000
                                                    super_bonus_payout = True

                                                if player_class.bets[0] >= 25:
                                                    await ctx.send(f"**{player_name}** won $5000!")
                                                    print(f"{player_name}'s {aa} split 777 with dealer 7, pays 5000 cos bet of {player_class.bets[0]} between 5 and 24")
                                                    special_payout = True
                                                    player_class.money_change = 5000
                                                    super_bonus_payout = True

                        if not special_payout:
                            await ctx.send(f"**{player_name}** has hit 21!")
                            await ctx.send(f"**{player_name}** won ${player_class.bets[0]}.")
                            print(f"{player_name} got 21, no special payout.")

                        player_class.ended = True
                        if not super_bonus_payout:
                            player_class.money_change = player_class.bets[0] * player_class.bet_multipliers

                    # Finishes this guy's turn

        # If there are still players in the game
        ended_game = True
        for player_class in queueClasses:
            if not player_class.split:
                if not player_class.ended:
                    ended_game = False
            if player_class.split:
                for result in player_class.split_results:
                    if not result:
                        ended_game = False
        if ended_game:
            print(f"Everyone ended the game already.")
            for player_class in queueClasses:
                if player_class.surrender:
                    player_name = player_class.name
                    player_class.money_change = 0 - 0.5 * player_class.bets[0]
                    print(f"{player_name} lost half his bet of {player_class.bets[0]}")

        if not ended_game:
            print(f"People still in the game.")
            # Dealer's turn
            await ctx.send("Dealer draws his second card.")

            # Dealer draws second card
            dealer_card_2 = apd.draw_a_card()
            dealer_cards.append(dealer_card_2)
            print(f"Dealer drew card 2.")

            no_split_dealer_aces = 0
            no_split_dealer_has_ace = False

            somebody_surrendered = False
            for player_class in queueClasses:
                if player_class.surrender:
                    somebody_surrendered = True

            # For card in dealer's hand
            # If any card is Ace, no_split_dealer_aces += 1, and set no_split_dealer_has_ace to True
            for card in dealer_cards:
                if card.value == 11:
                    no_split_dealer_aces += 1
                    no_split_dealer_has_ace = True

            dealer_value += dealer_card_2.value

            print(f"Dealer magic.")
            # Magic happens here
            # While value exceeds 21 but there are aces to -10 and negate, do it
            while dealer_value > 21 and no_split_dealer_aces > 0:
                no_split_dealer_aces -= 1
                dealer_value -= 10

            # Show dealer's hand and everyone's hand
            await ctx.send(dealer_results_format())

            if dealer_card_1.num == "Ace":
                if dealer_card_2.value == 10:
                    for player_class in queueClasses:
                        player_name = player_class.name
                        if player_class.insurance != 0:
                            await ctx.send(f"{player_name} won his insurance bet of {player_class.insurance}. "
                                           f"Insurance pays 2 to 1.")
                            player_class.total_money += 2 * player_class.insurance
                if dealer_card_2.value != 10:
                    for player_class in queueClasses:
                        player_name = player_class.name
                        if player_class.insurance != 0:
                            await ctx.send(f"{player_name} lost his insurance bet of {player_class.insurance}")
                            player_class.total_money -= player_class.insurance

            if dealer_value == 21:
                await ctx.send(f"Dealer pontoons.")
                if somebody_surrendered:
                    await ctx.send("Surrenders are void.")
                print("Dealer pontoons, surrenders are invalid.")
                for player_class in queueClasses:
                    if player_class.surrender:
                        player_name = player_class.name
                        player_class.money_change = 0-player_class.bets[0]
                        print(f"{player_name} lost his bet of {player_class.bets[0]}")

            # No matter the dealer's cards, surrenders lose their bet if not pontoon.
            if dealer_value != 21:
                if somebody_surrendered:
                    await ctx.send(f"Dealer does not pontoons. Those who surrendered lost only half their bet.")
                    print("Dealer doesn't pontoon, surrenders are valid.")
                    for player_class in queueClasses:
                        if player_class.surrender:
                            player_name = player_class.name
                            player_class.money_change = 0-(player_class.bets[0] * 0.5)
                            print(f"{player_name} lost half his bet, which is half of {player_class.bets[0]}")

            time.sleep(global_pause_time)
            for player_class in queueClasses:
                if not player_class.ended:
                    player_name = player_class.name
                    await ctx.send(results_format(player_class))
                    time.sleep(global_pause_time/2)

            print(f"Starting loop for dealer if he hasn't hit hard 17 or soft 18, have a feeling there's issues though.")
            # While dealer hasn't hit hard 17 or soft 18, keep drawing a card

            while True:
                if not no_split_dealer_has_ace:  # if no Ace
                    dealer_hand_soft = False  # dealer hand is hard
                else:  # if dealer has Ace
                    if no_split_dealer_aces == 0:  # dealer has Ace but no more Aces available to -10
                        dealer_hand_soft = False
                    else:
                        dealer_hand_soft = True

                if dealer_hand_soft and dealer_value >= 18 or not dealer_hand_soft and dealer_value >= 17:
                    break
                else:
                    await ctx.send("Dealer draws another card.")
                    no_split_dealer_further_card = apd.draw_a_card()
                    dealer_cards.append(no_split_dealer_further_card)
                    dealer_value += no_split_dealer_further_card.value
                    if no_split_dealer_further_card.value == 11:
                        no_split_dealer_aces += 1
                        no_split_dealer_has_ace = True
                    while dealer_value > 21 and no_split_dealer_aces > 0:
                        no_split_dealer_aces -= 1
                        dealer_value -= 10

                # Show dealer's hand and everyone's hand
                await ctx.send(dealer_results_format())
                time.sleep(global_pause_time)
                for player_class in queueClasses:
                    if not player_class.ended:
                        player_name = player_class.name
                        await ctx.send(results_format(player_class))
                        time.sleep(global_pause_time/2)

            # Dealer has hit hard 17 or soft 18
            print("Dealer has hit hard 17 or soft 18")
            await ctx.send("End of card drawing.")
            time.sleep(global_pause_time)

            # If dealer busts
            if dealer_value >= 22:
                await ctx.send(dealer_results_format())
                await ctx.send("Dealer busted.")
                print("Dealer busted.")
                for player_class in queueClasses:
                    if not player_class.split:
                        if not player_class.ended:
                            player_name = player_class.name
                            await ctx.send(results_format(player_class))
                            await ctx.send(f"**{player_name}**'s hand is {player_class.hands_values()[0]}.")
                            await ctx.send(f"**{player_name}** won ${player_class.bets[0]}")
                            player_class.ended = True
                            player_class.money_change = player_class.bets[0]
                            time.sleep(global_pause_time)
                    if player_class.split:
                        for i in range(len(player_class.split_results)):
                            if player_class.split_results[i]:
                                pass
                            else:
                                player_name = player_class.name
                                await ctx.send(results_format(player_class))
                                if i == 0:
                                    aa = "first"
                                if i == 1:
                                    aa = "second"
                                await ctx.send(f"**{player_name}**'s {aa} hand is {player_class.hands_values()[i]}.")
                                await ctx.send(f"**{player_name}** won ${player_class.bets[i]}")
                                player_class.split_results[i] = True
                                player_class.split_money_change[i] = player_class.bets[i]

            # If dealer hits 21:
            if dealer_value == 21:
                await ctx.send(dealer_results_format())
                await ctx.send("Dealer hit 21.")
                print("Dealer hit 21.")
                for player_class in queueClasses:
                    if not player_class.split:
                        if not player_class.ended:
                            player_name = player_class.name
                            await ctx.send(results_format(player_class))
                            await ctx.send(f"**{player_name}**'s hand is {player_class.hands_values()[0]}.")
                            await ctx.send(f"**{player_name}** lost ${player_class.bets[0]}")
                            player_class.ended = True
                            player_class.money_change = 0-player_class.bets[0]
                            time.sleep(global_pause_time)
                    if player_class.split:
                        for i in range(len(player_class.split_results)):
                            if player_class.split_results[i]:
                                pass
                            else:
                                player_name = player_class.name
                                await ctx.send(results_format(player_class))
                                if i == 0:
                                    aa = "first"
                                if i == 1:
                                    aa = "second"
                                await ctx.send(f"**{player_name}**'s {aa} hand is {player_class.hands_values()[i]}.")
                                await ctx.send(f"**{player_name}** lost ${player_class.bets[i]}")
                                player_class.split_results[i] = True
                                player_class.split_money_change[i] = 0 - player_class.bets[i]
                                time.sleep(global_pause_time)

            # If dealer does not hit 21 or bust:
            if dealer_value < 21:
                print("Dealer <21.")
                await ctx.send(dealer_results_format())
                await ctx.send(f"Dealer's hand is {dealer_value}.")
                for player_class in queueClasses:
                    if not player_class.split:
                        if not player_class.ended:
                            player_name = player_class.name
                            await ctx.send(results_format(player_class))
                            await ctx.send(f"**{player_name}**'s hand is {player_class.hands_values()[0]}.")

                            # If player's value is higher than dealer's
                            if player_class.hands_values()[0] > dealer_value:
                                await ctx.send(f"**{player_name}** won!")
                                await ctx.send(f"**{player_name}** won ${player_class.bets[0]}")
                                player_class.ended = True
                                player_class.money_change = player_class.bets[0]
                                time.sleep(global_pause_time)

                            # If player's value is lower than dealer's
                            if player_class.hands_values()[0] < dealer_value:
                                await ctx.send(f"**{player_name}** lost.")
                                await ctx.send(f"**{player_name}** lost ${player_class.bets[0]}")
                                player_class.ended = True
                                player_class.money_change = 0-player_class.bets[0]
                                time.sleep(global_pause_time)

                            # If player's value is same as dealer
                            if player_class.hands_values()[0] == dealer_value:
                                await ctx.send(f"**{player_name}** and the dealer has the same hand value.")
                                await ctx.send(f"No change in **{player_name}**'s money.")
                                player_class.ended = True
                                time.sleep(global_pause_time)

                    if player_class.split:
                        for i in range(len(player_class.split_results)):
                            if player_class.split_results[i]:
                                pass
                            else:
                                player_name = player_class.name
                                await ctx.send(results_format(player_class))
                                if i == 0:
                                    aa = "first"
                                if i == 1:
                                    aa = "second"
                                await ctx.send(f"**{player_name}**'s {aa} hand is {player_class.hands_values()[i]}.")

                                # If player's value is higher than dealer's
                                if player_class.hands_values()[i] > dealer_value:
                                    await ctx.send(f"**{player_name}** won his {aa} hand!")
                                    await ctx.send(f"**{player_name}** won ${player_class.bets[i]}")
                                    player_class.split_results[i] = True
                                    player_class.split_money_change[i] = player_class.bets[i]
                                    time.sleep(global_pause_time)

                                # If player's value is lower than dealer's
                                if player_class.hands_values()[i] < dealer_value:
                                    await ctx.send(f"**{player_name}** lost his {aa} hand.")
                                    await ctx.send(f"**{player_name}** lost ${player_class.bets[i]}")
                                    player_class.split_results[i] = True
                                    player_class.split_money_change[i] = 0 - player_class.bets[i]
                                    time.sleep(global_pause_time)

                                # If player's value is same as dealer
                                if player_class.hands_values()[i] == dealer_value:
                                    await ctx.send(f"**{player_name}**'s {aa} hand and the dealer has the same hand value.")
                                    await ctx.send(f"No change in **{player_name}**'s money for that hand.")
                                    player_class.split_results[i] = True
                                    player_class.split_money_change[i] = 0
                                    time.sleep(global_pause_time)

        print("Info all typed out, settling money.")
        newrecords = {}
        for player_class in queueClasses:
            if not player_class.split:
                if player_class.money_change > 0:
                    await ctx.send(f"**{player_class.name}**, you earned ${player_class.money_change}")
                if player_class.money_change < 0:
                    await ctx.send(f"**{player_class.name}**, you lost ${-player_class.money_change}")
                if player_class.money_change == 0:
                    await ctx.send(f"**{player_class.name}**, you neither won or lost money.")

            if player_class.split:
                for i in range(len(player_class.split_money_change)):
                    if i == 0:
                        aa = "first"
                    if i == 1:
                        aa = "second"
                    if player_class.split_money_change[i] > 0:
                        await ctx.send(f"**{player_class.name}**, you earned ${player_class.split_money_change[i]} from your {aa} hand.")
                    if player_class.split_money_change[i] < 0:
                        await ctx.send(f"**{player_class.name}**, you lost ${-player_class.split_money_change[i]} from your {aa} hand")
                    if player_class.split_money_change[i] == 0:
                        await ctx.send(f"**{player_class.name}**, you neither won or lost money from your {aa} hand.")
                player_class.money_change = player_class.split_money_change[0] + player_class.split_money_change[1]

            final_money = player_class.total_money + player_class.money_change
            his_games = temp_records[str(player_class.id)][1] + 1
            newrecords[str(player_class.id)] = [final_money, his_games]
        temp_records.update(newrecords)
        print("Money info all typed out, updating database.")

        with open("records.json", 'w') as update_newest_records:
            json.dump(temp_records, update_newest_records)
        print("Database updated")

        for player_id in game_queue:
            continue_msg_out = await ctx.send(f"**{name_from_id(player_id)}**, do you want to continue? You have ${int(temp_records[str(player_id)][0])}")
            await add_multiple_reactions(continue_msg_out, [yEmoji, nEmoji])
            continueornoreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)

            while str(continueornoreaction) not in [yEmoji, nEmoji]:
                continueornoreaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u.name == player_name)
                time.sleep(global_pause_time)

            # Continue
            if str(continueornoreaction) == yEmoji:
                await clear_multiple_reactions(continue_msg_out, [yEmoji, nEmoji])
                time.sleep(global_pause_time)
                print(f"**{name_from_id(player_id)}** continued")

            if str(continueornoreaction) == nEmoji:
                await clear_multiple_reactions(continue_msg_out, [yEmoji, nEmoji])
                game_queue.remove(player_id)
                await ctx.send(f"**{name_from_id(player_id)}**, you have safely left the game.")
                print(f"{name_from_id(player_id)} stopped, left game_queue.")

bot.run(my_token)
