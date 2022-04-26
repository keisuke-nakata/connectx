from collections.abc import Callable
from typing import Union

import numpy as np
from kaggle_environments import make, evaluate

from connectx.tutorial.one_step_lookahead import agent as one_step_agent
from connectx.tutorial.minimax_agent import agent as minimax_agent

Agent = Union[Callable, str]


def get_win_percentages(agent1: Agent, agent2: Agent, n_rounds: int = 100) -> None:
    # Use default Connect Four setup
    config = {'rows': 6, 'columns': 7, 'inarow': 4}
    # Agent 1 goes first (roughly) half the time
    outcomes = evaluate("connectx", [agent1, agent2], config, [], n_rounds // 2)
    # Agent 2 goes first (roughly) half the time
    outcomes += [[b,a] for [a,b] in evaluate("connectx", [agent2, agent1], config, [], n_rounds - n_rounds // 2)]
    print("Agent 1 Win Percentage:", np.round(outcomes.count([1,-1]) / len(outcomes), 2))
    print("Agent 2 Win Percentage:", np.round(outcomes.count([-1,1]) / len(outcomes), 2))
    print("Number of Invalid Plays by Agent 1:", outcomes.count([None, 0]))
    print("Number of Invalid Plays by Agent 2:", outcomes.count([0, None]))


if __name__ == "__main__":
    from pathlib import Path
    outdir = Path("./out").resolve()
    outdir.mkdir(exist_ok=True)

    # env = make("connectx", debug=True)
    # env.run([one_step_agent, "random"])
    # html = env.render(mode="html")
    # with open(outdir / "a.html", "w") as f:
    #     print(html, file=f)
    # get_win_percentages(one_step_agent, "random")

    # env = make("connectx", debug=True)
    # env.run([minimax_agent, "random"])
    # html = env.render(mode="html")
    # with open(outdir / "a.html", "w") as f:
    #     print(html, file=f)
    # get_win_percentages(minimax_agent, "random")

    env = make("connectx", debug=True)
    env.run([minimax_agent, one_step_agent])
    html = env.render(mode="html")
    with open(outdir / outdir / "a.html", "w") as f:
        print(html, file=f)
    # get_win_percentages(minimax_agent, "random")

    # env = make("connectx", debug=True)
    # env.run([minimax_agent, minimax_agent])
    # html = env.render(mode="html")
    # with open("a.html", "w") as f:
    #     print(html, file=f)
    # get_win_percentages(minimax_agent, "random")
