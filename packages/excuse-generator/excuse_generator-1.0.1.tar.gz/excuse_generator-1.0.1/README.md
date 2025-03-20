## Excuse Generator for Software Engineers

![Build Status](https://github.com/software-students-spring2025/3-python-package-pyckle-jar/actions/workflows/python-package.yml/badge.svg)
![Build Status](https://github.com/software-students-spring2025/3-python-package-pyckle-jar/actions/workflows/event-logger.yml/badge.svg)

excuse-generator is a fun and practical Python package that helps software engineers come up with excuses for common coding problems. Whether you're dealing with bugs, missed deadlines, PR delays, failed deployments, or awkward meetings, this package has you covered!

## Table of Contents


- [Installation](#installation)
- [Usage](#usage)
- [Functions](#functions)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)

## Installation

### With pipenv:

1. Install **pipenv** if you don't have it yet:

```bash
pip install pipenv
```

2. Install the package and dependencies:

```bash
pipenv install --dev
pipenv shell
```

### Or with pip:

1. Install the package:

```bash
pip install excuse-gnerator
```

## Usage

You can import the **excuse_genertator** module and start generating excuses! Here are a few examples of how to use the package:

```python
from excuse_generator.excuses import generate_excuse, add_custom_excuse, random_excuse, list_categories

# Get a random excuse
print(random_excuse())

# Get an excuse for a specific category (e.g., bug, deadline)
print(generate_excuse("bug"))

# Add a custom excuse to a category
add_custom_excuse("bug", "It's a feature, not a bug.")
print(generate_excuse("bug"))

# List all available categories
print(list_categories())

```

### Example Output

```plaintext
It works on my machine.
The timeline was more of a suggestion.
It's a feature, not a bug.
['bug', 'deadline', 'PR', 'meeting', 'deployment']

```

## Functions

## Authors
