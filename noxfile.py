"""Nox configuration."""

import nox

SOURCES = ["noxfile.py", "src", "tests"]


def install_dependencies(session):
    """Install Poetry and project dependencies."""
    session.install("poetry")
    session.run("poetry", "install")


@nox.session(python="3.7")
def mypy(session):
    """Type check code with mypy."""
    install_dependencies(session)
    session.run("poetry", "run", "mypy", "--strict", "src")


@nox.session(python="3.7")
def flake8(session):
    """Lint code with Flake8."""
    install_dependencies(session)
    session.run("poetry", "run", "flake8", *SOURCES)


@nox.session(python="3.7")
def coverage(session):
    """Test coverage."""
    install_dependencies(session)
    session.run("poetry", "run", "pytest", "--cov", "./")
    session.run("poetry", "run", "codecov")


@nox.session(python="3.7")
def black(session):
    """Check code formatting with black."""
    install_dependencies(session)
    session.run("poetry", "run", "black", "--check", *SOURCES)
