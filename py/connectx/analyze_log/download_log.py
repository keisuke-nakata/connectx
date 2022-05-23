from __future__ import annotations

from pathlib import Path
import time

import click
from selenium import webdriver
from selenium.webdriver.common import by
from selenium.webdriver.support import ui
import requests


@click.command()
@click.argument("submission_id", type=click.STRING)
@click.argument("outdir", type=click.Path(exists=True, file_okay=False, writable=True, path_type=Path))
def download_log(submission_id: str, outdir: Path) -> None:
    episode_ids = _get_episode_list(submission_id)
    (outdir / submission_id).mkdir(exist_ok=True)
    for episode_id in episode_ids:
        if (outdir / submission_id / (episode_id + ".json")).exists():
            print(f"{episode_id}.json already exists. skip")
            continue
        _download_a_episode(episode_id, outdir / submission_id)
        time.sleep(1)


def _get_episode_list(submission_id: str) -> list[str]:
    url = "https://www.kaggle.com/competitions/connectx/submissions?dialog=episodes-submission-" + submission_id
    driver.get(url)
    elem_container = ui.WebDriverWait(driver, timeout=10).until(  # type: ignore
        lambda d: d.find_element(by=by.By.CLASS_NAME, value="mdc-dialog__container")
    )
    for _ in range(30):
        webdriver.ActionChains(driver).scroll(0, 0, 0, 1000, origin=elem_container).perform()  # type: ignore
        a_list = elem_container.find_elements(by=webdriver.common.by.By.TAG_NAME, value="a")  # type: ignore
        if "keisuke (Validation) vs" in a_list[-1].text:
            break
        time.sleep(1)
    else:
        raise RuntimeError("scroll limit!")
    hrefs = [a.get_attribute("href") for a in a_list]
    return [href[-8:] for href in hrefs]


def _download_a_episode(episode_id: str, submission_outdir: Path) -> None:
    base_url = "https://www.kaggleusercontent.com/episodes/"  # 37216202.json
    url = base_url + episode_id + ".json"
    res = requests.get(url)
    if not res.ok:
        raise RuntimeError(f"failed to get episode {episode_id}!")
    with open(submission_outdir / (episode_id + ".json"), "w") as f:
        print(res.content.decode("utf-8"), file=f)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    try:
        download_log()
    finally:
        driver.quit()
