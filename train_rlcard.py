import os
import torch
import rlcard
from rlcard.agents import DQNAgent, NFSPAgent, CFRAgent
from rlcard.utils import (
    get_device,
    set_seed,
    tournament,
    reorganize,
    Logger,
    plot_curve,
)

def train(agent_type='dqn', episodes=1000, save_path='models'):
    # Check for models directory
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    # Set device
    device = get_device()
    # Seed for reproducibility
    set_seed(42)

    # Make environment
    env = rlcard.make('no-limit-holdem', config={'seed': 42, 'allow_step_back': True})
    print(f"Env num_actions: {env.num_actions}")
    print(f"Env state_shape: {env.state_shape}")

    # Initialize agent
    model_name = ""
    if agent_type == 'dqn':
        agent = DQNAgent(num_actions=env.num_actions, state_shape=env.state_shape[0], mlp_layers=[512, 512], device=device)
        model_name = 'dqn_agent.pth'
    elif agent_type == 'nfsp':
        agent = NFSPAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            hidden_layers_sizes=[512, 512],
            q_mlp_layers=[512, 512],
            device=device
        )
        model_name = 'nfsp_agent.pth'
    elif agent_type == 'cfr':
        # CFR learns by traversing checks
        agent = CFRAgent(env, os.path.join(save_path, 'cfr_policy'))
        model_name = 'cfr_agent_policy' # CFR saves directory structure often
    else:
        raise ValueError("Invalid agent type. Choose 'dqn', 'nfsp', or 'cfr'.")

    # Set agents in environment
    # RLCard No-Limit Hold'em is 2-player by default
    agents = [agent]
    for _ in range(1, env.num_players):
        # Opponents are standard DQN
        agents.append(DQNAgent(num_actions=env.num_actions, state_shape=env.state_shape[0], mlp_layers=[512, 512], device=device))
    
    env.set_agents(agents)

    # Logging
    rewards = []

    # Training loop
    print(f"Starting training for {agent_type} for {episodes} episodes...")
    for episode in range(episodes):
        if agent_type == 'cfr':
            agent.train()
            # Estimate payoff occasionally
            if episode % 100 == 0:
                print(f"CFR Iteration {episode}")
        else:
            # Generate data from the environment
            trajectories, payoffs = env.run(is_training=True)
            # Reorganize the trajectories to be used for training
            trajectories = reorganize(trajectories, payoffs)
            # Feed transitions into agent memory, and train the agent
            for ts in trajectories[0]:
                agent.feed(ts)
                
            if (episode + 1) % 100 == 0:
                print(f"Episode {episode + 1}/{episodes}, Payoff: {payoffs[0]}")
                rewards.append(payoffs[0])

    # Save the agent
    if agent_type == 'cfr':
        agent.save()
        print(f"CFR Model saved to {os.path.join(save_path, model_name)}")
    else:
        agent.save_checkpoint(save_path, model_name)
        print(f"Model saved to {os.path.join(save_path, model_name)}")
        
        # Simple plot for single agent
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(rewards)
        plt.title(f'{agent_type.upper()} Training')
        plt.savefig(os.path.join(save_path, f'{agent_type}_training.png'))

if __name__ == '__main__':
    # Train normal agents
    train(agent_type='dqn', episodes=100000)
    train(agent_type='nfsp', episodes=100000)
    train(agent_type='cfr', episodes=100000)
