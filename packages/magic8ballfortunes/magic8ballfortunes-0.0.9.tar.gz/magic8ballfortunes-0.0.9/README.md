 Magic8Ball

[![Build Status](https://github.com/software-students-spring2025/3-python-package-package/actions/workflows/build.yaml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-package/actions/workflows/build.yaml/badge.svg)

Magic8Ball is a lighthearted fortune-telling package designed with rigorous software engineering practices. It demonstrates the complete lifecycle of a Python package—from development (using pipenv and pytest) to building (using setuptools and build), and distribution on PyPI (via twine). The package is installable via pip and includes an example program to showcase its features.

## Team Members

- [Gilad](https://github.com/giladspitzer)
- [Polaris](https://github.com/pinkmaggs)
- [Shayne](https://github.com/shayne773)
- [Andrew](https://github.com/Toudles)

## Project Links

- **PyPI Package:** [https://pypi.org/project/magic8ballfortunes/](https://pypi.org/project/magic8ballfortunes/)
- **Repository:** [GitHub Repository](https://github.com/software-students-spring2025/3-python-package-package.git)
- **Bug Tracker:** [GitHub Issues](https://github.com/software-students-spring2025/3-python-package-package/issues)

## Features & Usage

Magic8Ball provides four functions that deliver different types of fortunes:

- **tell_fortune()**  
  *Returns a random general fortune.*  
  ```python
  from magic8ballfortunes.fortunes import Magic8Ball
  print(Magic8Ball.tell_fortune())
  ```

- **personalized_fortune(name: str)**  
  *Returns a fortune that incorporates the given name.*  
  ```python
  print(Magic8Ball.personalized_fortune("Alice"))
  ```

- **fortune_by_category(category: str)**  
  *Returns a fortune based on a specified category (e.g., 'love', 'career', or 'health').*  
  ```python
  print(Magic8Ball.fortune_by_category("career"))
  ```

- **daily_by_birth_month(birth_month: str)**  
  *Returns a daily fortune that is consistent for the same day based on the provided birth month.*  
  ```python
  print(Magic8Ball.daily_by_birth_month("March"))
  ```

- **fortune_by_personality(personality_type: str)** 
  *Returns a fortune based on the specified personality type (e.g., 'anxious', 'kind', 'rude').*
  ```python
  print(Magic8Ball.fortune_by_personality("anxious"))
  ```


## Installation

Magic8Ball is managed with [Pipenv](https://pipenv.pypa.io/en/latest/). To set up your virtual environment and install the package along with its development dependencies:

1. Make sure you are **inside** the Pipenv virtual environment. If you haven’t already, run:
   ```bash
   pipenv shell
   ```
2. Install development dependencies by running:
    ```bash
    pipenv install --dev
    ```

Once installed, you can also install the package via pip if you have downloaded the package artifacts from PyPI:

```bash
pip install magic8ballfortunes
```

## Running the Example Program

An example program is provided within the package. To run the interactive fortune-telling interface from the command line, execute:

```bash
python -m magic8ballfortunes
```

This will clear your screen and prompt you to choose a type of fortune.

## Running Tests

Unit tests are written using [pytest](https://docs.pytest.org/en/latest/). To run the full test suite, simply execute:

```bash
pipenv run pytest
```

This will verify that each function (including handling of valid, edge, and error cases) behaves as expected.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Branching:** Create a feature branch off of the `main` branch.
2. **Pull Request:** Once your changes are ready, open a pull request for review.
3. **Review:** Ensure that all tests pass and your code meets our style guidelines.
4. **Merge:** After approval, merge your changes into the `main` branch and delete your feature branch.

For more detailed instructions on setting up the environment, building the package, and running tests, please refer to the [instructions.md](./instructions.md) file in the repository.

## Configuration & Deployment

- **Configuration:** No additional configuration or environment variables are required to run Magic8Ball.
- **CI/CD:** GitHub Actions is configured to build and test the package on multiple recent Python versions for every pull request and then deploy to PyPi when pushed on main.
