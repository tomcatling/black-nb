"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "black_nb", "tests"]


@nox.session()
def mypy(session):
    """Type check code with mypy."""
    session.install("mypy")
    session.run("mypy", "--strict", "black_nb")


@nox.session()
def flake8(session):
    """Lint code with Flake8."""
    session.install("flake8")
    session.run("flake8", *SOURCES)


@nox.session()
def black(session):
    """Check code formatting with black."""
    session.install("black==19.10b0")
    if session.posargs:
        session.run("black", *session.posargs)
    else:
        session.run("black", "--check", *SOURCES)


@nox.session()
def test(session):
    """Test"""
    session.install("pytest")
    session.install("-e", ".")
    session.run("pytest", "black_nb", "tests/")
