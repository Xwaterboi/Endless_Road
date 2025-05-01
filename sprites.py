import pygame
import random


# Constants
LANEWIDTH = 80
WINDOW_HEIGHT = 800
SURFACE_HEIGHT = WINDOW_HEIGHT - 100
WINDOW_WIDTH = 400

# Car Sprite
class Car(pygame.sprite.Sprite):
    
    pic = pygame.image.load('pics/car.png')
    
    def __init__(self, lane):
        super().__init__()
        self.image = Car.pic.convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 100))  # Scale to the appropriate size
        self.rect = self.image.get_rect()
        self.rect.y = SURFACE_HEIGHT - self.rect.height - 10 # Position at bottom with some padding
        self.lane = lane
        self.update()

    def update(self):
        self.rect.x = self.lane * LANEWIDTH + (LANEWIDTH - self.rect.width) // 2  # Center in lane
        
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Obstacle Sprite
class Obstacle(pygame.sprite.Sprite):
    pic=pygame.image.load('pics/obstacle2.png')
    pics = [pygame.image.load('pics/obstacle.png'),pygame.image.load('pics/obstacle2.png'),pygame.image.load('pics/obstacle3.png')]
    
    def __init__(self,speed):
        super().__init__()
        self.pic=Obstacle.pics[random.randint(0,2)]
        self.image = self.pic.convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # Load obstacle image
        self.rect = self.image.get_rect()
        self.lane=random.randint(0, 4)
        self.rect.x =  self.lane* LANEWIDTH    + (LANEWIDTH - self.rect.width) // 2 # Random lane
        self.rect.y = 0  #above the screen
        self.speed = speed  # Speed at which the obstacle moves down

    def update(self):
        self.rect.y += self.speed  # Move the obstacle down
        if self.rect.top > SURFACE_HEIGHT:
            self.kill()  # Remove the sprite when it moves out of the screen

# Good Point Sprite
class GoodPoint(pygame.sprite.Sprite):

    indecis = [None]*5
    
    pics = [pygame.image.load('pics/coin.png'),pygame.image.load('pics/coin2.png'),pygame.image.load('pics/coin3.png')]
    
    def __init__(self,speed):
        super().__init__()
        self.pic=GoodPoint.pics[random.randint(0,2)]
        self.image = self.pic.convert_alpha()  # Load good point image
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.lane=random.randint(0, 4)
        self.rect.x = self.lane * LANEWIDTH + (LANEWIDTH - self.rect.width) // 2  # Random lane
        self.rect.y = 0  # Random height above the screen; random.randint(-200, -50)
        self.speed = speed  # Speed at which the good point moves down
        self.index = GoodPoint.indecis.index(None)
        GoodPoint.indecis[self.index] = self

    def update(self):
        self.rect.y += self.speed  # Move the good point down
        
        if self.rect.top > SURFACE_HEIGHT:
            self.kill()  # Remove the sprite when it moves out of the screen

    def kill(self):
        GoodPoint.indecis[self.index] = None
        super().kill()

