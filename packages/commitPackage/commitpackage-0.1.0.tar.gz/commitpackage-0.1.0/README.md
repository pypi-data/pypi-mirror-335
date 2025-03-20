[![CI](https://github.com/software-students-spring2025/3-python-package-pack-it-up/actions/workflows/build.yml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-pack-it-up/actions/workflows/build.yml)

# LazyCommit Package

## Team Members

1. [Jasmeen Kaur](https://github.com/jk7297)
2. [Sophia Schlichting](https://github.com/schlichtings)
3. [Preston Lee](https://github.com/prestonglee0805)
4. [Julia Ahn](https://github.com/juliaahn)

## About LazyCommit

A fun and lighthearted package for generating random and styled Git commit messages.

## PyPI Package Link

## Installation

```
pip install commitPackage
```

## Usage

Import the package and use the following functions:

```
from src.commitPackage.lazyCommit import (
    generate_commit_message, random_commit_message,
    git_blame_excuse, generate_haiku, add_commit_message, add_excuse, add_haiku
)

print(random_commit_message())
#Output: Random commit message from the database

print(generate_commit_message('funny'))
#Output: Random commit message with the specific style

print(git_blame_excuse())
#Output: Random excuse from database

print(generate_haiku())
#Output: Random haiku from the database

print(add_commit_message('funny', 'Example Program Commit Message'))
#Output: Add commit message to a style

print(add_excuse('Example Program Excuse'))
#Output: Add an excuse to the database

print(add_haiku('Breeze whispers through trees, Golden leaves dance on the wind, Autumn's soft embrace.'))
#Output: Add a haiku to the databse
```

Or try running the package as a script:

```
python -m commitPackage --random

python -m commitPackage --style funny
python -m commitPackage --style serious
python -m commitPackage --style professional
python -m commitPackage --style technical

python -m commitPackage --blame

python -m commitPackage --haiku

python -m commitPackage --addMessage funny "Fixed a typo"
python -m commitPackage --addMessage serious "Refactored database access layer"
python -m commitPackage --addMessage chaotic "DO NOT DELETE - I'm warning you"

python -m commitPackage --addExcuse "The intern wrote this line"

python -m commitPackage --addHaiku "Branches intertwine, Merge conflicts are poetry, Git writes our stories."
```

## Running [`exampleProgram.py`](exampleProgram.py)

To run [`exampleProgram.py`](exampleProgram.py), make sure you are in your virtual environment and have all dependencies installed. Then, run the following command:

```bash
python exampleProgram.py
```

## Development Guide

### Clone the Respository 

```
git clone git@github.com:software-students-spring2025/3-python-package-pack-it-up.git
cd 3-python-package-pack-it-up
```

### Set up Virtual Environment

```
pip install pipenv
pipenv shell
```

### Run Tests

Units test are provided in the tests directory. To run those use:
```
python -m pytest 
```

or  this if you have a python3:
```
python3 -m pytest 
```

### Build and Publish Package 

To build the package and upload it to TestPyPI:

```
python -m build
twine upload -r testpypi dist/*
```

To publish it to PyPI:
```
twine upload dist/*
```

## Contribute

To contribute to this project follow these steps:

1. Clone the repository
2. Create a feature branch 
```
git checkout -b feature-name.
```
3. Commit your changes 
```
git add .
git commit -m "Added new feature"
```
4. Push to your branch 
```
git push origin feature-name
```
5. Open a pull request.

# Function Documentation

## random_commit_message()

Generates a randomly selected commit message from the database

### Parameters:

- None

### Return:

- `str`: A randomly selected commit message

---

## generate_commit_message(style)

Generates a randomly selected commit message that has the style the user specified

### Parameters:

- `style` (`str`): the style of message the user wants

### Return:

- `str`: A randomly selected commit message from the user's desired style

---

## git_blame_excuse()

Generates a randomly selected excuse

### Parameters:

- None

### Return:

- `str`: A randomly selected excuse

---

## generate_haiku()

Generates a randomly selected haiku

### Parameters:

- None

### Return:

- `str`: A randomly selected excuse

---

## add_commit_message(style, message)

Allows a user to create a new commit message

### Parameters:

- `style` (`str`): the style of message the user wants to add
- `message` (`str`): the message the user wants to add

### Return:

- `str`: if the message was successfully saved to the database, a confirmation str will be displayed
- `str`: if the message already exists in the database, a str outlining that will be displayed
- `str`: if there are issues with saving the message, and error message will be displayed

---

## add_excuse(message)

Allows a user to create a new excuse

### Parameters:

- `message` (`str`): the excuse the user wants to add

### Return:

- `str`: if the excuse was successfully saved to the database, a confirmation str will be displayed
- `str`: if the excuse already exists in the database a str outlining that will be displayed
- `str`: if there are issues with saving the excuse an error message will be displayed

---

## add_haiku(message)

Allows a user to create a new haiku

### Parameters:

- `message` (`str`): the haiku the user wants to add

### Return:

- `str`: if the haiku was successfully saved to the database, a confirmation str will be displayed
- `str`: if the haiku already exists in the database, a message outlining that will be displayed
- `str`: if there are issues with saving the haiku an error message will be displayed## Deveopment Guide

