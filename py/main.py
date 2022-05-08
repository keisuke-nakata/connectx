from connectx.tutorial import connectx_game
from connectx.tutorial import minimax_agent


agent = minimax_agent.Agent(outdir=None)


def act(obs: connectx_game.Observation, config: connectx_game.Config) -> int:
    return agent(obs, config)
