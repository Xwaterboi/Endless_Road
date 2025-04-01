import pygame
import random


car_image = pygame.image.load('pics\car.png')
obstacle_image = pygame.image.load('pics\obstacle.png')


# Constants
LANEWIDTH = 80
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 400

# Car Sprite
class Car(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = pygame.image.load('pics/car.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 100))  # Scale to the appropriate size
        self.rect = self.image.get_rect()
        self.lane = lane
        self.update()

    def update(self):
        self.rect.x = self.lane * LANEWIDTH + (LANEWIDTH - self.rect.width) // 2  # Center in lane
        self.rect.y = WINDOW_HEIGHT - self.rect.height - 110  # Position at bottom with some padding
        #print(f"Car position: x={self.rect.x}")#, y={self.rect.y}
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Obstacle Sprite
class Obstacle(pygame.sprite.Sprite):
    # Static image that will be shared by all obstacles
    OBSTACLE_IMAGE = None

    def __init__(self):
        super().__init__()
        # Load the image only once for all instances
        if Obstacle.OBSTACLE_IMAGE is None:
            Obstacle.OBSTACLE_IMAGE = pygame.image.load('pics\obstacle.png').convert_alpha()
            Obstacle.OBSTACLE_IMAGE = pygame.transform.scale(Obstacle.OBSTACLE_IMAGE, (50, 50))
        
        # Use the static image for this instance
        self.image = Obstacle.OBSTACLE_IMAGE
        self.rect = self.image.get_rect()
        self.lane = random.randint(0, 4)
        self.rect.x = self.lane * LANEWIDTH + (LANEWIDTH - self.rect.width) // 2
        self.rect.y = -100
        self.speed = 5

    def update(self):
        self.rect.y += self.speed  # Move the obstacle down
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()  # Remove the sprite when it moves out of the screen

# Good Point Sprite
class GoodPoint(pygame.sprite.Sprite):
    # Static image that will be shared by all coins
    COIN_IMAGE = None
    indecis = [None]*5

    def __init__(self):
        super().__init__()
        # Load the image only once for all instances
        if GoodPoint.COIN_IMAGE is None:
            GoodPoint.COIN_IMAGE = pygame.image.load('pics\coin.png').convert_alpha()
        self.image = GoodPoint.COIN_IMAGE
        self.rect = self.image.get_rect()
        self.lane = random.randint(0, 4)
        self.rect.x = self.lane * LANEWIDTH + (LANEWIDTH - self.rect.width) // 2
        self.rect.y = -100
        self.speed = 5
        self.index = GoodPoint.indecis.index(None)
        GoodPoint.indecis[self.index] = self

    def update(self):
        self.rect.y += self.speed  # Move the good point down
        
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()  # Remove the sprite when it moves out of the screen

    def kill(self):
        GoodPoint.indecis[self.index] = None
        super().kill()

