![Build Status](https://github.com/software-students-spring2025/3-python-package-pyunit/actions/workflows/ci.yml/badge.svg)

# Documentation

The `lazydev` package provides funny and light-hearted tools for developers, including:

- Randomly generated commit messages.
- Auto-generated pull request titles.
- Creative excuses for not writing tests.
- Handy procrastination tips.

## Installation

### Running on Any Platform
Windows: Use PowerShell, ensure `pip` and `git` are installed. <br />
macOS: Use Terminal, ensure `brew` or `pip` is updated. <br />
Linux: Use `bash`, ensure `python3` and `pipenv` are installed.

### Package
To install our package, simply run:
```
pip install lazydev
```
Or if you would like to install directly from the source, use:
```
git clone https://github.com/software-students-spring2025/3-python-package-pyunit.git
cd lazydev
pip install .
```

## Usage Guide

### 1. Generate a Lazy Commit Message
```
from lazydev import lazy_commit_message

# generate a random commit message
print(lazy_commit_message())

# generate a commit message with a keyword
print(lazy_commit_message(keyword="HOTFIX"))
```
#### Example Output:
```
A weird piece of code was refactored. Hopefully, it works.
HOTFIX: I patched the function. Maybe this will work?
```

### 2. Generate a Lazy Pull Request Title
```
from lazydev import lazy_pull_request

# generate a random pull request title for github
print(lazy_pull_request())

# generate a pull request title with a custom verb and noun
print(lazy_pull_request(inputVerb="improved", inputNoun="error handling"))
```

#### Example Output:
```
Fixed a bug. Just accept the pull request.
Improved error handling to align with new version.
```

### 3. Generate a Lazy Test Excuse
```
from lazydev import lazy_test_excuse

# Generate a random test excuse
print(lazy_test_excuse())

# Generate a test excuse with a specific reason
print(lazy_test_excuse(reason="ran out of coffee"))
```

#### Example Output
```
I'll add tests later...
I was going to write tests, but ran out of coffee.
```

### 4. Get a Procrastination Tip
```
from lazydev import procrastination_tip

# Generate a random procrastination tip
print(procrastination_tip())

# Generate a procrastination tip with a keyword
print(procrastination_tip(keyword="BREAK TIME"))
```

#### Example Output
```
Go grab some oreos. Snacks help you think... or keep you distracted for 10 minutes.
BREAK TIME: Grab a drink! I recommend a coffee. You can buy some around your neighborhood.
```

## Example Program
For a complete example that uses all the functions, check out this example script: 🔗 [lazydev_example.py](https://github.com/software-students-spring2025/3-python-package-pyunit/blob/main/lazydev_example)
```
from lazydev import lazy_commit_message, lazy_pull_request, lazy_test_excuse, procrastination_tip

print(lazy_commit_message("BUGFIX"))
print(lazy_pull_request("refactored", "database queries"))
print(lazy_test_excuse("the server went down"))
print(procrastination_tip("STUDY BREAK"))
```
## Contributing to and Modifying Lazy Dev Tools

Follow these steps to set up your environment in order to contribute!

### 1. Clone the Repository
```
git clone https://github.com/software-students-spring2025/3-python-package-pyunit.git
cd lazydev
```

### 2. Set Up a Virtual Environment
```
pip3 install pipenv       # install pipenv
pipenv shell              # run the shell
python                    # enter the shell
```

### 3. Install Dependencies
```
pipenv install --dev
```

### 4. Run Tests
Ensure everything works before making changes:
```
pipenv run pytest tests/
```

### 5. Build the Package
```
pip install build
python -m build
```

### 6. Install Locally for Development
```
pip install -e .
```

### 7. Create a Pull Request
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Description of changes"`).
4. Push to your fork (`git push origin feature-name`).
5. Open a Pull Request on GitHub.

You have successfully contributed your modifications and changes to our package! Thank you for submitting your work!

## Team Members
[Mahmoud Shehata](https://github.com/MahmoudS1201) <br /> 
[Syed Naqvi](https://github.com/syed1naqvi) <br />
[Brandon Morales](https://github.com/BAMOEQ) <br />
[David Yu](https://github.com/DavidYu00)

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/software-students-spring2025/3-python-package-pyunit/blob/main/LICENSE) file for details.