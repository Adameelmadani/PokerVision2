import os
import torch
import rlcard
from rlcard.agents import DQNAgent, NFSPAgent
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
    env = rlcard.make('no-limit-holdem', config={'seed': 42})
    print(f"Env num_actions: {env.num_actions}")
    print(f"Env state_shape: {env.state_shape}")

    # Initialize agent
    if agent_type == 'dqn':
        agent = DQNAgent(num_actions=env.num_actions, state_shape=env.state_shape[0], mlp_layers=[512, 512])
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
    else:
        raise ValueError("Invalid agent type. Choose 'dqn' or 'nfsp'.")

    # Set agents in environment
    # RLCard No-Limit Hold'em is 2-player by default
    agents = [agent]
    for _ in range(1, env.num_players):
        agents.append(DQNAgent(num_actions=env.num_actions, state_shape=env.state_shape[0], mlp_layers=[512, 512]))
    
    env.set_agents(agents)

    # Training loop
    print(f"Starting training for {agent_type} for {episodes} episodes...")
    for episode in range(episodes):
        # Generate data from the environment
        trajectories, payoffs = env.run(is_training=True)

        # Reorganize the trajectories to be used for training
        trajectories = reorganize(trajectories, payoffs)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{episodes} complete")

    # Save the agent
    agent.save_checkpoint(save_path, model_name)
    print(f"Model saved to {os.path.join(save_path, model_name)}")

if __name__ == '__main__':
    # Train both agents for a small number of episodes for demonstration
    # In a real scenario, you'd want many more episodes (e.g., 100,000+)
    train(agent_type='dqn', episodes=100)
    train(agent_type='nfsp', episodes=100)
