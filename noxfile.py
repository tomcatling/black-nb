"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "black_nb", "tests"]


@nox.session(python=["3.7.1"])
def mypy(session):
    """Type check code with mypy."""
    session.install("mypy")
    session.run("mypy", "--strict", "black_nb")


@nox.session(python=["3.7.1"])
def flake8(session):
    """Lint code with Flake8."""
    session.install("flake8")
    session.run("flake8", *SOURCES)


@nox.session(python=["3.7.1"])
def isort(session):
    """Check import ordering with isort."""
    session.install("isort")
    if session.posargs:
        session.run("isort", "--recursive", *session.posargs)
    else:
        session.run("isort", "--check-only", "--recursive", *SOURCES)


@nox.session(python=["3.7.1"])
def black(session):
    """Check code formatting with black."""
    session.install("black==18.9b0")
    if session.posargs:
        session.run("black", *session.posargs)
    else:
        session.run("black", "--check", *SOURCES)


@nox.session(python=["3.6.7", "3.7.1"])
def test(session):
    """Test and report coverage."""
    session.install("coverage")
    session.install("pytest")
    session.install("pytest-cov")
    session.install("codecov")
    session.run("pip", "install", ".")
    session.run("pytest", "--cov", "black_nb", "tests/")
    session.run("codecov")
