# "kill 1" in shell if discord HTTP error

import discord

from replit import db

import random
import os
import time

from keep_alive import keep_alive
import variables as var
import functions

RED = discord.Colour.from_rgb(255,0,0)
MAIN = discord.Colour.from_rgb(115,20,165)

games = []

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

client = discord.Client(intents = intents)

async def error(message):
  emb = discord.Embed(description="Incorrect command format or an error occurred.", colour=RED)
  emb.set_image(url="https://cdn.discordapp.com/attachments/1023323171144872057/1058160662544654387/D31en26T471bAAAAAElFTkSuQmCC.png")
  await message.channel.send(embed=emb)

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  print("Running on " + str(len(client.guilds)) + " servers")

  await client.change_presence(status=discord.Status.online, activity=discord.Game(name="T!help"))

  #for key in db.keys():
  #  del db[key]
  

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  nsfw = message.channel.is_nsfw()

  if msg.startswith("T!ping"):
    try:
      emb = discord.Embed(title="Pong!", description="> " + str(round(client.latency*1000,2)) + "ms" , colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!help"):
    try:
      categories = msg.split("T!help ",1)
      if len(categories) > 1:
        emb = discord.Embed(title=categories[1], description="> " + var.help_dict[categories[1]], colour=MAIN)
      elif len(categories) ==  1:
        emb = discord.Embed(title=categories[0], description="> " + var.help_dict[categories[0].replace(" ","")], colour=MAIN)
      else:
        raise IndexError
      await message.channel.send(embed=emb)
    except:
      await message.channel.send(embed=discord.Embed(description="Invalid help command", colour=RED))

  if msg.startswith("T!cat"):
    try:
      x = functions.cat(message)
  
      if x == "A HTTP error occurred":
        emb = discord.Embed(description=x, colour=MAIN)
        
      elif len(x) == 2:
        emb = discord.Embed(description=x[1], colour=MAIN)
        
      else:
        emb = discord.Embed(colour=MAIN)
  
      emb.set_image(url=x[0])
      await message.channel.send(embed=emb)
    except:
      await error(message)
    

  if msg.startswith("T!meme"):
    try:
      post = functions.getPost("memes", client, message, nsfw)
      title = post.title
      description = f"https://reddit.com{post.permalink}\n{int(post.upvote_ratio*100)}% positive\nFrom u/{post.author.name}"
      emb = discord.Embed(title=title, description=description, colour=MAIN)
      emb.set_image(url=post.url)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!shitpost"):
    try:
      post = functions.getPost("shitposting", client, message, nsfw)
      title = post.title
      description = f"https://reddit.com{post.permalink}\n{int(post.upvote_ratio*100)}% positive\nFrom u/{post.author.name}"
      emb = discord.Embed(title=title, description=description, colour=MAIN)
      emb.set_image(url=post.url)
      await message.channel.send(embed=emb)
    except:
      await error(message)
    
  if msg.startswith("T!porn"):
    try:
      if nsfw:
        post = functions.getPost("porn", client, message, nsfw)
        title = post.title
        description = f"https://reddit.com{post.permalink}\n{int(post.upvote_ratio*100)}% positive\nFrom u/{post.author.name}"
        emb = discord.Embed(title=title, description=description, colour=MAIN)
        emb.set_image(url=post.url)
        await message.channel.send(embed=emb)
      else:
        await message.channel.send(embed=discord.Embed(description="This command can only be used in an NSFW channel.", colour=RED))
    except:
      await error(message)
      
  if msg.startswith("T!wiki"):
    try:
      search = msg.split("T!wiki ",1)[1]
      emb = discord.Embed(description=functions.getWiki(search), colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!nasa"):
    try:
      search = msg.split("T!nasa ",1)[1]
      await message.channel.send(functions.NasaImage(search))
    except:
      await error(message)

  if msg.startswith("T!urban"):
    try:
      search = msg.split("T!urban ",1)[1]
      emb = discord.Embed(title=search, description=functions.urban(search), colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!weather"):
    try:
      search = msg.split("T!weather ",1)[1]
      emb = discord.Embed(title="Weather in " + search, description=">>> " + functions.weather(search), colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg == "T!flip":
    emb = discord.Embed(title=str(message.author), description=">>> " + random.choice(["Heads", "Tails"]), colour=MAIN)
    await message.channel.send(embed=emb)

  if msg.startswith("T!random"):
    try:
      search = msg.split("T!random ",1)[1]
      rep = " " if " " not in search else ""
      search = search.replace(",", rep)
      n1 = int(search.split(" ",1)[0].replace(" ",""))
      n2 = int(search.split(" ",1)[1].replace(" ",""))
      n1, n2 = (min([n1,n2]), max([n1,n2]))
      emb = discord.Embed(title=str(message.author), description=f"Random number between {n1} and {n2}:\n{random.randint(n1,n2)}", colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)
    
  
  if msg.startswith("T!type"):
    #if user has admin perms
    if message.author.guild_permissions.administrator:
      try:
        #seperating message into needed chunks
        noPre = msg.split("T!type ",1)[1]
        send = noPre.split(";")[0]
        channelstr = noPre.split(";")[1]
        channelstr = channelstr.replace(" ", "")
        #if channel is tagged
        if "<" in channelstr and ">" in channelstr and "#" in channelstr:
          channelstr = channelstr.replace("<", "")
          channelstr = channelstr.replace(">", "")
          channelstr = channelstr.replace("#", "")
          channel = int(channelstr)
          channel = client.get_channel(channel)
        #if channel is string
        else:
            channel = discord.utils.get(client.get_all_channels(), name = channelstr)
        
        try:
          await channel.send(send)
          time.sleep(1)
          await message.delete()
        except AttributeError:
          await message.channel.send("No channel with this name exists.", delete_after = 5)
          time.sleep(1)
          await message.delete()
      except:
        await error(message)
    else:
      await message.channel.send(embed=discord.Embed(description="Only members with Administrator role can use this command.", colour=RED))
      
  if msg.startswith("T!clear"):
    #if user has admin perms
    if message.author.guild_permissions.administrator:
      try:
        #seperating message into needed chunks
        number = msg.split("T!clear ")[1]
        number = number.replace(" ", "")
        number = int(number)
        #setting limit of 1-100 messages
        if number < 101 and number > 0:
          async for x in message.channel.history(limit = number):
            await x.delete()
          await message.delete()
        else:
          await message.channel.send(embed=discord.Embed(description="Chosen amount too high. Must be 100 or less.", colour=RED))
      except:
        await error(message)
    else:
      await message.channel.send(embed=discord.Embed(description="Only members with Administrator role can use this command.", colour=RED))
  
  if msg.startswith("T!role"):
    if message.author.guild_permissions.administrator:
      try:
        noPre = msg.split("T!role ",1)[1]
        command = noPre.split(" ",1)[0].replace(" ", "")
        rolename = noPre.split(" ",1)[1]
      
        if command == "create":
          await message.guild.create_role(name = rolename)
          await message.channel.send(embed=discord.Embed(description=f"Role {rolename} created", colour=MAIN))
          
        elif command == "delete":
          try:
            role = functions.get_role_object(message,rolename)

            await message.channel.send(embed=discord.Embed(description=f"Role {role.name} deleted", colour=MAIN))
            await role.delete()
          except:
            await message.channel.send(embed=discord.Embed(description="An error occurred.", colour=RED))
  
        elif command == "rename":
          ogName = rolename.split(" ; ")[0]
          newName = rolename.split(" ; ")[1]
  
          try:
            role = functions.get_role_object(message,ogName)

            old = role.name
            await role.edit(name = newName)
            await message.channel.send(embed=discord.Embed(description=f"{old} is now {newName}", colour=MAIN))
          except:
            await message.channel.send(embed=discord.Embed(description="An error occurred.", colour=RED))

        elif command == "color" or command == "colour":
          role = rolename.split(" ; ")[0]
          dispCol = rolename.split(" ; ")[1]
          newCol = int("0x" + dispCol, base=16)

          try:
            role = functions.get_role_object(message,role)
  
            await role.edit(colour = discord.Colour(newCol))
            await message.channel.send(embed=discord.Embed(description=f"Role {role.name} colour is now {dispCol}", colour=MAIN))
          except:
            await message.channel.send(embed=discord.Embed(description="An error occurred.", colour=RED))

        elif command == "give":
          user = rolename.split(" ; ")[0]
          role = rolename.split(" ; ")[1]
          try:
            user = functions.get_user_object(message,user)
            role = functions.get_role_object(message,role)
            await user.add_roles(role)
            await message.channel.send(embed=discord.Embed(description=f"{user.name} given {role.name} successfully.", colour=MAIN))
          except discord.errors.Forbidden:
            await message.channel.send(embed=discord.Embed(description="Chosen role is above my role on hierarchy.", colour=RED))
          except:
            await message.channel.send(embed=discord.Embed(description="An error occurred.", colour=RED))
          
        else:
          await message.channel.send(embed=discord.Embed(description="Invalid command", colour=RED))
      except:
        await error(message)
    else:
      await message.channel.send(embed=discord.Embed(description="Only members with Administrator role can use this command.", colour=RED))

  if msg.startswith("T!trivia"):
    #try:
    emb = discord.Embed(title=str(message.author), description=functions.trivia(message), colour=MAIN)
    await message.channel.send(embed=emb)
    #except:
      #await error(message)
  
  if msg.startswith("T!hangman"):
    try:
      emb = discord.Embed(description="> "+functions.hangman(message), colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!unscramble"):
    try:
      emb = discord.Embed(description="> "+functions.unscramble(message), colour=MAIN)
      await message.channel.send(embed=emb)
    except:
      await error(message)

  if msg.startswith("T!connect4"):
    try:
      emb = functions.connect4(message)
      if type(emb) is discord.Embed:
        emb.colour = MAIN
        await message.channel.send(embed=emb)
      elif type(emb) is list:
        emb[0].colour = MAIN
        await message.channel.send(embed=emb[0], file=emb[1])
    except:
      await error(message)

  if "smd" in msg.lower() or "suck my dick" in msg.lower():
    await message.channel.send(random.choice(var.responses))

  if "joe" in msg.lower():
    await message.channel.send("<@" + str(message.author.id) + ">" " Joe mama")

  if any(phrase in msg.lower() for phrase in var.maternal_phrases):
    await message.channel.send("<@" + str(message.author.id) + ">" " bro stfu")

  if "cheese" in msg.lower():
    await message.channel.send("There's no cheese and crackers in prison Gromit")
      


keep_alive()
client.run(os.getenv("TOKEN"))