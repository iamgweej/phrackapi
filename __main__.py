# builtins imports
import urllib.parse
import pathlib
import re
import os

from pprint import pprint

# 3rd party imports
import requests
import click

from bs4 import BeautifulSoup

# Constants
ISSUES_URL = "http://www.phrack.org/archives/issues/"
ISSUE_PATTERN = re.compile(r"[0-9]+/")
STORY_PATTERN = re.compile(r"[0-9]+\.txt")
CHUNK_SIZE = 4096

def download_story(story_url: str, dest_file: pathlib.Path):
    click.echo(f"[+] Downloading issue from {story_url} to {dest_file}")

    story_req = requests.get(story_url)
    assert story_req.status_code == 200

    with open(dest_file, "wb") as f:
        for chunk in story_req.iter_content(CHUNK_SIZE):
            f.write(chunk)

def download_issue(issue_url: str, dest_dir: pathlib.Path):
    click.echo(f"[+] Downloading issue from {issue_url} to {dest_dir}")

    issue_req = requests.get(issue_url)
    assert issue_req.status_code == 200

    issue_bs = BeautifulSoup(issue_req.text, features="html.parser")
    issue_all_a = issue_bs.find_all("a")
    issue_all_hrefs = (tag["href"] for tag in issue_all_a)
    issue_stories = (href for href in issue_all_hrefs if re.match(STORY_PATTERN, href) is not None)

    for story_url in issue_stories:
        story_abs_url = urllib.parse.urljoin(issue_url, story_url)
        story_abs_path = dest_dir.joinpath(story_url).absolute()

        download_story(story_abs_url, story_abs_path)

@click.command()
@click.argument('dest', type=click.Path(exists=True, dir_okay=True, file_okay=False))
def download_all(dest: str):
    dest_path = pathlib.Path(dest)

    phrack_issues_req = requests.get(ISSUES_URL)
    assert phrack_issues_req.status_code == 200

    issues_bs = BeautifulSoup(phrack_issues_req.text, features="html.parser")
    issues_all_a = issues_bs.find_all('a')
    issues_all_hrefs = (tag["href"] for tag in issues_all_a)
    issues_hrefs = (href for href in issues_all_hrefs if re.match(ISSUE_PATTERN, href))

    for issue_url in issues_hrefs:
        issue_abs_url = urllib.parse.urljoin(ISSUES_URL, issue_url)
        issue_abs_path = dest_path.joinpath(issue_url).absolute()
        
        issue_abs_path.mkdir(exist_ok=True)
        download_issue(issue_abs_url, issue_abs_path)

def main():
    download_all()


if __name__ == "__main__":
    main()
