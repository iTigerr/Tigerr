import discord
import requests
import random
import os
from replit import db
from bs4 import BeautifulSoup
import wikipedia as wiki
import praw

import variables as var
import connect4 as c4

reddit = praw.Reddit(
  client_id= "Z47OA1ACz7kzbG2TUeNbCA",
  client_secret=os.getenv("PRAW_SECRET"),
  user_agent="Tigerr discord bot. /u/BruhWhatsThis, iTiger#1476"
)


def countForRadix(data, placeValue):
    
  count = [0] * 10
  dataLen = len(data)

  for x in range(dataLen):
    placeEl = (data[x] // placeValue) % 10
    count[placeEl] =+ 1

  for x in range(1, 10):
    count[x] =+ count[x-1]

  output = [0] * dataLen
  i = dataLen - 1

  while i >= 0:
    current = data[i]
    placeEl = (data[i] // placeValue) % 10
    count[placeEl] -= 1
    newPos = count[placeEl]
    output[newPos] = current
    i -= 1

  return output

def radix(data):
    
  maxEl = max(data)
  D = 1
  while maxEl > 0:
    maxEl /= 10
    D += 1

  placeValue = 1

  output = data
  while D > 0:
    output = countForRadix(output, placeValue)
    placeValue *= 10
    D -= 1
  return data

def get_role_object(message,input):
  if "<" in input and ">" in input and "@" in input and "&" in input:
    output = int(input.replace("<","").replace(">", "").replace("@", "").replace("&", ""))
    output = discord.utils.get(message.guild.roles, id=output)
    return output
              
  elif not("<" in input and ">" in input and "@" in input and "&" in input):
    for role in message.guild.roles:
      if role.name == input:
        return role
  else:
    raise ValueError

def get_user_object(message,input):
  if "<" in input and ">" in input and "@"  in input:
    output = int(input.replace("<","").replace(">","").replace("@","").replace("!",""))
    for member in message.guild.members:
      if member.id == output:
        return member

def http_cat(code):
  return f"https://http.cat/{code}.png"

def urban(search):
  try:
    #requesting and formatting data
    r = requests.get("http://www.urbandictionary.com/define.php?term={}".format(search))
    soup = BeautifulSoup(r.content, features="html5lib")
    meaning = soup.find("div",attrs={"class":"meaning"}).text
    author = soup.find("div",attrs={"class":"contributor"}).text
    link = "http://www.urbandictionary.com/define.php?term={}".format(search)
    #returning the fully concatenated output
    return (meaning + "\n\n" + author + "\n<" + link.replace(" ", "%20") + ">")
  except AttributeError:
    return "No definition of this word found."

def getWiki(search):
  try:  
    #requesting suggested page
    page = wiki.page(search)
  except wiki.DisambiguationError:
    return ("Be more specific with your search!")
  except wiki.PageError:
    return ("No page found of this topic.")
  #formatting data
  it1 = page.summary.split(".")[:4]
  summary = it1 = ['.'.join(it1)]
  #returning the fully concatenated output
  return ("**"+page.title+"**" + "\n\n" + str(summary)[2:len(summary)-3] + ".\n\nSource: <" + page.url + ">")

def getPost(subreddit, client, message, nsfw):
  post = random.randint(1,101)
  for i, each in enumerate(reddit.subreddit(subreddit).hot(limit=101)):
    if post == i:
      post = each
      break

  if post.over_18 and not(nsfw):
    return getPost(subreddit, client, message, nsfw)
  else:
    return post

def cat(message):
  msg = message.content
  msg = msg.replace("T!cat", "")

  send = ""

  key = os.getenv("cat_key")
  
  if msg == "":
    r = requests.get(f"https://api.thecatapi.com/v1/images/search?api_key={key}")
  else:
    toRemove = []
    breeds = msg.split(",")

    c = 0
    f = True
    for x in breeds:
      if x[0] == " ":
        x = x[1:len(x)]
        
      if len(x) == 4:
        x = x[:4]
      
      elif len(x) > 4:
        if " " not in x:
          x = x[:4]
        else:
          x = x.split(" ",1)
          x[0] = x[0][:1]
          x[1] = x[1][:3]
          x = "".join(x)
          
      x.replace(" ", "")
      breeds[c] = x
      
      if len(requests.get(f"https://api.thecatapi.com/v1/images/search?api_key={key}&breed_ids={x}").json()) == 0:
        if f:
          f = False
          send += f"Invalid breeds found. They have been removed: "
        toRemove.append(x)
        send += x + ", "
      c += 1
        
    for x in toRemove:
      breeds.remove(x)
    breeds = ",".join(breeds)
    
    if len(breeds) != 0:
      r = requests.get(f"https://api.thecatapi.com/v1/images/search?api_key={key}&breed_ids={breeds}")
    else:
      send += "\nSince you gave no valid breeds, a completely random cat has been chosen"
      r = requests.get(f"https://api.thecatapi.com/v1/images/search?api_key={key}")

  if r.status_code == 200:
    r = r.json()[0]["url"]
    return [r, send]
  else:
    return "A HTTP error occurred"

def NasaImage(date):
    baseURL = "https://apod.nasa.gov/apod/ap"
    
    day = date.split("/")[0]
    month = date.split("/")[1]
    year = date.split("/")[2]

    page = requests.get(f"{baseURL}{year}{month}{day}.html")

    if page.status_code == 404:
        return "No image exists for this date"
    elif page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        return ("https://apod.nasa.gov/apod/" + str(soup.find_all("a")[1]).split("<")[1].replace("a href=\"", "").replace("\">","")).split("\"",1)[0]
    else:
        return "A HTTP error occurred"

def weather(search):
  BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
  token = os.getenv("WEATHER_TOKEN")
  
  request_url = f"{BASE_URL}?appid={token}&q={search}"
  response = requests.get(request_url)

  if response.status_code == 200:
      data = response.json()
      weather = data["weather"][0]["description"]
      temperature = round(data["main"]["temp"]-273.15, 2)
      return f"Weather: {weather} \nTemperature: {temperature}℃"
  else:
      return "An error occurred"

def trivia(message):
  tServerID = "trivia"+str(message.guild.id)
  tUserID = "trivia"+str(message.author.id)
  
  if tServerID not in db.keys():
    db[tServerID] = {}

  if tUserID not in db[tServerID]:
    db[tServerID][tUserID] = {
      "total": 0,
      "correct": 0,
      "easyCorrect": 0,
      "mediumCorrect": 0,
      "hardCorrect": 0,
      "easyTotal": 0,
      "mediumTotal": 0,
      "hardTotal": 0,
      "answer": "",
      "answers": "",
      "difficulty": ""
    }

  user = db[tServerID][tUserID]
  
  msg = message.content
  msg = msg.split("T!trivia",1)[1]

  if msg == "":
    r = requests.get("https://the-trivia-api.com/api/questions/")
    rr = requests.get("https://the-trivia-api.com/api/questions/")
    
    if r.status_code == 200 and rr.status_code == 200:
      r = r.json()
      rr = rr.json()
      r = r+rr

      while True:
        q = random.choice(r)

        if q["type"] == "Multiple Choice" and q["isNiche"] == False:
          break

      question = q["question"]
      answers = [q["correctAnswer"]] + q["incorrectAnswers"]
      random.shuffle(answers)
      answer = q["correctAnswer"]
      category = q["category"]
      difficulty = q["difficulty"]

      pAnswers = ""
      c=1
      for a in answers:
        pAnswers += str(c) + ". " + a + "\n"
        c+=1

      user["answer"] = answer
      user["answers"] = answers
      user["difficulty"] = difficulty
      
      return f'{question}\n\n{pAnswers}\n\nCategory: {category}\nDifficulty: {difficulty}\n\nAnswer with T!trivia answer {{number}}'
      
    else:
      return "A http error occurred"

  elif msg.startswith(" stats"):
    try:
      return f'''
      Total questions aswered: {user['total']}
      Total correct answers: {user['correct']}
      Correct rate: {int((user['correct'] / user['total'])*100)}%
      
      Total easy questions asnwered: {user['easyTotal']}
      Total easy correct answers: {user['easyCorrect']}
      Easy correct rate: {int((user['easyCorrect'] / user['easyTotal'])*100)}%
      
      Total medium questions asnwered: {user['mediumTotal']}
      Total medium correct answers: {user['mediumCorrect']}
      Medium correct rate: {int((user['mediumCorrect'] / user['mediumTotal'])*100)}%
      
      Total hard questions asnwered: {user['hardTotal']}
      Total hard correct answers: {user['hardCorrect']}
      Hard correct rate: {int((user['hardCorrect'] / user['hardTotal'])*100)}%
      '''
    except ZeroDivisionError:
      return "To avoid Division by Zero, you must have answered a question of each 3 difficulties before seeing stats"

  elif msg.startswith(" leaderboard"):
    users1 = [u for u in db[tServerID].keys()]
    rates = []
    users = {}

    for u in users1:
      try:
        total = db[tServerID][u]["total"]
        correct = db[tServerID][u]["correct"]
        rate = int((correct/total)*100)
      except ZeroDivisionError:
        rate = 0
      rates.append(rate)
    
    c=0
    for u in users1:
      users[u] = rates[c]
      c+=1
    print(rates)
    rates = radix(rates)
    rates.reverse()

    print(rates)

    c=0
    for rate in rates:
      for key in users:
        if users[key] == rate:
          users1[c] = key
          break
    users = users1

    c=0
    for u in users:
      u = u.replace("trivia", "")
      u = get_user_object(message, u+"<>@")
      users[c] = str(u)
      c+=1

    send = ""
    c=0
    for u in users:
      if c < 10:
        send += str(c+1) + ". "+ users[c] + ": " + str(rates[c]) + "%\n"
      else:
        return send
      c+=1
  else:
    if user["difficulty"] == "":
      return "You do not have any question to answer"
    
    answer = msg.replace(" answer", "")
    if answer[0] == " ":
      answer = answer[1:len(answer)].lower()
    else:
      raise IndexError

    answers = []
    for a in user["answers"]:
      answers.append(a.lower())

    try:
      _ = answers[int(answer)-1]
      answer = answers[int(answer)-1]
    except:
      return "Give your answer as a number correlating to your choice"

    if answer in answers:
      user["total"] += 1
      user[user["difficulty"]+"Total"] += 1
      
      if answer == user["answer"].lower():
        user["correct"] += 1
        user[user["difficulty"]+"Correct"] += 1
        
        answer = user["answer"]
        user["answers"] = ""
        user["answer"] = ""
        user["difficulty"] = ""
        
        return f"Correct, the answer is {answer}"
      else:
        answer = user["answer"]
        user["answers"] = ""
        user["answer"] = ""
        user["difficulty"] = ""
      
        return f"Incorrect, the answer was {answer}"
    else:
      return "This is not one of the options"
    
		
def hangman(message):
  send = str(message.author) + "\n"
  hmID = str(message.author.id) + "hm"
  if hmID in db.keys():
    user = db[hmID]
    try:
      letter = message.content.split("T!hangman ")[1]
      letter = letter.lower()
      if letter == "reset":
        db.pop(hmID)
        return str(message.author) + "\n" + "Game ended."
    except IndexError:
      return str(message.author) + "\n" + "No guessed letter detected."
  else:
    db[hmID] = {
      "guessed_letters" : [],
      "goal" : "",
      "dashes" : "",
      "display" : "",
      "prevDisplay" : "",
      "lives" : 8
    }
    user = db[hmID]
    user["goal"] = random.choice(var.hmWordList)
    user["dashes"] = "-"*len(user["goal"])
    user["display"] = user["dashes"]
    send += "Game started\n"
    send += str(user["lives"]) + " lives remaining\n"
    send += "Guess a letter with T!hangman {letter}\n\n"
    send += user["display"]
    return send

  send += str(user["lives"]) + " lives remaining\n"
  send += "Guess a letter with T!hangman {letter}\n"
  if len(letter) != 1:
    return str(message.author) + "\n" + "You can only guess one letter!\n" + user["display"]
  elif letter in user["guessed_letters"]:
    return str(message.author) + "\n" + "You have already guessed this letter!\n" + user["display"]
  elif not letter.isalpha():
    return str(message.author) + "\n" + "Not a letter!\n" + user["display"]
  else:
    user["guessed_letters"].append(letter)
    counter = 0
    replaceIndex = [pos for pos, char in enumerate(user["goal"]) if char == letter]
    user["prevDisplay"] = user["display"]
    for x in range(0, len(replaceIndex)):
      finalIndex = int(replaceIndex[counter])
      user["display"] = user["dashes"][:finalIndex] + letter + user["dashes"][finalIndex+1:]
      user["dashes"] = user["display"]
      counter = counter + 1
    if user["dashes"] == user["prevDisplay"]:
      user["lives"] = user["lives"] - 1
      if user["lives"] < 1:
        db.pop(hmID)
        return str(message.author) + "\n" + "The word was: " + user["goal"] + "\nYou Lost!\n"
      return str(message.author) + "\n" + letter + " is not in the word.\n" + user["display"] + "\n" + str(user["lives"]) + " lives left."
    elif user["display"] == user["goal"]:
      db.pop(hmID)
      return str(message.author) + "\n" + user["goal"] + "\n" + "You won!\n"
    else:
      send += user["display"] + "\n"
  return send

def unscramble(message):
  send = str(message.author) + "\n"
  usID = str(message.author.id) + "us"
  if usID in db.keys():
    user = db[usID]
    try:
      word = message.content.split("T!unscramble ")[1]
      word = word.lower()
      if word == "reset":
        db.pop(usID)
        return str(message.author) + "\n" + "Game ended."
    except IndexError:
      return str(message.author) + "\n" + "No guessed word detected."
  else:
    db[usID] = {
      "goal" : "",
      "display" : "",
      "tries" : 0
    }
    user = db[usID]
    user["goal"] = random.choice(var.hmWordList)
    user["display"] = ''.join(random.sample(user["goal"], len(user["goal"])))
    send += "Game started\n"
    send += str(user["tries"]) + " attempts\n"
    send += "Try to unscramble the word\n"
    send += "Guess a word with T!unscramble {word}\n"
    send += user["display"]
    return send
    
  black = "⬛"
  green = "🟩"
  if word == user["goal"]:
    goal = user["goal"]
    attempts = user["tries"]
    db.pop(usID)
    return str(message.author) + "\n" + goal + "\n" + (green+" ")*len(goal) + "\n" + "You won in " + str(attempts+1) + " attempts!\n"
  squares = []
  
  if len(word) == len(user["goal"]):
    user["tries"] += 1
    for x, char in enumerate(word):
      squares.append("")
      if char == user["goal"][x]:
        squares[x] = green
      else:
        squares[x] = black
  else:
    return "You need to guess a word the same length as the hint"
  squares = " ".join(squares)

  send += str(user["tries"]) + " attempts\n"
  send += "Guess a word with T!unscramble {word}\n"
  send += user["display"] + "\n"
  send += word + "\n"
  send += squares
  return send


def connect4(message):
  msg = message.content.split(" ",1)[1]
  
  allplayer1 = [db[key]["player1"] for key in db.keys() if key[len(key)-2:] == "c4"]
  allplayer2 = [db[key]["player2"] for key in db.keys() if key[len(key)-2:] == "c4"]
  if message.author.id in allplayer1 or message.author.id in allplayer2: # user is a player in a game
    if msg.replace(" ", "").startswith("<@"): # user is trying to start new game
      return discord.Embed(description="You are already in a game of connect4. Use 'T!connect4 stop' to end an ongoing game")
      
    
    gameIDs = [db[key]["id"] for key in db.keys() if key[len(key)-2:] == "c4"]
    for ID in gameIDs:
      game = db[ID]
      if game["player2"] == message.author.id or game["player1"] == message.author.id: # user is a player in game
        if msg.replace(" ", "").startswith("stop"): # user used stop command
          os.remove(f"{db[ID]['id']}c4.png")
          del db[ID]
          return discord.Embed(description="Game stopped successfully")

        elif msg.replace(" ", "").startswith("view"): # user used view command
          return [discord.Embed(description="This is your current game"), c4.Game(game, message.guild).render()]

        else: # user supposedly played a move
          game = c4.Game(db[ID], message.guild)
          memberIDs = [user.id for user in message.guild.members]
          if not(game.player1 in memberIDs and game.player2 in memberIDs): # both players of game are not in server
            return discord.Embed(description="Can only play game in server with both players")
          try:
            column = int(msg.replace(" ", ""))
      
            if game.player == 1 and game.player1 == message.author.id: # correct player 1
              send = game.play(column)
              if send[0].description.startswith("It's a draw!") or send[0].description.startswith("yellow wins!") or send[0].description.startswith("red wins!"): # game ended
                os.remove(f"{db[ID]['id']}c4.png")
                del db[ID]
                return send
              else: # game continued
                return send
            elif game.player == 2 and game.player2 == message.author.id: # correct player 2
              send = game.play(column)
              if send[0].description == "It's a draw!" or send[0].description == "yellow wins!" or send[0].description == "red wins!": # game ended
                os.remove(f"{db[ID]['id']}c4.png")
                del db[ID]
                return send
              else: # game continued
                return send
            else: # incorrect player
              return discord.Embed(description="It is not your turn")
            if send[0].description == "It's a draw!" or send[0].description == "yellow wins!" or send[0].description == "red wins!": # game ended
              os.remove(f"{db[ID]['id']}c4.png")
              del db[ID]
              return send
            else: # game continued
              return send
            
            
          except ValueError:
            return discord.Embed(description="Invalid column")

  c4ID = str(message.author.id)+"c4"
  states = []
  for i in range(42):
    states.append("empty")

  try:
    player2 = get_user_object(message, msg).id
  except:
    return discord.Embed(description="Mention a member to start a game with them")

  if player2 in allplayer1 or message.author.id in allplayer2:
    return discord.Embed(description="You cannot start a game with this user since they are already in a game")

  try:
    db[c4ID] = {
      "id": c4ID,
      "player": 1,
      "player1": message.author.id,
      "player2": get_user_object(message, msg).id,
      "states": states
    }
  except:
    return discord.Embed(description="Mention a member to start a game with them")
  game = c4.Game(db[c4ID], message.guild)
  return [discord.Embed(title="Game started", description=f"It is player 1's turn! <@{game.player1 if game.player == 1 else game.player2}>"), game.render()]
    
      