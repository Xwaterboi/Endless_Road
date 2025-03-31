from sprites import *
import torch
class Environment:
    def __init__(self) -> None:
        self.car = Car(2)
        self.obstacles_group = pygame.sprite.Group()
        self.good_points_group= pygame.sprite.Group()
        #self.spawn_timer = 0
        self.score=0
        GoodPoint.indecis = [None] * 5


    def move (self, action):#checks if action  Is Legal Move
        lane = self.car.lane
        if action == 1 and lane < 4:
            self.car.lane +=1
            
        if action == -1 and lane > 0:
            self.car.lane -=1

    def _check_obstacle_placement(self, obstacle):
        collided = pygame.sprite.spritecollide(obstacle, self.obstacles_group, False)
        collided2 = pygame.sprite.spritecollide(obstacle, self.good_points_group, False)
        return len(collided) == 0 and len(collided2) == 0  # Return True if no collisions
    
    def Max_obstacle_check(self):
        """Checks if there are more than 10 obstacles in the game."""
        if len(self.obstacles_group) >= 4:
            return True  # More than 10 obstacles exist
        else:
            return False # 10 or fewer obstacles exist
            
    def Max_GoodPoints_check(self):
        """Checks if there are more than 10 good points in the game."""
        if len(self.good_points_group) >= 5:
            return True  # More than 5 points exist
        else:
            return False # 5 or fewer points exist
        
    def add_obstacle(self):
        spawn_probability = 0.01  #CHANGE
        if random.random() < spawn_probability:
            obstacle = Obstacle()
            #obstacle.rect.x = random.randrange(0, 400, 80)
            obstacle.rect.y = -obstacle.rect.height  # Spawn at the top of the screen
            if self._check_obstacle_placement(obstacle) and self.Max_obstacle_check() is False:
                self.obstacles_group.add(obstacle)


    def add_coins (self):                                                           ###### Gilad
        # Spawn good points (optional)
        spawn_good_point_probability = 0.015 #CHANGE  
        if random.random() < spawn_good_point_probability and len(self.good_points_group) < 5:
            good_point = GoodPoint()
            if self._check_obstacle_placement(good_point):
                self.good_points_group.add(good_point)
            else:
                good_point.kill()

    def car_colide(self) -> bool :
        colides = pygame.sprite.spritecollide(self.car,self.obstacles_group,False)
        return len(colides) ==0

    def AddGood(self):
        # pointCollided=pygame.sprite.spritecollide(self.car,self.good_points_group,True)
        # if len(pointCollided) != 0:
        #     self.score+=1
        # Custom collision detection for coins
        if len(pygame.sprite.spritecollide(self.car,self.good_points_group,True)) !=0:
             self.score += 1  # Increment the score
             return True
        return False
        # for sprite in self.good_points_group:
        #     rect = sprite.rect

    def reset(self):#for AI, we dont need screen,  print is good enough.
        from game import game
        print(self.score)
        game.loop()

    def state(self):
        state_list = []

        # 1. Car's Lane
        state_list.append((self.car.lane+1)/10)  # Add the car's lane 0-4

        # 2. Obstacle Positions
        for obstacle in self.obstacles_group:
            state_list.append((obstacle.lane+1)/10)  # X-coordinate of obstacle
            state_list.append(obstacle.rect.y/700)  # Y-coordinate of obstacle
        while (len(state_list)<9):
            state_list.append(0)  
            state_list.append(0)  
        # 3. Good Point Positions
        for good_point in GoodPoint.indecis:
            if good_point:
                state_list.append((good_point.lane+1)/10)  # X-coordinate of good point
                state_list.append(good_point.rect.y/700)  # Y-coordinate of good point
            else:   
                state_list.append(0)  
                state_list.append(0)  
        return torch.tensor(state_list, dtype=torch.float32)
    def Lane_Reward(self,lane=None):#calculate reward based on the lane the car is in, helps in vision for the AI agent
        if lane is None:lane=self.car.lane
        reward= -0.1
        Obstacles_In_Lane=[]
        for obstacle in self.obstacles_group:
            if obstacle.lane == lane:
                Obstacles_In_Lane.append(obstacle.rect.y)
        if not Obstacles_In_Lane:  # If no obstacles in lane
            closest_obstacle = 0
            reward=0.1
        else:
            closest_obstacle = min(Obstacles_In_Lane)
        for good_point in self.good_points_group:
            if good_point.rect.y>closest_obstacle:# i put > because as the good point goes down, her y goes up. 
                reward+=0.33#need to expirment with this value
        return reward
    
    def update (self,action):
        self.reward=0
        prev_lane=self.car.lane
        self.move(action=action)
        if self.car.lane != prev_lane:
            self.reward=self.reward-0.01#car change lane reward
        ### Add obstacles and coins to screen
        self.add_obstacle()
        self.add_coins()
        ###
        ### Update game objects
        self.car.update()
        self.obstacles_group.update()
        self.good_points_group.update()
        ###
        self.reward+=self.Lane_Reward(self.car.lane)
        if(self.AddGood()):self.reward+=7#coin reward
        if not self.car_colide():return (True,-5)#lose reward
        ### Remove off screen obstacles and coins
        for obstacle in self.obstacles_group:
            if obstacle.rect.top > 800 :
                obstacle.kill()
                self.obstacles_group.remove(obstacle)
        for GoodPoint in self.good_points_group:

            if GoodPoint.rect.top > 800 :
                GoodPoint.kill()
                self.good_points_group.remove(GoodPoint)
        ### 
        return (False,self.reward)

                 
        
        

    

