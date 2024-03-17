#!/usr/bin/env python3
import contextlib
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import click


def run(*args: str) -> None:
    cmd = " ".join(args)
    click.echo("{} {}".format(click.style(">", fg="blue", bold=True), cmd))

    verbose = click.get_current_context().meta["verbose"]
    process = subprocess.run(args, capture_output=(not verbose))
    if process.returncode != 0:
        click.echo(
            "{} {} failed with returncode {}".format(click.style("!", fg="red", bold=True), cmd, process.returncode),
            err=True,
        )

        if process.stderr or process.stdout:
            click.echo(process.stdout.decode())
            click.echo(process.stderr.decode(), err=True)
        raise click.ClickException(f"Command failed with return code {process.returncode}")


def python(venv: Path, *args: str) -> None:
    pybinary = venv / "bin" / "python"
    run(str(pybinary), *args)


def dist(location: Path, pattern: str) -> Path:
    candidates = sorted(location.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise click.ClickException("No sdist found")
    return candidates[0]


def clean(package: str) -> None:
    run("rm", "-rf", f"src/{package}/assets/*")
    run("rm", "-rf", "dist")


@contextlib.contextmanager
def virtualenv(root: Path, name: str) -> Iterator[Path]:
    run("python", "-m", "venv", str(root / name))
    yield root / name
    run("rm", "-rf", str(root / name))


def check(venv: Path, package: str, assets: bool = False) -> None:
    python(venv, "-c", f"import {package}; print({package}.__version__)")

    if assets:
        python(venv, "-c", f"import {package}.assets; {package}.assets.check_dist()")

    python(venv, "-m", "pip", "install", "twine")
    python(venv, "-m", "twine", "check", f"dist/{package}-*")


def sdist(package: str, assets: bool = False) -> None:
    clean(package=package)
    run("python", "-m", "build", "-s", ".")
    with virtualenv(Path("dist"), "venv-sdist") as venv:
        python(venv, "-m", "pip", "install", "--upgrade", "pip")
        sdist = dist(Path("dist/"), "*.tar.gz")
        python(venv, "-m", "pip", "install", str(sdist))
        check(venv, package, assets=assets)
    click.secho("sdist built and installed successfully", fg="green", bold=True)


def wheel(package: str, assets: bool = False) -> None:
    clean(package=package)
    run("python", "-m", "build", "-w", ".")
    with virtualenv(Path("dist"), "venv-wheel") as venv:
        wheel = dist(Path("dist/"), "*.whl")
        python(venv, "-m", "pip", "install", str(wheel))
        check(venv, package, assets=assets)
    click.secho("wheel built and installed successfully", fg="green", bold=True)


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-a", "--assets", is_flag=True, help="Check assets")
@click.argument("package", type=str)
@click.pass_context
def main(ctx: click.Context, package: str, verbose: bool, assets: bool) -> None:
    """Check distribution for package"""
    if os.environ.get("CI") == "true":
        verbose = True

    ctx.meta["verbose"] = verbose
    sdist(package, assets=assets)
    wheel(package, assets=assets)


if __name__ == "__main__":
    main()
