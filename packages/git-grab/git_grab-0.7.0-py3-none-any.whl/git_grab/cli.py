import argparse
import logging
import os
import subprocess  # nosec
import tempfile
from pathlib import Path
from typing import List
from urllib.parse import ParseResult, urlparse

from git_grab import __version__

logger = logging.getLogger("grab")


class Repository:
    site: str
    owner: str
    project: str
    clone: str

    def __init__(self, repo: str) -> None:
        logger.debug(f"Repository: {repo}")
        parsed = urlparse(repo)
        if len(parsed.scheme) == 0:
            self.git_parser(repo)
        else:
            self.url_parser(parsed)
        self.clone = repo

    def url_parser(self, parse: ParseResult) -> None:
        logger.debug(f"Url parser: {parse}")
        # https://github.com/Boomatang/git-grab.git
        self.site = parse.hostname if parse.hostname is not None else ""
        string = parse.path.split("/")
        self.owner = string[1]
        string = string[2].split(".")
        self.project = string[0]

    def git_parser(self, parse: str) -> None:
        logger.debug(f"Git parser: {parse}")
        # git@github.com:Boomatang/git-grab.git
        elements: list[str] = parse.split("@")
        elements = elements[1].split(":")
        self.site = elements[0]
        elements = elements[1].split("/")
        self.owner = elements[0]
        if elements[1].endswith(".git"):
            self.project = elements[1][:-4]
        else:
            logger.error('expected input to end with ".git"')
            exit(1)

    def __repr__(self) -> str:
        return f"{self.site}/{self.owner}/{self.project}"


def configure_logger(logger: logging.Logger, debug: bool = False) -> None:
    ch = logging.StreamHandler()
    if debug:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def create_project_path(path: Path, repo: Repository) -> Path:
    p: Path = Path(path, repo.site, repo.owner, repo.project)
    logger.debug(f"Creating project path: {p}, if not already exists")
    if p.is_dir():
        logger.warning(f'Directory "{p}" already exists.')
        logger.warning(f'Not attempting to clone "{repo}".')
        exit(1)
    p.mkdir(parents=True)
    return p


def clone(path: Path, repo: Repository) -> None:
    logger.info(f"Starting to clone {repo}")
    value = subprocess.run(
        ["git", "-C", str(path), "clone", "--bare", repo.clone, ".bare"],
        capture_output=True,
    )  # nosec
    if value.returncode != 0:
        logger.error(f"Failed to clone {repo}")
        logger.debug(f"error: {value.stderr.decode()}")
    else:
        logger.info(f"Successfully cloned {repo}")


def link_git(path: Path) -> None:
    logger.debug("Creating .git file")
    git_file = Path(path, ".git")
    with open(git_file, "w") as f:
        f.write("gitdir: .bare")


def make_main_worktree(path: Path) -> None:
    logger.debug("Creating initial main work tree")

    value = subprocess.run(
        ["git", "-C", str(path), "worktree", "add", "main"],
        capture_output=True,
    )  # nosec
    if value.returncode != 0:
        logger.error("Failed to create main work tree")
        logger.debug(f"error: {value.stderr.decode()}")
    else:
        logger.info("Successfully created main work tree")


def configure_origin_fetch(path: Path) -> None:
    logger.debug("Configure fetch for origin")
    value = subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "config",
            "remote.origin.fetch",
            "+refs/heads/*:refs/remotes/origin/*",
        ],
        capture_output=True,
    )  # nosec
    if value.returncode != 0:
        logger.error("Failed to configure origin fetch")
        logger.debug(f"error: {value.stderr.decode()}")
    else:
        logger.info("Successfully configured origin fetch")


def get_paths(path: Path, repo: Repository) -> List[Path]:
    out = []

    for p in path.iterdir():
        if p.is_dir() and p.name == repo.site:
            for sp in p.iterdir():
                if sp.is_dir():
                    for ssp in sp.iterdir():
                        if ssp.is_dir() and ssp.name == repo.project:
                            logger.debug(f"Found {ssp}")
                            out.append(ssp)
    return out


def add_remote(origin: Path, repo: Repository) -> None:
    logger.debug(f"Checking if remote {repo.owner} exists")
    value = subprocess.run(
        ["git", "-C", str(origin), "remote"], capture_output=True
    )  # nosec
    if value.returncode != 0:
        logger.error(f"Failed to check if remote {repo.owner} exists")
        logger.debug(f"error: {value.stderr.decode()}")
        return
    result = value.stdout.decode().split("\n")
    if repo.owner in result:
        logger.warning(f"Remote {repo.owner} already exists, skipping")
        return

    logger.debug(f"Adding remote {repo.owner}")
    value = subprocess.run(
        ["git", "-C", str(origin), "remote", "add", repo.owner, repo.clone],
        capture_output=True,
    )  # nosec
    if value.returncode != 0:
        logger.error(f"Failed to add remote {repo}")
        logger.debug(f"error: {value.stderr.decode()}")
        return
    logger.info(f"Successfully added remote {repo.owner} to {origin}")


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="grab",
        description="grab clones the give repositories into a structure "
        "directory. The path to the root of this structure is "
        "set in the GRAB_PATH environment variable.",
    )
    parser.add_argument(
        "REPOS",
        nargs="*",
        help="Git repositories to clone.",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Overrides the path set in the GRAB_PATH environment variable.",
    )
    parser.add_argument(
        "-t",
        "--temp",
        help="Download repositories to a temporary directory. This will be the OS "
        "default temporary directory.",
        action="store_true",
    )
    parser.add_argument(
        "-r", "--remote", help="Add remote to existing repo.", action="store_true"
    )
    parser.add_argument("--debug", help="Enable debug mode.", action="store_true")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s, version {__version__}",
    )
    args = parser.parse_args()
    configure_logger(logger, debug=args.debug)

    logger.debug(f"{args=}")

    if args.temp and args.path is not None:
        logger.error("Cannot specify both --temp and --path.")
        exit(1)

    if args.temp:
        path = tempfile.gettempdir()
        logger.debug(f"Using temp directory {path}")
    elif args.path:
        path = args.path
        logger.debug(f"Using path {path}")
    else:
        path = os.getenv("GRAB_PATH", "")
        logger.debug(f"Using default path {path}")

        if path is None:
            logger.error("No path provided.")
            logger.info("Set GRAB_PATH environment variable or use --path.")
            exit(1)

    path_dir = Path(path)
    if not path_dir.is_dir():
        logger.error(f'Path "{path_dir}" not a directory.')
        logger.info(f"Please create the directory: {path_dir}")
        exit(1)

    for repo in args.REPOS:
        r = Repository(repo)
        if args.remote:
            logger.info(f"Processing remote {r}")
            origins = get_paths(path_dir, r)
            if len(origins) == 0:
                logger.warning(f"No origins found for {r}")
            for origin in origins:
                add_remote(origin, r)
        else:
            logger.info(f"Processing repository {r}")
            project_path = create_project_path(path_dir, r)

            clone(project_path, r)
            link_git(project_path)
            make_main_worktree(project_path)
            configure_origin_fetch(project_path)


if __name__ == "__main__":
    cli()
