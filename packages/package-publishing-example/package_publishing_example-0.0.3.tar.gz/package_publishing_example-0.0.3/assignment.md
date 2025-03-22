# Python packaging workshop
25.03.2025

## Assignment 1: python package management with uv
In this assignment we will initialize a new python project using [uv](https://docs.astral.sh/uv/). Some of the things uv will do for us: structure/configure `pyproject.toml`, add/remove dependencies, manage python versions and virtual environments, run linters and tests, publish to pypi.

### step 1
Create a new git repository, either on the commandline or in the github user interface.

Commandline:

```{sh}
$ mkdir new_project
$ cd new_project
$ git init 
```

Github:
Create a new repository in the [user interface](https://github.com/new) and copy the project url.

```{sh}
$ git clone <NEW_PROJECT_URL>
$ cd new_project
```

### step 2
Install [uv](https://docs.astral.sh/uv/)

```{sh}
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

### step 3
Initialize a new python project using uv. In this workshop we will focus on building a python package, but uv can also be used for smaller projects such a single scripts. See https://docs.astral.sh/uv/concepts/projects/init/ for various options on how to initialize a project.

```{sh}
$ uv init --package
```

This should give you a relatively barebones `pyproject.toml` file containing all your projects configuration, and a few minimal folders and files for your python project. Note the `.python-version` file: this is uv's way (and also e.g. pyenv's way) of tracking which python version is used for the project, and will be used in the project's virtual environment. The following steps add functionality and dependencies to the project, which you can track in the `pyproject.toml` file.

### Step 3
We're going to add some code!

Uv already created a folder structure and `__init__.py` with some minimal content, so let's update that a bit. You can come up with something yourself, or past the below code in `src/new_project/__init__.py`.

```{python}
# Goes in __init__.py

def add(number1: int | float, number2: int | float) -> int:
    """
    Integer addition, if floats are provided they will be first 
    converted to integers by rounding down

    Examples:
        >>> add(1, 2)
        3

        >>> add(2.3, 4.5)
        6
  
    Args:
        number1 (int | float): first number for addition
        number2 (int | float): second number for addition
  
    Returns:
        int: sum of (possibly rounded down) inputs
    """
    return int(number1) + int(number2)
```

### Step 4

Let's add and run a linter/formatter to see if our code meets current best practices

```{sh}
$ uv add ruff
$ uv run ruff check
```

### Step 5

Let's add a testing framework to check our code for correctness. If you've used the code example above you can run a test on the examples in the docstring (i.e. a doctest), otherwise it is common to specify tests in a `tests` folder, e.g. in `tests/test_add.py`.

```{sh}
$ uv add pytest
$ uv run pytest --doctest-modules src
```

Note that we had to specify explicitly that we wanted pytest to run doctests. If you always want to do this, you can add the following lines to you `pyproject.toml`:

```{toml}
[pytest]
addopts = --doctest-modules
```

This way pytest always runs with the doctest option enabled, so the command for running tests would simplify to `uv run pytest`. 

### Step 6

Now that we have a functioning and tested codebase, let's start thinking about publishing to pypi!


## Assignment 2: Publishing a package to conda

## Assignment 3: Miscellaneous tips and tricks with github