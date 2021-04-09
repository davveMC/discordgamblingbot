import os, discord, random, json
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()

os.chdir("C:\\Users\\ldpla\\Desktop\\Python\\Discord Bots\\Gambling")

#Values
player_cards = []
player_hand = []
player_hits = 0
player_total = 0

dealer_cards = []
dealer_hand = []
dealer_hand_end = []
dealer_total_end = 0
dealer_hits = 0
dtotal,dhits = 0,0
current_player = ""
emojis = []

blackjackActive = False

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready')

# Blackjack!!!
@client.command(pass_context=True)
async def blackjack(ctx, *, q=0, stand= False):
    global player_cards, player_hand, player_hits, player_total, dealer_cards, dealer_hand, dealer_hand, dealer_hits, blackjackActive, current_player,bet


    if current_player == '':
        player_hits, dealer_hits = 0,0
        current_player = ctx.author.id
        await open_account(ctx.author)
        users = await get_bank_data()
        user = ctx.author
        bet = q
        if bet < 10:
        
            pass
           # await
        if users[str(user.id)] >= int(bet): 
            users[str(user.id)] -= int(bet)
        else:
            print("You poor bastard")
        with open("mainbank.json","w") as f:
            json.dump(users,f)
        await create_cards()
    if current_player == ctx.author.id:
        if blackjackActive == False:
            pass
        gameActive = True    
        over_21 = False
        if ctx.author.id != current_player:
            await ctx.channel.send("Tyvärr ett spel åt gången")

        gameActive = False
        while gameActive:
            player_hand = await hand(player_cards, player_hits, player=True)
            dealer_hand = await hand(dealer_cards, dealer_hits)
            player_total, ace = await total(player_hand, player=True)
            dealer_total = await total(dealer_hand, player=False)
            if ace != True:
                if int(player_total) > 21:
                    over_21 = True
            await printEmbed(ctx, dealer_hand, dealer_total,  player_hand, player_total, stand = stand, over_21 = over_21)
            blackjackActive = True
            break

@client.command(pass_context=True)
async def hit(ctx):
    global blackjackActive, player_hits, dealer_hits, current_player, current_player
    if current_player == ctx.author.id:
        if blackjackActive:
            player_hits += 1
            await blackjack(ctx)
        else:
            ctx.send("Error 404")

@client.command(pass_context=True)
async def stand(ctx):
    global blackjackActive, current_player
    if current_player == ctx.author.id:
        await blackjack(ctx, stand = True)
        blackjackActive = False
        await resetall()

async def beting(ctx,bet,status):
    users = get_bank_data()
    user = ctx.author
    if status == "win":
        users[str(user.id)] += bet*1.5
    if status == "draw":
        users[str(user.id)] += bet

    with open("mainbank.json","w") as f:
        json.dump(users,f)
    

async def resetall():
    global player_total, blackjackActive,player_cards,player_hand,player_hits,dealer_hits,dealer_cards, dealer_hand,dtotal,dhits,current_player
    player_cards = []
    player_hand = []
    player_hits = 0
    player_total = 0
    dealer_cards = []
    dealer_hand = []
    dealer_hits = 0
    dtotal,dhits = 0,0
    current_player = ''
def score(total):
    dtotal = dealer_total_end
# Check who won
    if total == dtotal:
        return('Ni fick samma nummer!', 'Du har fått tillbaka alla dina pengar.')

    elif int(dtotal) == 21 or int(total) < int(dtotal) or int(total) > 21:
        return('Du förlorade', 'Tyvärr')
    elif int(dtotal) > 21 or int(total) == 21 or int(total) > int(dtotal) and int(total) < 21:
        return('Du vann!', 'gg ez')

    else:
        return(f"venne vem som vann dealer score: {dtotal} och player score: {total}", 'Bruh')
    
async def printEmbed(ctx, dealer_hand, dealer_total,  player_hand, player_total, stand = False, over_21 = False):
    global dealer_cards,dealer_hand_end,dealer_total_end
    d_stat = "visar en"
    em=discord.Embed(title="Välkommen till Blackjack!", color=0xff0000)
    em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    em.set_thumbnail(url="https://twitter.com/GlobalBlackjack/photo")
    if stand or over_21:
        d_stat = 'fick'
        result, winorloss = score(player_total)
        em.add_field(name=f"Dealern {d_stat}, Totalt: `{dealer_total_end}`", value=f"[`{'` `'.join(map(str,dealer_hand_end))}`](https://bit.ly/3dKVIIU)", inline=False)
        em.add_field(name=f"Du har, Totalt: `{player_total}`", value=f"[`{'` `'.join(map(str,player_hand))}` `?`](https://bit.ly/3dKVIIU)", inline=False)
        em.add_field(name=f"{result}", value=f"{winorloss}", inline=False)
        if result == ('Du vann!', 'gg ez'):
            em.color(color = 0x53836a )
        await resetall()
    else:
        em.add_field(name=f"Dealern {d_stat}, Totalt: `{dealer_total}`", value=f"[`{''.join(map(str,dealer_hand))}` `?`](https://bit.ly/3dKVIIU)", inline=False)
        em.add_field(name=f"Du har, Totalt: `{player_total}`", value=f"[`{'` `'.join(map(str,player_hand))}`](https://bit.ly/3dKVIIU)", inline=False)
        em.add_field(name= ".hit\n.stand", value =".quit", inline= False)
    await ctx.send(embed=em)

async def emoji(hand):
    emoji_ = []
    emojis = ''
    with open("cards.json","r") as f:
        emojis = json.load(f)
    for n in hand:
        emoji_.append(emojis[0][n])
    return(emoji_)

async def create_cards():
    global player_cards, dealer_cards,dtotal,dhits,dealer_hand_end,dealer_total_end
    lst = [2,3,4,5,6,7,8,9,10,'J','Q','K','A']
    deck = []
    for n in lst:
        deck.append(f'{n}C')
        deck.append(f'{n}D')
        deck.append(f'{n}H')
        deck.append(f'{n}S')
    random.shuffle(deck)
    player_cards = deck[:-43]
    dealer_cards = deck[9:-34]
    dealer_hand = []
    dtotal = 0
    dhits = 0

async def dealer(dealer_cards):
    hand = []
    cards = dealer_cards
    total = 0
    total2 = 0
    while total < 17:
        hand.append(cards[0])
        if cards[0][:-1] in {'K','Q','J'}:
            total += 10
        elif cards[0][:-1] == 'A':
            total += 11
            total2 = total - 10
            if total > 21:
                total -=10
        else:
            total += cards[0][:-1]
        if total > 21:
            if total2 > 21:
                cards.pop(0)
                break
        
        cards.pop(0)
    return(total, hand)

async def hand(cards, hits, player=False):
    lst = []
    if player == False:
        hits -= 1
    for n in range(int(hits+2)):
        try:
            lst.append(cards[n])
        except Exception as e:
            print(e,n,lst,cards)
    return lst

async def total(cards, player=False):
    global player_hits, blackjackActive
    lst = []
    total, alttotal = 0,0
    for n in cards:
        n=n[:-1]
        if n == 'J' or n == 'Q' or n == 'K':
            total += 10
            alttotal += 10
        elif n == 'A':
            total += 11
            alttotal += 1
        else:
            total += int(n)
            alttotal += int(n)
    if total > 21 or total == alttotal:
        total = alttotal
        blackjackActive = False
        return(f"{total}")
    elif total != alttotal and total < 21:
        blackjackActive = False
        return(f"{total} eller {alttotal}", True)
        
    elif total == 21:
        blackjackActive = False
        return(f"{total}")
    if player:
        if int(total) > 21:
            await resetall()
            blackjackActive = False
            print("You busted!")
        elif int(total) == 21:
            if int(player_hits) == 0:
                blackjackActive = False
                print("Blackjack")
            else:
                print("You won!!!")
                blackjackActive = False

async def open_account(user):
    users = await get_bank_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)] = 100
    with open("mainbank.json","w") as f:
        json.dump(users,f)
    return True

# Pengar och bank!!!
@client.command()
async def balance(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    wallet_amt = users[str(user.id)]
    em = discord.Embed(title= f"{ctx.author.name}")
    em.add_field(name= f"Chips :white_flower:", value = wallet_amt)
    await ctx.send(embed = em)

async def get_bank_data():
    with open("mainbank.json","r") as f:
        users = json.load(f)
        return users

if __name__ == "__main__":
    client.run(TOKEN)