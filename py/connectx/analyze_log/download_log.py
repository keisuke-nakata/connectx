from __future__ import annotations

from pathlib import Path
import time
import re
import os
import traceback

import click
from selenium import webdriver
from selenium.webdriver.common import by
from selenium.webdriver.support import ui
import requests

EPISODE_URL_PATTERN = re.compile(
    r"https://www.kaggle.com/competitions/connectx/submissions\?dialog=episodes-episode-(?P<episode_id>\d{8})"
)


@click.command()
@click.argument("submission_id", type=click.STRING)
@click.argument("outdir", type=click.Path(exists=True, file_okay=False, writable=True, path_type=Path))
def download_log(submission_id: str, outdir: Path) -> None:
    episode_ids = _get_episode_list(submission_id)
    submission_outdir = outdir / submission_id / "jsons"
    submission_outdir.mkdir(exist_ok=True)
    for episode_id in episode_ids:
        if (submission_outdir / (episode_id + ".json")).exists():
            print(f"{episode_id}.json already exists. skip")
            continue
        print(f"downloading episode {episode_id}...")
        _download_a_episode(episode_id, submission_outdir)
        time.sleep(1)


def _login(username: str, password: str) -> None:
    url = "https://www.kaggle.com/account/login?phase=emailSignIn"
    driver.get(url)
    driver.find_element(by=by.By.NAME, value="email").find_element(by=by.By.XPATH, value="..").send_keys(username)
    driver.find_element(by=by.By.NAME, value="password").find_element(by=by.By.XPATH, value="..").send_keys(password)
    driver.find_element(by=by.By.XPATH, value="//button[@type='submit']").click()
    ui.WebDriverWait(driver, timeout=3).until(lambda d: d.current_url == "https://www.kaggle.com/")
    time.sleep(3)


def _get_episode_list(submission_id: str) -> list[str]:
    url = "https://www.kaggle.com/competitions/connectx/submissions"
    driver.get(url)
    time.sleep(1)
    episode_ids = []
    start = 0
    for i in range(start, start + 10):  # 10回連続で機械的に episode を取ろうとすると session を切られるっぽい？
        try:
            driver.find_element(
                by=by.By.XPATH, value=f"//a[@href='?dialog=episodes-submission-{submission_id}']"
            ).click()
            surface = ui.WebDriverWait(driver, timeout=3).until(
                lambda d: d.find_element(by=by.By.CLASS_NAME, value="mdc-dialog__surface")
            )
            ul = ui.WebDriverWait(surface, timeout=3).until(
                lambda surface: surface.find_element(by=by.By.TAG_NAME, value="ul")
            )
            li = ul.find_elements(by=by.By.TAG_NAME, value="li")[i]
            li.click()
            current_url = driver.current_url
            match = EPISODE_URL_PATTERN.match(current_url)
            if match is None:
                raise RuntimeError(f"{current_url} does not match the pattern!")
            episode_ids.append(match.group("episode_id"))
            close = ui.WebDriverWait(driver, timeout=3).until(
                lambda d: d.find_element(by=by.By.XPATH, value="//span[contains(text(), 'Close')]")
            )
            close.find_element(by=by.By.XPATH, value="..").click()
            time.sleep(0.5)
        except Exception:
            traceback.print_exc()
            print(f"_get_episode_list was failed at {i}-th episode.")
            break
    return episode_ids


def _download_a_episode(episode_id: str, submission_outdir: Path) -> None:
    base_url = "https://www.kaggleusercontent.com/episodes/"
    url = base_url + episode_id + ".json"
    res = requests.get(url)
    if not res.ok:
        raise RuntimeError(f"failed to get episode {episode_id}!")
    with open(submission_outdir / (episode_id + ".json"), "w") as f:
        print(res.content.decode("utf-8"), file=f)


if __name__ == "__main__":
    username = os.environ["KAGGLE_USERNAME"]
    password = os.environ["KAGGLE_PASSWORD"]

    driver = webdriver.Chrome()
    try:
        _login(username, password)
        download_log()
    finally:
        driver.quit()
