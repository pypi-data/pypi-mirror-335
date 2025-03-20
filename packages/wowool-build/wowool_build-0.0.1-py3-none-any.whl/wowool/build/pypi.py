from os import environ
from pathlib import Path
from subprocess import run


from wowool.build.exceptions import UploadError


def _check_not_dirty(fn: Path):
    if "dirty" in fn.name:
        raise UploadError(f"Attempted to upload a dirty version: {fn}")


def upload_pypi(fp: Path, expression: str = "*", repository: str | None = None):
    """
    Upload a Python package to pypi
    """
    fp_dist = fp / "dist"
    for fn in fp_dist.glob(expression):
        _check_not_dirty(fn)
        repository = environ.get("TWINE_REPOSITORY", None)
        repository_option = f"--repository-url {repository}" if repository else ""
        cmd = f"python -m twine upload {repository_option} dist/*"
        try:
            print(f"cmd: {cmd} {fn=} {fp_dist=}")
            run(cmd, shell=True, check=True, cwd=str(fp))
        except Exception as error:
            raise UploadError(f"PyPi Twine upload failed: {error}")
