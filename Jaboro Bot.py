import discord
from discord.ext import commands
from discord import app_commands
import random
import string
from datetime import timedelta, datetime
import pytz
import requests
import json
import os
from discord.ui import View, Button, Select

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(),
case_insensitive=True)

mainshop = [{"name":"Watch","price":100,"description":"Tell the time"}]










async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("economy17.json", "w") as f:
        json.dump(users,f)
    return True



async def get_bank_data():
    with open("economy17.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user,change=0,mode = "wallet"):
    users = await get_bank_data()


    users[str(user.id)][mode] += change

    with open("economy17.json", "w") as f:
        json.dump(users,f)


        bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal
async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("economy17.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]


















 
@bot.event
async def on_ready():
    print("The bot is now online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    activity = discord.Game(name="Discord")
    await bot.change_presence(activity=activity)
    status = discord.Status.do_not_disturb
    await bot.change_presence(status=status, activity=activity)



@bot.tree.command(name="say")
@app_commands.describe(what_to_say = "What Should I Say?")
async def say(interaction: discord.Interaction, what_to_say: str):
    await interaction.response.send_message(f"{interaction.user.mention} said `{what_to_say}`")




@bot.tree.command(name="cf", description="coinflip")
async def cf(interaction: discord.Interaction, choice: str):
    valid_choices = ["heads", "tails"]

    if choice.lower() not in valid_choices:
        await interaction.response.send_message("Invalid choice! Please choose either 'heads' or 'tails'.")
        return

    coin_side = random.choice(valid_choices)

    if choice.lower() == coin_side:
        result = "You win!"
    else:
        result = "You lose!"

    await interaction.response.send_message(f"The coin landed on ```{coin_side}. {result}```")


@bot.tree.command(name="ban", description="bans users")
async def ban(interaction: discord.Interaction, member: discord.Member, reason : str):
    if not interaction.user.guild_permissions.ban_members:
        em1 = discord.Embed(title=f"Ban Case", description=f"You do not have permission to use this command.")
        await interaction.response.send_message(em1=em1)
        return
    await member.ban()
    embed = discord.Embed(title=f"Ban Case", description=f"{member.mention} was banned from ```{interaction.guild.name}``` for reason: ```{reason}``` they were banned by {interaction.user.mention}")
    await interaction.response.send_message(embed=embed)
    embed = discord.Embed(title=f"Ban Case", description=f"You were banned from ```{interaction.guild.name}``` for reason: ```{reason}``` you were banned by {interaction.user.mention}")
    await member.send(embed=embed)





















@bot.tree.command(name="kick", description="kicks users")
async def kick(interaction: discord.Interaction, member: discord.Member, *, reason: str):
    if not interaction.user.guild_permissions.kick_members:
        embed = discord.Embed(title=f"You are not allowed to use this command.", description=f"You must have the permission: Kick Members.")
        await interaction.response.send_message(embed=embed)
        if interaction.user == member:
            embed = discord.Embed(title="You cannot kick yourself.")
            await interaction.response.send_message(embed=embed)
        return

    await member.kick(reason=reason)
    embed = discord.Embed(title=f"Kick Case", description=f"{member.mention} has been kicked for reason: {reason}")
    await interaction.response.send_message(embed=embed)

    embed = discord.Embed(title=f"Kick Case", description=f"You have been kicked from {interaction.guild.name} by {interaction.user.mention}. For reason: {reason}")
    await member.send(embed=embed)








@bot.tree.command()
async def embedcreate(interaction: discord.Interaction, title: str, description: str):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.random()
    )
    await interaction.response.send_message(embed=embed)










@bot.tree.command(name="ui", description="gets mentioned user's user info")
async def ui(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="User Info", color=discord.Color.random())
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Discord", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Roles", value=", ".join(role.name for role in member.roles[1:]), inline=False)


    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="rng", description="random number generator")
async def rng(interaction: discord.Interaction, min: int, max: int):
    if min >= max:
        await interaction.response.send_message("Invalid range. The start value must be less than the end value.")
        return
    random_num = random.randint(min, max)
    await interaction.response.send_message(f"{random_num}")

@bot.tree.command(name="rlg", description="random letter generator")
async def rlg(interaction: discord.Interaction):
    random_letter = random.choice(string.ascii_letters)
    await interaction.response.send_message(f"{random_letter}")








@bot.tree.command(name="embedtitle", description="title of an embed")
async def embedtitle(interaction: discord.Interaction, title_say: str):
    embed = discord.Embed(title=f" {interaction.user.mention} said: {title_say}", color= discord.Color.random()) 
    await interaction.response.send_message(embed=embed)







@bot.tree.command(name="balance", description="check user balance")
async def balance(interaction: discord.Interaction):
    await open_account(interaction.user)

    users = await get_bank_data()
    
    user = interaction.user


    

    wallet_amt = users[str(user.id)]["wallet"] 
    bank_amt = users[str(user.id)]["bank"] 

    em =  discord.Embed(title=f"{interaction.user.name} here is your balance.", color=discord.Color.dark_blue())
    em.add_field(name = "Wallet Balance",value= wallet_amt)
    em.add_field(name = "Bank Balance",value= bank_amt)
    await interaction.response.send_message(embed=em)
    


@bot.tree.command(name="beg", description="beg for money")
async def beg(interaction: discord.Interaction):
        await open_account(interaction.user)
        users = await get_bank_data()
        user = interaction.user

        earnings = random.randint(1, 500)


        await interaction.response.send_message(f"You begged and begged and someone gave you {earnings} dollars.")



        users[str(user.id)]["wallet"] += earnings

        with open("economy17.json", "w") as f:
            json.dump(users,f)



        wallet_amt = users[str(user.id)]["wallet"] 





@bot.tree.command(name="withdraw", description="withdraw money from the bank")
async def withdraw(interaction: discord.Interaction, amount:str):
    await open_account(interaction.user)
    if amount == None:
        await interaction.response.send_message("Please enter the amount of money you want to withdraw.")
        return
    bal= await update_bank(interaction.user)
    amount = int(amount)
    if amount>bal[1]:
        await interaction.response.send_message("You dont have that amount of money.")
        return
    if amount<0:
        await interaction.response.send_message("Amount must be positive.")
        return
    

    await update_bank(interaction.user,amount,"wallet")
    await update_bank(interaction.user,-1*amount,"bank")



    await interaction.response.send_message(f"You withdrew {amount} dollars from your bank.")




@bot.tree.command(name="deposit", description="deposit money into the bank")
async def withdraw(interaction: discord.Interaction, amount:str):
    await open_account(interaction.user)
    if amount == None:
        await interaction.response.send_message("Please enter the amount of money you want to deposit.")
        return
    bal= await update_bank(interaction.user)
    amount = int(amount)
    if amount>bal[1]:
        await interaction.response.send_message("You dont have that amount of money.")
        return
    if amount<0:
        await interaction.response.send_message("Amount must be positive.")
        return
    

    await update_bank(interaction.user,-1*amount,"wallet")
    await update_bank(interaction.user, amount,"bank")



    await interaction.response.send_message(f"You deposited {amount} dollars into your bank.")







@bot.tree.command(name="give", description="give money to other users")
async def give(interaction: discord.Interaction, member: discord.Member, amount:str):
    await open_account(interaction.user)
    await open_account(member)
    if amount == None:
        await interaction.response.send_message("Please enter the amount of money you want to send.")
        return
    bal= await update_bank(interaction.user)
    amount = int(amount)
    if amount>bal[1]:
        await interaction.response.send_message("You dont have that amount of money.")
        return
    if amount<0:
        await interaction.response.send_message("Amount must be positive.")
        return
    

    await update_bank(interaction.user,-1*amount,"bank")
    await update_bank(member, amount,"bank")



    await interaction.response.send_message(f"You gave {member.mention} {amount} dollars.")






    










@bot.tree.command(name="rob", description="rob users")
async def give(interaction: discord.Interaction, member: discord.Member):
    await open_account(interaction.user)
    await open_account(member)
    bal= await update_bank(member)
    if bal[0]<100:
        await interaction.response.send_message(f"{member.mention} does not have enough money.")
        return
    

    earnings = random.randrange(0, bal[0])


    await update_bank(interaction.user, earnings)
    await update_bank(interaction.user, -1* earnings)



    await interaction.response.send_message(f"You robbed {member.mention} and gained {earnings} dollars.")







@bot.tree.command(name="shop", description="buy items!")
async def shop(interaction: discord.Interaction):
    em = discord.Embed(title="Shop")


    for item in mainshop:
        name = item["name"]
        price = item["price"]
        description = item["description"]
        em.add_field(name = name, value= f"${price} | {description}")

        await interaction.response.send_message(embed=em)





@bot.tree.command(name="buy", description="buy a item")
async def buy(interaction: discord.Interaction, item:str, amount: int = 1):
    await open_account(interaction.user)

    res = await buy_this(interaction.user,item, amount)

    if not res[0]:
        if res[1]==1:
            await interaction.response.send_message("That Object isn't there!")
            return
        if res[1]==2:
            await interaction.response.send_message(f"You don't have enough money in your wallet to buy {amount} {item}")
            return
        


    await interaction.response.send_message(f"You just bought {amount} {item}")


@bot.tree.command(name="bag", description="check your bag")
async def bag(interaction: discord.Interaction):
    await open_account(interaction.user)
    user = interaction.user
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await interaction.response.send_message(embed = em)    



    




@bot.tree.command(name="work", description="work for money")
async def work(interaction: discord.Interaction):
    await open_account(interaction.user)
    users = await get_bank_data()
    user = interaction.user

    earnings = random.randrange(1000)


    await interaction.response.send_message(f"You worked and got {earnings} dollars!")



    users[str(user.id)]["bank"] += earnings

    with open("economy17.json", "w") as f:
        json.dump(users,f)










@bot.tree.command(name="memberbalance", description="check user balance")
async def memberbalance(interaction: discord.Interaction, member: discord.Member):
    await open_account(interaction.user)
    await open_account(member)

    users = await get_bank_data()
    

    wallet_amt2 = users[str(member.id)]["wallet"] 
    bank_amt2 = users[str(member.id)]["bank"] 

    em2 = discord.Embed(title=f"Here is {member.name}'s balance", color = discord.Color.dark_blue())
    em2.add_field(name = "Wallet Balance", value= wallet_amt2)
    em2.add_field(name = "Bank Balance", value= bank_amt2)
    await interaction.response.send_message(embed=em2)




@bot.tree.command(name="insulter", description="insult anyone you dont like!")
async def jjwjwj(interaction:discord.Interaction, member: discord.Member, insult: str):
    if member == interaction.user:
        await interaction.response.send_message(f"{interaction.user.mention} you cant insult yourself!!")
    j = interaction.user.mention
    h = member.mention
    em01=discord.Embed(title =f"{j}'s insult to {h}")
    em01.add_field(name=f"It says:", value=f"**{insult}**",inline=True)
    await interaction.response.send_message(embed=em01)








bot.run("TOKEN")
