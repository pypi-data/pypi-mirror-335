![CI](https://github.com/software-students-spring2025/3-python-package-teamproj3/actions/workflows/build.yml/badge.svg?branch=)

# Python Package Exercise

# Fortune Cookie Python Package

## Team Members

[Oluwapelumi Adesiyan](https://github.com/oadesiyan) <br />
[Nikita Bhaskar](https://github.com/nikitabhaskar) <br />
[Ariya Mathrawala](https://github.com/ariyamath29) <br />
[Emily Ney](https://github.com/EmilyNey) <br />

## What is This Package?

The Fortune Cookie package is a python package that will bring some joy to your day to day coding! You can can use this package to get a random fortune or find your lucky numbers.

## PyPI Package Link

[View our package on PyPI here](https://pypi.org)

## Installation

`pip3 install fortunecookiepkg`

## Usage

Import the package and use the following functions:

```
from fortunecookiepackage import get_random_fortune, get_lucky_numbers, get_daily_fortune, get_custom_fortune, get_themed_fortune

print(get_random_fortune())
#Output: Sell your ideas—they have exceptional merit.
print(get_lucky_numbers(6))
#Output: Lucky Numbers: [83, 40, 3, 45, 66, 17]
print(get_daily_fortune("Monday"))
#Output: Today's Fortune: Goodness is the only investment that never fails.
print(get_custom_fortune("Alice"))
#Output: Alice, A journey of a thousand miles begins with a single step.
print(get_themed_fortune("Love"))
#Output: The one you love is closer than you think.
```

Or try running the package as a script:

```
python -m fortunecookiepkg --random
python -m fortunecookiepkg --numbers 6
python -m fortunecookiepkg --daily monday
python -m fortunecookiepkg --custom Alice
python -m fortunecookiepkg --themed Love
```
## Example Program

Demo the package by running the Python file found [here](./example.py) or copy and paste the code below!

```
from fortunecookiepackage import get_random_fortune, get_lucky_numbers, get_daily_fortune, get_custom_fortune, get_themed_fortune

print(get_random_fortune()) 
#Output: Sell your ideas—they have exceptional merit.
print(get_lucky_numbers(6))
#Output: Lucky Numbers: [83, 40, 3, 45, 66, 17]
print(get_daily_fortune("Monday"))
#Output: Today's Fortune: Goodness is the only investment that never fails.
print(get_custom_fortune("Alice"))
#Output: Alice, A journey of a thousand miles begins with a single step.
print(get_themed_fortune("Love"))
#Output: The one you love is closer than you think.
```

## Development Guide

### Clone the Repository

```
git clone https://github.com/software-students-spring2025/3-python-package-teamproj3.git
cd 3-python-package-teamproj3
```

### Set up Virtual Environment

**Using `pipenv`:**

```
pip install pipenv
pipenv shell
```

**Using `venv`:**

```
python3 -m venv .venv
source .venv/bin/activate #On Mac
.venv\Scripts\activate.bat #On Windows
```

### Run Tests

Simple example unit tests are included within the tests directory. To run these tests use:

```
pytest tests/
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
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Added new feature"`).
4. Push to your branch (`git push origin feature-name`).
5. Open a pull request.

## Function Documentation

### get_random_function()

Generates a random fortune <br />
**Parameters:** <br />

- _None_

**Return:** <br />

- `str`: A randomly selected fortune.

---

### get_lucky_numbers(len)

Generates a set of lucky numbers. <br />
**Parameters:** <br />

- `len` (`int`): The number of lucky numbers to return

**Return:** <br />

- `list[int]`: A list of lucky numbers.

---

### get_daily_fortune(day)

Generates the same fortune for all users for that day. <br />
**Parameters:** <br />

- `day` (`str`): The weekday for which to retrieve a fortune.

**Return:** <br />

- `str`: The fortune for the given day.

---

### get_custom_fortune(name)

Generates a fortune that includes the user's name. <br />
**Parameters:**

- `name` (`str`): The name to include in the fortune.

**Return:** <br />

- `str`: A personalized fortune.

---

### get_themed_fortune(theme)

Genrates a fortune that relates to the selected theme. <br />
**Parameters:**

- `theme` (`str`): The theme for the fortune (ie. love, career, happiness)

**Return:** <br />

- `str`: A themed fortune.
