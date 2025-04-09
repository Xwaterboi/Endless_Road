import pygame
import sprites
from graphics import Background
import random
from Environment import Environment

from ReplayBuffer import ReplayBuffer
from AI_Agent import AI_Agent
from DQN import DQN
import torch
import wandb
import os
def main ():

    pygame.init()
    
    
    
    #CONSTS
    FPS = 60
    WINDOWWIDTH = 400
    WINDOWHEIGHT = 800
    MIN_BUFFER=500
    MODEL_PATH = "model/DQN.pth"  # Ensure cross-platform path
    #clock = pygame.time.Clock()
    background = Background(WINDOWWIDTH, WINDOWHEIGHT) 
    env = Environment()
    background.render(env)
    best_score = 0
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        device = torch.device('cuda')
        print("CUDA")
        scaler = torch.amp.GradScaler('cuda')
    else:
        device = torch.device('cpu')
        print("CPU")
        scaler = None
    
    ####### params and models ############
    dqn_model = DQN(device=device)
    # Comment out this line if starting fresh training and uncomment the next line
    dqn_model.load_params(MODEL_PATH)
    #dqn_model.save_params(MODEL_PATH)
    print("Model loaded successfully!")
    player = AI_Agent(dqn_model,device=device)
    player_hat = AI_Agent(dqn_model,device=device)
    player_hat.dqn_model = player.dqn_model.copy()
    batch_size = 128
    buffer = ReplayBuffer(path=None)
    learning_rate = 0.001
    ephocs = 200000
    start_epoch = 0
    C = 5
    loss = torch.tensor(0)
    avg = 0
    scores, losses, avg_score = [], [], []
    optim = torch.optim.Adam(player.dqn_model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.StepLR(optim,5*100, gamma=0.97)
    # scheduler = torch.optim.lr_scheduler.MultiStepLR(optim, 
    #     milestones=[1000, 2000, 4000, 8000, 16000,32000,48000,64000,80000,96000,112000,128000,144000,160000 ], 
    #     gamma=0.6)
    step = 0

    ######### checkpoint Load ############
    num = 30
    checkpoint_path = f"Data/checkpoint{num}.pth"
    buffer_path = f"Data/buffer{num}.pth"
    resume_wandb = False
    if os.path.exists(checkpoint_path):
        resume_wandb = True
        checkpoint = torch.load(checkpoint_path)
        start_epoch = checkpoint['epoch']+1
        player.dqn_model.load_state_dict(checkpoint['model_state_dict'])
        player_hat.dqn_model.load_state_dict(checkpoint['model_state_dict'])
        optim.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        buffer = torch.load(buffer_path)
        losses = checkpoint['loss']
        scores = checkpoint['scores']
        avg_score = checkpoint['avg_score']
    player.dqn_model.train()
    player_hat.dqn_model.eval()
    
    ################# Wandb.init #####################
    
    wandb.init(
        # set the wandb project where this run will be logged
        project="Endless_Road",
        resume=resume_wandb, 
        id=f'Endless_Road {num}',
        # track hyperparameters and run metadata
        config={
        "name": f"Endless_Road {num}",
        "checkpoint": checkpoint_path,
        "learning_rate": learning_rate,
        #"Schedule": f'{str(scheduler.milestones)} gamma={str(scheduler.gamma)}',
        #"Schedule": f'step_size={str(scheduler.step_size)} gamma={str(scheduler.gamma)}',
        "epochs": ephocs,
        "start_epoch": start_epoch,
        "decay": 50,
        "gamma": 0.99,
        "batch_size": batch_size, 
        "C": C,
        "Model":str(player.dqn_model),
        "device": str(device)
        }
    )
    wandb.config.update({"Model":str(player.dqn_model)}, allow_val_change=True)
    
    #################################

    for epoch in range(start_epoch, ephocs):
        step = 0
        #clock = pygame.time.Clock()
        background = Background(WINDOWWIDTH, WINDOWHEIGHT)
        env = Environment()
        background.render(env)

        end_of_game = False
        state = env.state()
        
        while not end_of_game:
            step += 1
            pygame.event.pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    checkpoint = {
                        'epoch': epoch,
                        'model_state_dict': player.dqn_model.state_dict(),
                        'optimizer_state_dict': optim.state_dict(),
                        'scheduler_state_dict': scheduler.state_dict(),
                        'loss': losses,
                        'scores':scores,
                        'avg_score': avg_score
                    }
                    torch.save(checkpoint, checkpoint_path)
                    torch.save(buffer, buffer_path)
                    return
            
            ############## Sample Environement #########################
            action = player.getAction(state=state, epoch=epoch)
            
            done,reward = env.update(action)
            # if env.score>=5:
            #     reward=5
            #     break
            next_state = env.state()
            buffer.push(state, torch.tensor(action, dtype=torch.int64), torch.tensor(reward, dtype=torch.float32), 
                        next_state, torch.tensor(done, dtype=torch.float32))
            if done:
                best_score = max(best_score, env.score)
                break
            else:
                background.render(env)
            #print(state)
            state = next_state

            
            pygame.display.flip()
            # clock.tick(FPS)
            
            if len(buffer) < MIN_BUFFER:
                continue
    
            ############## Train ################
            states, actions, rewards, next_states, dones = buffer.sample(batch_size)
            #Q_values = player.Q(states, actions)
            # next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states) # DDQ
            # loss = player.dqn_model.loss(Q_values, rewards, Q_hat_Values, dones)
            # loss.backward()
            #  torch.nn.utils.clip_grad_norm_(player.dqn_model.parameters(), max_norm=1.0)
            # optim.step()
            # optim.zero_grad()
            

            #this is so the gpu will be faster, and also cpu will be compatible
            if scaler is not None:
                with torch.amp.autocast('cuda'):
                    Q_values = player.Q(states, actions)
                    next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)#ddqn
                    loss = player.dqn_model.loss(Q_values, rewards, Q_hat_Values, dones)
                scaler.scale(loss).backward()
                torch.nn.utils.clip_grad_norm_(player.dqn_model.parameters(), max_norm=1.0)

                scaler.step(optim)
                scaler.update()
                optim.zero_grad()
                
            else:
                Q_values = player.Q(states, actions)
                next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)
                loss = player.dqn_model.loss(Q_values, rewards, Q_hat_Values, dones)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(player.dqn_model.parameters(), max_norm=1.0)
                optim.step()
                optim.zero_grad()
        #after game ends, step.
        scheduler.step()
        if epoch % C == 0:
            # player_hat.dqn_model.load_state_dict(player.dqn_model.state_dict())
            player_hat.fix_update(dqn=player.dqn_model)
            # player_hat.soft_update(dqn_model=player.dqn_model, tau=tau)

        #########################################
        print (f'epoch: {epoch} loss: {loss:.7f} LR: {scheduler.get_last_lr()}  ' \
               f'score: {env.score} step {step} ')
        
        if epoch % 10 == 0:
            scores.append(env.score)
            losses.append(loss.item())
        wandb.log ({
                "score": env.score,
                "loss": loss.item(),
                "step":step
            })
        step = 0
        avg = (avg * (epoch % 10) + env.score) / (epoch % 10 + 1)
        if (epoch + 1) % 10 == 0:
            avg_score.append(avg)
            wandb.log ({
                # "score": env.score,
                # "loss": loss.item(),
                "avg_score": avg
            })
            print (f'average score last 10 games: {avg} ')
            avg = 0

        if epoch % 1000 == 0 and epoch > 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': player.dqn_model.state_dict(),
                'optimizer_state_dict': optim.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': losses,
                'scores':scores,
                'avg_score': avg_score
            }
            torch.save(checkpoint, checkpoint_path)
            torch.save(buffer, buffer_path)





        
if __name__ == "__main__":
    main ()