from connectx.tutorial import connectx_game
from connectx.tutorial import mcts_agent


agent = mcts_agent.Agent(depth=1, outdir=None)


def act(obs: connectx_game.Observation, config: connectx_game.Config) -> int:
    return agent(obs, config)
