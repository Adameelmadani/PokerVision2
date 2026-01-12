import os
import torch
import rlcard
import numpy as np
import matplotlib.pyplot as plt
from rlcard.agents import DQNAgent, NFSPAgent, RandomAgent, CFRAgent
from rlcard.utils import tournament

def load_agent(agent_type, model_path, env, device):
    if 'dqn' in agent_type:
        agent = DQNAgent(num_actions=env.num_actions, state_shape=env.state_shape[0], mlp_layers=[512, 512], device=device)
        try:
            checkpoint = torch.load(model_path, map_location=device)
            agent.from_checkpoint(checkpoint)
        except:
            print(f"Could not load {model_path}, using random init.")
    elif 'nfsp' in agent_type:
        agent = NFSPAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            hidden_layers_sizes=[512, 512],
            q_mlp_layers=[512, 512],
            device=device
        )
        try:
            checkpoint = torch.load(model_path, map_location=device)
            # NFSP checkpoint loading manual fix may be needed depending on saving method
            if isinstance(checkpoint, dict) and 'policy_network' in checkpoint:
                 agent.policy_network.load_state_dict(checkpoint['policy_network'])
        except:
             print(f"Could not load {model_path}, using random init.")
    elif 'cfr' in agent_type:
        agent = CFRAgent(env, model_path)
        agent.load()
    else:
        agent = RandomAgent(num_actions=env.num_actions)
    return agent

def compare_models(models_dir='models', num_games=1000):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    env = rlcard.make('no-limit-holdem', config={'seed': 42})
    
    # Define the 6 agents
    agents_config = [
        ('Normal DQN', 'dqn', os.path.join(models_dir, 'dqn_agent.pth')),
        ('Normal NFSP', 'nfsp', os.path.join(models_dir, 'nfsp_agent.pth')),
        ('Normal CFR', 'cfr', os.path.join(models_dir, 'cfr_agent_policy')),
        ('Multi DQN', 'dqn', os.path.join(models_dir, 'multi_dqn.pth')),
        ('Multi NFSP', 'nfsp', os.path.join(models_dir, 'multi_nfsp.pth')),
        ('Random', 'random', None)
    ]
    
    loaded_agents = []
    names = []
    
    print("Loading agents for tournament...")
    for name, type_, path in agents_config:
        print(f"Loading {name}...")
        agent = load_agent(type_, path, env, device)
        loaded_agents.append(agent)
        names.append(name)
        
    # Run Tournament
    # Since tournament() usually takes a list of agents for one game instance,
    # we want to evaluate head-to-head or all together.
    # Let's do a round-robin head-to-head matrix.
    
    results_matrix = np.zeros((6, 6))
    
    print(f"Running Round-Robin Tournament ({num_games} games per match)...")
    
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            
            # Setup 2-player duel for comparison metric
            env_duel = rlcard.make('no-limit-holdem', config={'game_num_players': 2})
            env_duel.set_agents([loaded_agents[i], loaded_agents[j]])
            
            payoffs = tournament(env_duel, num_games)
            # payoffs is a list of normalized rewards usually
            avg_payoff = payoffs[0] # Player 1's average payoff
            
            results_matrix[i][j] = avg_payoff
            print(f"{names[i]} vs {names[j]}: {avg_payoff:.3f}")

    # Plot Matrix
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(results_matrix, cmap='RdYlGn')
    
    # Show all ticks
    ax.set_xticks(np.arange(len(names)))
    ax.set_yticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_yticklabels(names)
    
    # Loop over data dimensions and create text annotations.
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j:
                text = ax.text(j, i, f"{results_matrix[i, j]:.2f}",
                               ha="center", va="center", color="black")

    ax.set_title("Head-to-Head Payoff Matrix (Row Agent Payoff)")
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(os.path.join(models_dir, 'agents_comparison_matrix.png'))
    print("Comparison saved to agents_comparison_matrix.png")

    # Bar chart summary (Average win rate against all others)
    avg_performance = np.sum(results_matrix, axis=1) / 5 # divide by opponents
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, avg_performance, color=['blue', 'orange', 'green', 'purple', 'red', 'gray'])
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title('Average Payoff vs All Other Agents')
    plt.ylabel('Average Payoff')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(models_dir, 'agents_ranking.png'))
    print("Ranking saved to agents_ranking.png")

if __name__ == "__main__":
    compare_models()