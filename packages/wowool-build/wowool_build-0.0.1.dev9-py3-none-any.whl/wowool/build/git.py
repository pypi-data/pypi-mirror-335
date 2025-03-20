from logging import getLogger
from os import getcwd
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional, Union
from os import environ

logger = getLogger(__name__)


def _get_repository_path(fp_repo: Optional[Union[str, Path]] = None) -> Path:
    if fp_repo is None:
        return Path(getcwd())
    else:
        return Path(fp_repo).parent if Path(fp_repo).is_file() else Path(fp_repo)


def increment_version(version: str) -> str:
    try:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except ValueError:
        return version


def make_version(tag: str, nr_commits: int, has_changes: bool):
    postfix = environ.get("WOWOOL_VERSION_POSTFIX", f".dev{nr_commits}+dirty")
    if "dev0" in tag:
        tag = tag.replace(".dev0", "")
        version = f"{tag}.dev{nr_commits}" if has_changes == 0 else f"{tag}{postfix}"
        return version
    else:
        if has_changes == 0:
            if nr_commits == 0:
                return tag
            else:
                tag = increment_version(tag)
                if "WOWOOL_VERSION_POSTFIX" not in environ:
                    version = f"{tag}.dev{nr_commits}"
                else:
                    version = f"{tag}{postfix}"
                return version
        else:
            tag = increment_version(tag)
            version = f"{tag}{postfix}"
            return version


def run_safe(cmd: str, capture_output: bool = True, cwd: Optional[Union[str, Path]] = None) -> str:
    try:
        res = run(cmd, shell=True, check=True, cwd=cwd, capture_output=capture_output)
        return res.stdout.decode("utf-8").strip()
    except CalledProcessError as ex:
        logger.error(f"Error running command: {cmd}")
        logger.error(ex)
        print(ex.stderr.decode("utf-8"))
        print(ex.stderr.decode("utf-8"))
        raise ex


def get_version_info(fp_repo: Optional[Union[str, Path]] = None) -> dict:
    tag = run_safe("git describe --tags --abbrev=0", cwd=fp_repo)
    nr_commits_result = run_safe(f"git log {tag}..HEAD --oneline", cwd=fp_repo)
    nr_commits = len(nr_commits_result.splitlines())
    has_changes = run("git diff --quiet --exit-code HEAD", shell=True).returncode != 0
    return {"tag": tag, "nr_commits": nr_commits, "has_changes": has_changes}


def get_version(fp_repo: Optional[Union[str, Path]] = None) -> str:
    """
    Get the version from the git history of the given repository folder

    :param fp_repo: Optional repository folder. If not provided, the current
                    working directory is used
    """

    fp_repo = _get_repository_path(fp_repo)

    _git_info = get_version_info(fp_repo)
    return make_version(_git_info["tag"], _git_info["nr_commits"], _git_info["has_changes"])


def git_hash(fp_repo: Optional[Union[str, Path]] = None) -> str:
    fp_repo = _get_repository_path(fp_repo)
    result = run("git rev-parse HEAD", capture_output=True, shell=True, check=True, cwd=fp_repo)
    git_hash_rev = result.stdout.decode().strip()
    return git_hash_rev
