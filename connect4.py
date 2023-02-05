import pygame
import discord
from replit import db
pygame.init()


GREY = (170,170,170)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

r = 25
s = 5

text = pygame.font.SysFont('Lato-Bold.ttf', 30)


class Game:
  def __init__(self, game, _guild):
    self.id = game["id"]
    self.player1 = game["player1"]
    self.player2 = game["player2"]

    self.states = game["states"]

    self.guild = _guild

    self.l = 7
    self.w = 6
    
    self.x = r * 2 * self.l + s * (self.l + 1)
    self.y = r * 2 * self.w + s * (self.w + 1)
    self.dim = [self.x,self.y+75]
         
    self.screen = pygame.display.set_mode(self.dim)

    self.board = Board(self.l, self.w, self.screen, game["states"])
    self.board.create_dirs()
    
    self.l = self.board.l
    self.w = self.board.w
    
    self.player = game["player"]
    
    self.colText = []
    for i in range(self.l):
      self.colText.append(text.render(str(i+1), True, WHITE))

    
  def render(self):
    self.screen.fill((14, 66, 143))

    p1 = text.render(f"Player 1", True, RED)
    p2 = text.render(f"Player 2", True, YELLOW)

    n1, n2 = None, None
    for member in self.guild.members:
      id = member.id
      if id == self.player1:
        n1 = str(member)
      if id == self.player2:
        n2 = str(member)
      if n1 != None and n2 != None:
        break

    n1 = text.render(f"{n1}", True, RED)
    n2 = text.render(f"{n2}", True, YELLOW)

    self.screen.blit(p2, (10, self.y+50))
    self.screen.blit(p1, (10, self.y+25))

    self.screen.blit(n2, (150, self.y+50))
    self.screen.blit(n1, (150, self.y+25))

    for i in range(self.l):
      self.screen.blit(self.colText[i], (self.board.spaces[i].circle.x-5, self.y))

    for space in self.board.spaces:
      space.circle.draw()

    pygame.image.save(self.screen, f"{self.id}c4.png")
    return discord.File(f"{self.id}c4.png")

    
  def play(self, col):
    try:
      col = int(col)
      if col > self.board.l or col < 1:
        raise ValueError
      if not self.board.col_available(col):
        raise NameError
    except ValueError:
      return discord.Embed(description="Enter a valid value")
    except NameError:
      return discord.Embed(description="This column is full")
          
    self.board.place(col, self.player)
    db[self.id]["states"] = [state for state in [self.board.spaces[i].circle.state for i in range(42)]]
    self.render()
    self.player = 1 if self.player == 2 else 2
    db[self.id]["player"] = self.player
 
    win = self.board.check_win()
    if win == "draw":
      return [discord.Embed(description="It's a draw!"), self.render()]
    if win == "red" or win == "yellow":
      return [discord.Embed(description=f"{win} wins! <@{self.player1 if self.player == 2 else self.player2}>"), self.render()]
    if win == None:
      return [discord.Embed(description=f"Player {self.player}'s turn! <@{self.player1 if self.player == 1 else self.player2}>"), self.render()]


class Space:
  def __init__(self, _pos):
    self.x, self.y = _pos
    self.circle = None

        
class Circle:
  def __init__(self, _r, _pos, _state, _rgb, _screen):
    self.x = int(_pos[0])
    self.y = int(_pos[1])
    self.state = _state
    self.r = _r
    self.rgb = _rgb
    self.screen = _screen

  def draw(self):
    if self.state == "yellow":
      self.rgb = YELLOW
    if self.state == "red":
      self.rgb = RED
    if self.state == "empty":
      self.rgb = GREY
        
    pygame.draw.circle(self.screen, self.rgb, (self.x,self.y), r)


class Board:
  def __init__(self, _l, _w, _screen, _states):
    self.l = _l
    self.w = _w

    self.states = _states
        
    self.positions = []
    for i in range(_w):
      y = s*(i+_w) + r*2*(i)
      for j in range(_l):
        x = s*(j+_l-1) + 2*r*(j)
        self.positions.append((x,y))

    self.spaces = []
    for i in range(_l*_w):
      self.spaces.append(Space(self.positions[i]))

    for i, space in enumerate(self.spaces):
      space.circle = Circle(r, self.positions[i], self.states[i], GREY, _screen)

  def up(self, x):
    return x - self.l
  def down(self, x):
    return x + self.l
  def left(self, x):
    return x - 1
  def right(self, x):
    return x + 1
  def up_left(self, x):
    return self.up(x) - 1
  def up_right(self, x):
    return self.up(x) + 1
  def down_left(self, x):
    return self.down(x) - 1
  def down_right(self, x):
    return self.down(x) + 1

  def create_dirs(self):
    self.dirs = {
      "up": self.up,
      "down": self.down,
      "left": self.left,
      "right": self.right,
      "up_left": self.up_left,
      "up_right": self.up_right,
      "down_left": self.down_left,
      "down_right": self.down_right
      }
        

  def place(self, col, player):
    search = []
    for i in range(self.w):
      search.append((col-1)+i*self.l)
    available = None
    for i in search:
      if self.spaces[i].circle.state == "empty":
        available = self.spaces[i].circle
    if available != None:
      if player == 1:
        available.state = "red"
      else:
        available.state = "yellow"

  def col_available(self, col):
    return self.spaces[col-1].circle.state == "empty"

  def neighbours(self, i, direction = None, colour = None):
    if colour == None and direction == None:
      if not(self.spaces[i].circle.state == "empty"):
        colour = self.spaces[i].circle.state

        self.total = 1
        up = self.dirs["up"](i)
        if i < self.l:
          pass
        else:
          if self.spaces[up].circle.state == colour:
            self.total += 1
            self.neighbours(up, "up", colour)
            if self.total > 3:
              return colour


        self.total = 1
        down = self.dirs["down"](i)
        if i > (self.l * (self.w-1))-1:
          pass
        else:
          if self.spaces[down].circle.state == colour:
            self.total += 1
            self.neighbours(down, "down", colour)
            if self.total > 3:
              return colour


        self.total = 1
        left = self.dirs["left"](i)
        if i % self.l == 0:
          pass
        else:
          if self.spaces[left].circle.state == colour:
            self.neighbours(left, "left", colour)
            self.total += 1
            if self.total > 3:
              return colour


        self.total = 1
        right = self.dirs["right"](i)
        if (i-(self.l-1)) % self.l == 0:
          pass
        else:
          if self.spaces[right].circle.state == colour:
            self.total += 1
            self.neighbours(right, "right", colour)
            if self.total > 3:
              return colour


        self.total = 1
        up_left = self.dirs["up_left"](i)
        if i % self.l == 0 or i < self.l:
          pass
        else:
          if self.spaces[up_left].circle.state == colour:
            self.total += 1
            self.neighbours(up_left, "up_left", colour)
            if self.total > 3:
              return colour


        self.total = 1
        up_right = self.dirs["up_right"](i)
        if (i-(self.l-1)) % self.l == 0 or i < self.l:
          pass
        else:
          if self.spaces[up_right].circle.state == colour:
            self.total += 1
            self.neighbours(up_right, "up_right", colour)
            if self.total > 3:
              return colour


        self.total = 1
        down_left = self.dirs["down_left"](i)
        if i > (self.l * (self.w-1))-1 or i % self.l == 0:
          pass
        else:
          if self.spaces[down_left].circle.state == colour:
            self.total += 1
            self.neighbours(down_left, "down_left", colour)
            if self.total > 3:
              return colour


        self.total = 1
        down_right = self.dirs["down_right"](i)
        if (i-(self.l-1)) % self.l == 0 or i > (self.l * (self.w-1))-1:
          pass
        else:
          if self.spaces[down_right].circle.state == colour:
            self.total += 1
            self.neighbours(down_right, "down_right", colour)
            if self.total > 3:
              return colour
        return None
                
      else:
        return None

    else:
      new = self.dirs[direction](i)
      flag = True

      if direction == "up" and i < self.l:
        flag = False
      if direction == "down" and i > (self.l * (self.w-1))-1:
        flag = False
      if direction == "left" and i % self.l == 0:
        flag = False
      if direction == "right" and (i-(self.l-1)) % self.l == 0:
        flag = False
      if direction == "up_left" and (i % self.l == 0 or i < self.l):
        flag = False
      if direction == "up_right" and ((i-(self.l-1)) % self.l == 0 or i < self.l):
        flag = False
      if direction == "down_left" and (i > (self.l * (self.w-1))-1 or i % self.l == 0):
        flag == False
      if direction == "down_right" and ((i-(self.l-1)) % self.l == 0 or i > (self.l * (self.w-1))-1):
        flag = False
      if new > self.l*self.w-1 or new < 0:
        flag = False

      if flag:
        if self.spaces[new].circle.state == colour:
          self.total += 1
          self.neighbours(new, direction, colour)
        else:
          pass
      else:
        pass
        
        
  def check_win(self):
    f = 0
    for i in range(self.l):
      if self.spaces[i].circle.state != "empty":
        f += 1
    if f == self.l:
      return "draw"
  
    for i in range(self.l * self.w):
      win = self.neighbours(i)
      if win == "red" or win == "yellow":
        return win
    else:
      return None
