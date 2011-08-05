#! /usr/bin/env python

import os, sys
import pygame, random

try:
    import android
except ImportError:
    android = None

FPS = 30
TIMEREVENT = pygame.USEREVENT


class SkierClass(pygame.sprite.Sprite):
    def __init__(self, screen, img_path):
        pygame.sprite.Sprite.__init__(self)
        self.img_path = img_path
        self.angle = 0
        self.rect = None
        self.set_image(2+self.angle)
        self.rect.center = [screen.get_width()/2, 100]

    def set_image(self, angle):
      center = None
      if self.rect: 
        center = self.rect.center

      self.image = pygame.image.load(os.path.join(self.img_path, skier_images[angle]))
      self.rect = self.image.get_rect()
      if center:
        self.rect.center = center

    def turn(self, direction):
        self.angle = self.angle + direction
        return self.set_angle(self.angle)

    def set_angle(self, angle):
      self.angle = angle
      if self.angle < -2: self.angle = -2
      if self.angle > 2: self.angle = 2
      return self._calc_speed()

    def _calc_speed(self):
      self.set_image(2+self.angle)
      speed = [self.angle, 6 - abs(self.angle) * 2]
      return speed

    def move(self, speed) :
        self.rect.centerx = self.rect.centerx + speed[0]
        if self.rect.centerx< 20: self.rect.centerx = 20
        if self.rect.centerx > 620: self.rect.centerx = 620
        
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self)
        self.image_file = image_file
        self.image = pygame.image.load(image_file)
        self.location = location
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type
        self.passed = False

    def scroll(self, t_ptr):
        self.rect.centery = self.location[1] - t_ptr

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

        self.clearObstacleGroup()
        self.init()

    def init(self):
        self.setup()
        #self.skier = SkierClass(self.screen, self.img_path)

        self.mp = 0
        self.points = 0
        self.activeMap = 0
        self.density = 1

        self.clearObstacleGroup()

    def clearObstacleGroup(self):
      self.obstacles = pygame.sprite.Group()
      
    def addObstacleGroup(self, oblist):
      for ob in oblist: self.obstacles.add(ob)

    def setup(self):
      self.addAllBricks(self.level)
      self.createPaddle()
      self.count = 0

    def addAllBricks(self, level):
      y = 72

      if level >= 2:
        oblist = self.addBrickRow("red.png", y)
        self.addObstacleGroup(oblist)
      y = y + (self.brick_height+self.border) * 2

      if level >= 1:
        oblist = self.addBrickRow("green.png", y)
        self.addObstacleGroup(oblist)
      y = y + (self.brick_height+self.border) * 2

      oblist = self.addBrickRow("blue.png", y)
      self.addObstacleGroup(oblist)
      y = y + (self.brick_height+self.border) * 2

    def addBrickRow(self, brickColor, y):
      obstacles = pygame.sprite.Group()

      img = os.path.join(self.img_path, brickColor)
      type = "brick"
      
      dx = (self.brick_width + self.brick_border)
      
      for i in range(2):
        for j in range(10):
          location = [self.border + j*dx + (self.brick_width/2), y]
          r = ObstacleClass(img, location, type)
          obstacles.add(r)
          
        y = y + self.brick_height + self.brick_border
      return obstacles

    def createPaddle(self):
      location = [self.screen_width/2, self.screen_height-50]
      self.paddle = ObstacleClass(os.path.join(self.img_path, "paddle.png"), 
                                  location, "paddle")

            
    def animate(self, flip=True):
        self.screen.fill([0,0,0])
        pygame.display.update(self.obstacles.draw(self.screen))

        mouse_pos = pygame.mouse.get_pos()
        self.paddle.rect.x = mouse_pos[0]
        
        self.screen.blit(self.paddle.image, self.paddle.rect)

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
        again_text = self.font.render("Press any key to play again", 1, (0,0,0))

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
            
            text = self.font.render("Game Over", 1, (0,0,0))
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
              
              x = a[0]
              if abs(x) < 1:
                self.speed = self.skier.set_angle(0)
              elif x > 3:
                self.speed = self.skier.set_angle(-2)
              elif x > 1:
                self.speed = self.skier.set_angle(-1)
              elif x < -3:
                self.speed = self.skier.set_angle(2)
              elif x < -1:
                self.speed = self.skier.set_angle(1)

            self.density = 1 + self.points/100
            self.score_text = self.font.render("Score: " + str(self.points), 1, (255,255,255))
            self.animate()

def main():
  pygame.init()

  screen = pygame.display.set_mode([480, 800])

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
