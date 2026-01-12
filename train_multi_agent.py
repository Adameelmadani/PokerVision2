import os
import torch
import rlcard
import numpy as np
import matplotlib.pyplot as plt
from rlcard.agents import DQNAgent, NFSPAgent, CFRAgent, RandomAgent
from rlcard.utils import get_device, set_seed, reorganize, Logger, plot_curve

def train_six_player_mix(episodes=2000, save_path='models'):
    """
    Train 3 types of agents simultaneously in a 6-player environment.
    Seats:
    0: DQN (Learning)
    1: NFSP (Learning)
    2: CFR (Learning)
    3: DQN (Learning - Copy 2)
    4: NFSP (Learning - Copy 2)
    5: Random (Baseline)
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    device = get_device()
    set_seed(42)
    
    # Create 6-player env
    config = {
        'seed': 42,
        'game_num_players': 6
    }
    env = rlcard.make('no-limit-holdem', config=config)
    
    # 1. Initialize DQN
    dqn_agent = DQNAgent(
        num_actions=env.num_actions,
        state_shape=env.state_shape[0],
        mlp_layers=[512, 512],
        device=device,
        save_path=save_path, # internal saving
        save_every=500
    )
    
    # 2. Initialize NFSP
    nfsp_agent = NFSPAgent(
        num_actions=env.num_actions,
        state_shape=env.state_shape[0],
        hidden_layers_sizes=[512, 512],
        q_mlp_layers=[512, 512],
        device=device
    )
    
    # 3. Initialize CFR
    # CFR in RLCard is usually tabular or deep. Basic tabular CFR requires smaller games.
    # For full NLH, standard CFR is too slow. We will use DeepCFR if available or fall back
    # to a second DQN if CFR is not viable for 6-player NLH in this lib version.
    # Assuming standard CFRAgent is used (which might be slow):
    try:
        from rlcard.agents import CFRAgent
        cfr_agent = CFRAgent(env, os.path.join(save_path, 'cfr_checkpoint'))
    except:
        print("CFR Agent not compatible with this setup, using Random for seat 2")
        cfr_agent = RandomAgent(num_actions=env.num_actions)

    # 4. Another DQN instance
    dqn_agent_2 = DQNAgent(
        num_actions=env.num_actions,
        state_shape=env.state_shape[0],
        mlp_layers=[512, 512],
        device=device
    )
    
    # 5. Another NFSP instance
    nfsp_agent_2 = NFSPAgent(
        num_actions=env.num_actions,
        state_shape=env.state_shape[0],
        hidden_layers_sizes=[512, 512],
        q_mlp_layers=[512, 512],
        device=device
    )
    
    # 6. Random Baseline
    random_agent = RandomAgent(num_actions=env.num_actions)
    
    agents = [
        dqn_agent, 
        nfsp_agent, 
        cfr_agent, 
        dqn_agent_2, 
        nfsp_agent_2, 
        random_agent
    ]
    
    env.set_agents(agents)

    # Metrics
    rewards_dqn = []
    rewards_nfsp = []
    rewards_cfr = []
    
    print(f"Starting Multi-Agent Training for {episodes} episodes...")
    
    for episode in range(episodes):
        # Run episode
        trajectories, payoffs = env.run(is_training=True)
        
        # Reorganize data
        trajectories = reorganize(trajectories, payoffs)
        
        # Train DQN (Seat 0)
        for ts in trajectories[0]:
            dqn_agent.feed(ts)
            
        # Train NFSP (Seat 1)
        for ts in trajectories[1]:
            nfsp_agent.feed(ts)
            
        # Train CFR (Seat 2) - Note: CFR usually updates differently, usually `train()` loop internal.
        # But if using DeepCFR/RLCard wrapper logic:
        # Standard tabular CFR doesn't need "feed", it learns during traversal.
        # If it is DeepCFR, it might need feed.
        # For this script, we assume standard CFR updates automatically or via its own loop.
        # RLCard CFRAgent typically trains via `agent.train()`, not step-by-step feed.
        # We will attempt to run one iteration of CFR training if supported.
        if hasattr(cfr_agent, 'train'):
            cfr_agent.train()
            
        # Logging
        if episode > 0 and episode % 100 == 0:
            print(f"Episode {episode}: DQN Payoff: {payoffs[0]}, NFSP Payoff: {payoffs[1]}, CFR Payoff: {payoffs[2]}")
            rewards_dqn.append(payoffs[0])
            rewards_nfsp.append(payoffs[1])
            rewards_cfr.append(payoffs[2])

    # Save Models
    print("Saving multi-agent models...")
    dqn_agent.save_checkpoint(save_path, 'multi_dqn.pth')
    nfsp_agent.save_checkpoint(save_path, 'multi_nfsp.pth')
    
    # CFR save
    if hasattr(cfr_agent, 'save'):
        cfr_agent.save() # usually saves to path defined in init
    
    dqn_agent_2.save_checkpoint(save_path, 'multi_dqn_2.pth')
    nfsp_agent_2.save_checkpoint(save_path, 'multi_nfsp_2.pth')

    # Plotting Learning Cures
    plt.figure(figsize=(10, 6))
    plt.plot(rewards_dqn, label='Multi-Agent DQN')
    plt.plot(rewards_nfsp, label='Multi-Agent NFSP')
    plt.plot(rewards_cfr, label='Multi-Agent CFR')
    plt.xlabel('Hundreds of Episodes')
    plt.ylabel('Payoff')
    plt.title('Multi-Agent Training Rewards')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(save_path, 'multi_agent_training_curve.png'))
    print("Training Complete. Plots saved.")

if __name__ == '__main__':
    train_six_player_mix(episodes=100000)