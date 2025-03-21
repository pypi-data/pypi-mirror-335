from os import environ
from sys import stderr
from dataclasses import dataclass
from typing import Optional, Union
from pathlib import Path
from subprocess import run
import hashlib
import json
import re
from wowool.build.exceptions import UploadError


@dataclass
class AwsCredentials:
    """
    Credentials to access AWS
    """

    domain: str
    domain_owner: int
    region: str

    @staticmethod
    def from_environment():
        return AwsCredentials(
            domain=environ["AWS_DOMAIN"],
            domain_owner=int(environ["AWS_DOMAIN_OWNER"]),
            region=environ["AWS_REGION"],
        )


@dataclass
class CodeArtifactCredentials:
    """
    Credentials to access a CodeArtifact repository
    """

    repository: str

    @staticmethod
    def from_environment():
        return CodeArtifactCredentials(repository=environ["AWS_CODEARTIFACT_REPOSITORY"])


def _check_not_dirty(fn: Path):
    if "dirty" in fn.name:
        raise UploadError(f"Attempted to upload a dirty version: {fn}")


def upload_pypi(fp: Path, expression: str = "*"):
    """
    Upload a Python package to AWS CodeArtifact
    """
    fp_dist = fp / "dist"
    for fn in fp_dist.glob(expression):
        _check_not_dirty(fn)
        cmd = f"twine upload {fn} --repository codeartifact"
        try:
            run(cmd, shell=True, check=True, cwd=fp)
        except Exception as error:
            raise UploadError(f"AWS CodeArtifact Twine upload failed: {error}")


def _sha256sum(fn: Path):
    with open(fn, "rb", buffering=0) as ifs:
        return hashlib.file_digest(ifs, "sha256").hexdigest()  # pyright: ignore


def delete_raw(
    package: str,
    version: str,
    namespace: str | None = None,
    format: str = "generic",
    aws: Optional[AwsCredentials] = None,
    codeartifact: Optional[CodeArtifactCredentials] = None,
):
    aws = aws or AwsCredentials.from_environment()
    codeartifact = codeartifact or CodeArtifactCredentials.from_environment()
    options = f"--namespace {namespace}" if namespace != None else ""
    options += f" --format {format}"
    cmd = f"""aws codeartifact delete-package-versions --domain {aws.domain} --domain-owner {aws.domain_owner} --region {aws.region} --repository {codeartifact.repository}  {options} --package {package} --versions {version} """
    result = run(cmd, shell=True, check=False, capture_output=True)
    print(result.stdout.decode())
    if result.returncode != 0:
        print(result.stderr.decode(), file=stderr)
        raise UploadError(f"AWS CodeArtifact generic upload failed {cmd=}")


def upload_raw(
    fn: Path,
    namespace: str,
    package: str,
    version: str,
    aws: Optional[AwsCredentials] = None,
    codeartifact: Optional[CodeArtifactCredentials] = None,
    overwrite=False,
):
    fn = Path(fn)
    aws = aws or AwsCredentials.from_environment()
    codeartifact = codeartifact or CodeArtifactCredentials.from_environment()

    if overwrite:
        try:
            delete_raw(namespace=namespace, package=package, version=version)
        except Exception as error:
            print(f"AWS CodeArtifact generic delete failed: {error}", file=stderr)

    try:
        asset_hash = _sha256sum(fn)
    except Exception as error:
        raise UploadError(f"Could not produce sha256 hash for {fn}: {error}")
    try:
        cmd = f"""aws codeartifact publish-package-version --domain {aws.domain} --domain-owner {aws.domain_owner} --region {aws.region} --repository {codeartifact.repository} --format generic --namespace {namespace} --package {package} --package-version {version} --asset-content {fn} --asset-name {fn.name} --asset-sha256 '{asset_hash}' --unfinished"""
        result = run(cmd, shell=True, check=False, capture_output=True)
        print(result.stdout.decode())
        if result.returncode != 0:
            print(result.stderr.decode(), file=stderr)
            raise UploadError(f"AWS CodeArtifact generic upload failed {cmd=}")
    except Exception as error:
        raise UploadError(f"AWS CodeArtifact generic upload failed: {error}")


def run_codeartifact(
    cmd: str,
    aws: Optional[AwsCredentials] = None,
    codeartifact: Optional[CodeArtifactCredentials] = None,
):
    aws = aws or AwsCredentials.from_environment()
    codeartifact = codeartifact or CodeArtifactCredentials.from_environment()
    try:
        codeartifact_cmd = f"aws codeartifact {cmd}"
        print(f"Running: {codeartifact_cmd}")
        result = run(codeartifact_cmd, shell=True, check=False, capture_output=True)

        if result.returncode != 0:
            print(result.stderr.decode(), file=stderr)
            raise UploadError(f"AWS CodeArtifact generic cmd failed {cmd=}")
        else:
            return result.stdout.decode()
    except Exception as error:
        raise UploadError(f"AWS CodeArtifact generic cmd failed: {error}")


def download_raw(
    output: Union[str, Path],
    namespace: str,
    package: str,
    version: str,
    aws: Optional[AwsCredentials] = None,
    codeartifact: Optional[CodeArtifactCredentials] = None,
):
    output = Path(output)
    aws = aws or AwsCredentials.from_environment()
    codeartifact = codeartifact or CodeArtifactCredentials.from_environment()
    try:
        cmd = f"""aws codeartifact get-package-version-asset --package-version {version} --domain {aws.domain} --domain-owner {aws.domain_owner} --region {aws.region} --repository {codeartifact.repository} --format generic --namespace {namespace} --package {package} --asset {output.name} {output}"""
        result = run(cmd, shell=True, check=False, capture_output=True)
        print(result.stdout.decode())
        if result.returncode != 0:
            print(result.stderr.decode(), file=stderr)
            raise UploadError(f"AWS CodeArtifact generic upload failed {cmd=}")
    except Exception as error:
        raise UploadError(f"AWS CodeArtifact generic upload failed: {error}")


def iter_packages(expression=".*", aws: Optional[AwsCredentials] = None, codeartifact: Optional[CodeArtifactCredentials] = None):

    exp_ = re.compile(expression)
    cmd = "list-packages --domain wowool --repository wowool --max-items 1000 "
    data = run_codeartifact(cmd, aws, codeartifact)
    jo = json.loads(data)
    for package in jo["packages"]:
        if exp_.search(package["package"]):
            yield package["package"]


def list_package_info(
    expression: str = ".*",
    version_expression: str = ".*",
    aws: Optional[AwsCredentials] = None,
    codeartifact: Optional[CodeArtifactCredentials] = None,
):

    version_exp_ = re.compile(version_expression)
    for name in iter_packages(expression, aws, codeartifact):
        try:
            cmd = f"list-package-versions --domain wowool --repository wowool --format pypi --package {name}"
            jo_version = json.loads(run_codeartifact(cmd))
            # print(jo_version)
            # yield jo_version['defaultDisplayVersion']
            for version in jo_version["versions"]:
                if version_exp_.match(version["version"]):
                    yield jo_version["namespace"], jo_version["package"], version["version"], jo_version["format"]
        except UploadError as error:
            print(f"Error: {error}", file=stderr)
