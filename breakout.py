#! /usr/bin/env python

import os, sys
import pygame, random

try:
    import android
except ImportError:
    android = None

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

FPS = 15
TIMEREVENT = pygame.USEREVENT

class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self)
        self.image_file = image_file
        self.image = pygame.image.load(image_file)
        self.location = location
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type

class BallClass(ObstacleClass):
  def __init__(self, image_file, location, type):
    ObstacleClass.__init__(self, image_file, location, type)
    self.vx = 5.0
    self.vy = 5.0

  def move(self, screen):
    self.rect.x = self.rect.x + self.vx
    self.rect.y = self.rect.y + self.vy

    if self.rect.x < screen.border: 
      self.rect.x = screen.border
      self.vx = -self.vx
    elif self.rect.x > screen.screen_width - screen.border: 
      self.rect.x = screen.screen_width - screen.border
      self.vx = -self.vx
    

class Game:
    def __init__(self, screen, img_path):
        self.img_path = img_path
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()

        self.brick_width = 45
        self.brick_height = 20
        self.border = 5
        self.brick_border = 2

        self.font = pygame.font.Font("freesansbold.ttf", 30)

        self.debug_text = ""
        self.score_text = None

        self.level = 0
        self.paddle = None
        self.ball = None

        self.splat = mixer.Sound("whistleup.wav")

        self.clearObstacleGroup()

    def init(self):
        self.setup()

        self.points = 0

    def clearObstacleGroup(self):
      self.obstacles = pygame.sprite.Group()
      
    def addObstacleGroup(self, oblist):
      for ob in oblist: self.obstacles.add(ob)

    def setup(self):
      self.clearObstacleGroup()
      self.addAllBricks(self.level)
      self.createPaddle()
      self.createBall()
      
    def addAllBricks(self, level):
      y = 72

      if level >= 2:
        oblist, y = self.addBrickRow("red.png", y, 4)
        self.addObstacleGroup(oblist)

      if level >= 1:
        oblist, y = self.addBrickRow("green.png", y, 4)
        self.addObstacleGroup(oblist)
        
      oblist, y = self.addBrickRow("blue.png", y, 4)
      self.addObstacleGroup(oblist)
      

    def addBrickRow(self, brickColor, y, rows):
      obstacles = pygame.sprite.Group()

      img = os.path.join(self.img_path, brickColor)
      type = "brick"
      
      dx = (self.brick_width + self.brick_border)
      
      for i in range(rows):
        for j in range(10):
          location = [self.border + j*dx + (self.brick_width/2), y]
          r = ObstacleClass(img, location, type)
          obstacles.add(r)
          
        y = y + self.brick_height + self.brick_border
      return obstacles, y

    def createPaddle(self):
      location = [self.screen_width/2, self.screen_height-50]
      self.paddle = ObstacleClass(os.path.join(self.img_path, "paddle.png"), 
                                  location, "paddle")
      self.obstacles.add(self.paddle)


    def createBall(self):
      location = [self.screen_width/2, 300]
      self.ball = BallClass(os.path.join(self.img_path, "ball.png"), 
                            location, "ball")

            
    def animate(self, flip=True):
        self.screen.fill([0,0,0])

        if self.paddle:
          mouse_pos = pygame.mouse.get_pos()
          self.paddle.rect.x = mouse_pos[0]

        pygame.display.update(self.obstacles.draw(self.screen))

        if self.ball:
          self.ball.move(self)
          self.screen.blit(self.ball.image, self.ball.rect)

        if self.score_text:
          self.screen.blit(self.score_text, [10, 10])

        if self.debug_text:
          text = self.font.render(self.debug_text, 1, (255,255,255))
          self.screen.blit(text, [10, self.screen_height-60])

        if flip:
            pygame.display.flip()


    def startScreen(self):
        self.addAllBricks(10)
      
        self.screen.fill([0,0,0])
        pygame.display.update(self.obstacles.draw(self.screen))

        title_text = self.font.render("Break the Ceiling", 1, (255,255,255))
        again_text = self.font.render("Touch here to start", 1, (255,255,255))

        pygame.display.flip()

        while 1:
          self.clock.tick(1000/FPS)
          if android:
            if android.check_pause():
              android.wait_for_resume()
          for event in pygame.event.get():
            if event.type == pygame.QUIT: 
              return False
            if event.type == pygame.MOUSEBUTTONUP:
              return True
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE:
                return False
              else:
                return True


          self.animate(False)
          rect = title_text.get_rect()
          self.screen.blit(title_text, [(self.screen_width - rect[2])/2, (self.screen_height - rect[3])/2])
          rect = again_text.get_rect()   
          self.screen.blit(again_text, [(self.screen_width - rect[2])/2, (self.screen_height - 100)])

          pygame.display.flip()
          pygame.time.delay(500)

          self.animate(False)

          rect = title_text.get_rect()
          self.screen.blit(title_text, [(self.screen_width - rect[2])/2, (self.screen_height - rect[3])/2])

          pygame.display.flip()
          pygame.time.delay(500)


    def gameOver(self):
        again_text = self.font.render("Press any key to play again", 1, (255,255,255))
        self.paddle = None

        while 1:
            if android:
              if android.check_pause():
                android.wait_for_resume()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                  return False
                if event.type == pygame.MOUSEBUTTONUP:
                  return True
                if event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_ESCAPE:
                    return False
                  else:
                    return True
            
            text = self.font.render("Game Over", 1, (255,255,255))
            rect = text.get_rect()

            self.animate(False)
            self.screen.blit(text, [(self.screen_width - rect[2])/2, (self.screen_height - rect[3])/2])
            rect = again_text.get_rect()   
            self.screen.blit(again_text, [(self.screen_width - rect[2])/2, (self.screen_height - 100)])

            pygame.display.flip()

            pygame.time.delay(500)
       
            self.animate(False)
            rect = again_text.get_rect()   
            self.screen.blit(again_text, [(self.screen_width - rect[2])/2, (self.screen_height - 100)])
            pygame.display.flip()

            pygame.time.delay(500)

        pygame.quit()
        sys.exit(0)

    def play(self):
        while True:
            self.clock.tick(1000/FPS)
          
            # Android-specific:
            if android:
              if android.check_pause():
                android.wait_for_resume()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                  return False
                
                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                          pass
                        elif event.key == pygame.K_RIGHT:
                          pass
                        elif event.key == pygame.K_ESCAPE:
                          return True

            if android:
              a = android.accelerometer_reading()
              #self.debug_text = "%f" % a[0]

            ## did the ball hit a brick or paddle?
            hit = pygame.sprite.spritecollide(self.ball, self.obstacles, False)
            if hit:
              if hit[0].type == "paddle":
                self.ball.vy = -self.ball.vy
              elif hit[0].type == "brick":
                self.ball.vy = -self.ball.vy
                self.points = self.points + 10
                self.obstacles.remove(hit)
                self.splat.play()

            ## did the ball hit the top of the screen?
            if self.ball.rect.y < self.border:
              self.ball.vy = self.ball.vy * 1.5
              self.ball.vy = -self.ball.vy

            ## did the ball hit the bottom of the screen?
            if self.ball.rect.y > self.screen_height:
              return True

            self.score_text = self.font.render("Score: " + str(self.points), 1, (255,255,255))
            self.animate()

def main():
  pygame.init()
  mixer.init()

  screen = pygame.display.set_mode([480, 700])

  if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
    android.accelerometer_enable(True)

  game = Game(screen, "images")

  ret = game.startScreen()

  if ret == False:
    pygame.quit()
    sys.exit(1)

  while 1:
    game.init()
    ret = game.play()
    if ret == False:
      pygame.quit()
      sys.exit(1)

    ret = game.gameOver()
    if ret == False:
      pygame.quit()
      sys.exit(1)

# This isn't run on Android.
if __name__ == "__main__":
    main()
