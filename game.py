import pygame
import sprites
from graphics import Background
import random
from Environment import Environment
from Start_menu import MenuScreen
from Human_Agent import Human_Agent
# from Random_Agent import Random_Agent
from AI_Agent import AI_Agent
from DQN_Attension import DQN
import torch
pygame.init()

# Constants
FPS = 60
WINDOWWIDTH = 400
WINDOWHEIGHT = 800
MODEL_PATH = None # "model/DQN.pth"  # Ensure cross-platform path

clock = pygame.time.Clock()
background = Background(WINDOWWIDTH, WINDOWHEIGHT)

# Initialize environment and model
env = Environment()
background.render(env)

# Load DQN model
dqn_model = DQN()

if MODEL_PATH:
    dqn_model.load_params(MODEL_PATH)
    print("Model loaded successfully!")


# player = AI_Agent(dqn_model)

class Game:
    def __init__(self):
        pass

    def start_new_game(self):
        """Start a new game session."""
        self.loop()

    def loop(self):
        """Main game loop."""
        #self.score = 0
        startscreen=MenuScreen(WINDOWWIDTH, WINDOWHEIGHT)
        self.settings=startscreen.run()
        background = Background(WINDOWWIDTH, WINDOWHEIGHT)
        env = Environment(diff=self.settings['difficulty'])
        background.render(env)
        
        # Keep the same AI agent instance
        if self.settings['agent_type']=='AI':
            player = AI_Agent(dqn_model=dqn_model,train=False)
            playertype=1
        else:
            player= Human_Agent()
            playertype=2
        self.duration = 30000
        start_time = pygame.time.get_ticks()

        run = True
        win = False

        while run:
            dt = clock.tick(FPS)
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    exit()

            elapsed_time = pygame.time.get_ticks() - start_time

            if env.score >= 5:
                print("5 points! You win!")
                win = True

            state = env.state()
            if playertype ==1:
                action = player.getAction(events=events, state=env.state())#AI
            else: 
                action=player.getAction(events=events)#human
            #env.move(action=action)
            done,reward = env.update(action=action) or win

            if done:
                
                
                if  playertype==2:
                    play_again = background.end_screen()
                    print(f"Score: {env.score}")
                    if play_again ==1:
                        self.start_new_game()  
                else:
                    print(f"Score: {env.score}")
                    self.start_new_game()

                
            else:
                background.render(env)

            pygame.display.flip()

        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.start_new_game()


