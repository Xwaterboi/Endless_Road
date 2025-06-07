import pygame
import numpy as np
from graphics import Background
from Environment import Environment
from ReplayBuffer import ReplayBuffer
#from ReplayBuffer_n_step import ReplayBuffer_n_step as ReplayBuffer
from AI_Agent import AI_Agent
#from AI_Agent_No_Exp import AI_Agent
#from AI_Agent_softmax import AI_Agent
# from DuelingDQN import DQN
# from DQN import DQN
from DQN_Attension import DQN
from Tester import Tester
import torch
import wandb
import os
def main (chkpt):

    pygame.init()
    
    #CONSTS
    FPS = 60
    WINDOWWIDTH = 400
    WINDOWHEIGHT = 800
    MIN_BUFFER=500
    MODEL_PATH = f"model/DQN{chkpt}.pth"  # Modified to include checkpoint number
    OLD_MODEL_PATH = f"model/DQN{463}.pth"  # Modified to include checkpoint number
    clock = pygame.time.Clock()
    background = Background(WINDOWWIDTH, WINDOWHEIGHT) 
    env = Environment(chkpt)
    best_score = 0
      
    #region###### params and models ############
    device=torch.device('cpu')
    #device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dqn_model = DQN(device=device)
    #dqn_model.load_params(MODEL_PATH)
    #print("Model loaded successfully!")
    player = AI_Agent(dqn_model,device=device)
    player_hat = AI_Agent(dqn_model,device=device)
    player_hat.dqn_model = player.dqn_model.copy()
    batch_size = 128
    buffer = ReplayBuffer(path=None)
    learning_rate = 3e-4
    ephocs = 2000
    start_epoch = 0
    C = 5
    loss = torch.tensor(0)
    avg = 0

    scores, losses, avg_score = [], [], []
    # optim = torch.optim.Adam(player.dqn_model.parameters(), lr=learning_rate, weight_decay=1e-4)
    optim = torch.optim.AdamW(player.dqn_model.parameters(), lr=learning_rate, weight_decay=1e-3)
    # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[1000*200, 3000*200, 5000*200], gamma=0.9)
    step = 0
    #endregion
    #region######## checkpoint Load ############
    num = chkpt
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
    #endregion
    #region################ Wandb.init #####################
    
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
        "Schedule": f'{str(scheduler.milestones)} gamma={str(scheduler.gamma)}',
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
    #endregion
        
    tester = Tester(player,env)

    for epoch in range(start_epoch, ephocs):
        
        step = 0
        clock = pygame.time.Clock()
        env.new_game()
        background.render(env,IsTrainer=True)

        end_of_game = False
        state = env.state()
        
        while not end_of_game:
            # clock.tick(60)
            step += 1
            print(step, end="\r")
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
                    # Save the DQN model separately with checkpoint number
                    torch.save(player.dqn_model.state_dict(), MODEL_PATH)
                    pygame.quit()
                    return
            
            ############## Sample Environement #########################
            action = player.getAction(state=state, epoch=epoch, train=True)
            done,reward = env.update(action)
            next_state = env.state()
            imediate_reward = env.immediate_reward_simple (state, action)
            reward += imediate_reward
            buffer.push(state, torch.tensor(action, dtype=torch.int64), torch.tensor(reward, dtype=torch.float32), 
                        next_state, torch.tensor(done, dtype=torch.float32))
            if done:
                best_score = max(best_score, env.score)
                # background.render(env)
                break
            else:
                background.render(env,IsTrainer=True)

            state = next_state
            
            
            if len(buffer) < MIN_BUFFER:
                continue
    
            ############## Train ################
            states, actions, rewards, next_states, dones = buffer.sample(batch_size)
            Q_values = player.Q(states, actions)

            next_actions, _ = player.get_Actions_Values(next_states)
            Q_hat_Values = player_hat.Q(next_states,next_actions) # DDQN
            
            # _, Q_hat_Values = player_hat.get_Actions_Values(next_states) # DQN
            

            loss = player.dqn_model.loss(Q_values, rewards, Q_hat_Values, dones)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(player.dqn_model.parameters(), max_norm=1.0)
            optim.step()
            # if epoch % C==0:
            #     with torch.no_grad():
            #         weights=torch.abs(player.dqn_model.level_embedding.weight.data.view(-1))
            #         sorted_weights, _ = torch.sort(weights)
            #         player.dqn_model.level_embedding.weight.data.copy_(sorted_weights.view(-1, 1))
            optim.zero_grad()
            scheduler.step()

        if epoch % C == 0:
            player_hat.fix_update(dqn=player.dqn_model)
            

        #region log & print########################################
        rounded_np = np.round(player.dqn_model.level_embedding.weight.detach().cpu().numpy(), 4).squeeze()
        clean_list = [round(float(v), 4) for v in rounded_np.tolist()]

        print (f'chkpt: {num} epoch: {epoch} loss: {loss:.7f} LR: {scheduler.get_last_lr()[0]:.6f}  ',
               f'score: {round(env.score,1)} step {step}', 
               f'embedding: {clean_list}')
        
        wandb.log ({
                "score": env.score,
                "loss": loss.item(),
                "step":step
            })
        
        

        if epoch % 500 == 0 and epoch > 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': player.dqn_model.state_dict(),
                'optimizer_state_dict': optim.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
            }
            torch.save(checkpoint, checkpoint_path)
            torch.save(buffer, buffer_path)
            # Save the DQN model separately with checkpoint number every 500 epochs
            torch.save(player.dqn_model.state_dict(), MODEL_PATH)
            
        #endregion

    # Save the final DQN model at the end of training
    torch.save(player.dqn_model.state_dict(), MODEL_PATH)
     
if __name__ == "__main__":
    if not os.path.exists("Data/checkpoit_num"):
        torch.save(460, "Data/checkpoit_num")    
    
    chkpt = torch.load("Data/checkpoit_num", weights_only=False)
    chkpt +=1
    torch.save(chkpt, "Data/checkpoit_num")    
    main (chkpt)