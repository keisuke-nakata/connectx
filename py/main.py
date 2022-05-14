from connectx.tutorial import connectx_game
from connectx.tutorial import primitive_mcts_agent


agent = primitive_mcts_agent.Agent(depth=1, outdir=None)


def act(obs: connectx_game.Observation, config: connectx_game.Config) -> int:
    return agent(obs, config)
