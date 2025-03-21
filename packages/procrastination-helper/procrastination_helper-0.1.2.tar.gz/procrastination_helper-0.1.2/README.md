# procrastination_helper

![Python build & test](https://github.com/software-students-spring2025/3-python-package-market-correction/actions/workflows/build.yaml/badge.svg)

---

## Project Description

**procrastination_helper** is a user-friendly application designed to assist individuals in managing their tasks and overcoming procrastination. By generating creative and humorous custom excuses, the app provides users with a lighthearted way to navigate their responsibilities. Whether you need a reason to delay a chore, skip a meeting, or take a break from studying, Procrastination Helper offers a variety of tailored excuses to suit any situation. With its intuitive interface and engaging content, this app aims to make task management more enjoyable and less stressful.

---

## PyPI Package

**[procrastination_helper on PyPI](https://pypi.org/project/procrastination-helper/0.1.0/)**

---

## Importing and Using procrastination_helper in Your Code

Developers can import and use `procrastination_helper` functions in their own projects.

### Available Functions & Examples

#### 1. `get_custom_excuse(task)`
Returns a personalized excuse based on the task using random templates.

```python
from procrastination_helper import get_custom_excuse
print(get_custom_excuse("homework"))
```

#### 2. `delay_timer(minutes)`
Allows the user to set a procrastination timer.

```python
from procrastination_helper import delay_timer
delay_timer(15)
```

#### 3. `get_excuse_list(n)`
Returns a specified number `n` of random excuses from the sample excuses list.

```python
from procrastination_helper import get_excuse_list
print(get_excuse_list(3))
```

#### 4. `get_excuse()`
Returns a single random excuse from a predefined list of sample excuses.

```python
from procrastination_helper import get_excuse
print(get_excuse())
```

#### 5. `quotes.get(num_quotes)`
Returns a specified number `num_quotes` of random motivational quotes about procrastination.

```python
from procrastination_helper import quotes
print(quotes.get(num_quotes=2))
```

## Using the Interactive Interface

After installing the package, you can use the interactive command-line interface:

### Using pipenv
```bash
# Install the package
pipenv install procrastination-helper

# Run the interactive interface
pipenv run python -m procrastination_helper
```

### Using pip
```bash
# Install the package
pip install procrastination-helper

# Run the interactive interface
python -m procrastination_helper
```

You can also use command-line arguments for specific features:

```bash
# Get 3 procrastination quotes
pipenv run python -m procrastination_helper --feature quotes --number 3

# Set a delay timer for 5 minutes
pipenv run python -m procrastination_helper --feature delay --time 5
```

## Running the Example Program

**[Example Program](./example.py)**

---

1. #### Install the procrastination_helper package
```bash
pipenv install procrastination-helper
```

2. #### Clone the repository to get the example.py
```bash
git clone https://github.com/software-students-spring2025/3-python-package-market-correction.git
cd 3-python-package-market-correction
```

3. #### Install the package in the repository's environment
```bash
pipenv install procrastination-helper
```

4. #### Run the example
```bash
pipenv run python example.py
```

---

## Developer Setup Guide

Follow these steps to set up and contribute to the **procrastination_helper** project:

### 1. Clone the Repository
```bash
git clone https://github.com/software-students-spring2025/3-python-package-market-correction.git
cd 3-python-package-market-correction
```

### 2. Set Up a Virtual Environment

You can use either `venv` or `pipenv`:

- **Using venv:**
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

- **Using pipenv:**
```bash
pipenv shell
```

### 3. Install Dependencies

- **Using venv:**
```bash
pip install -e .[dev]
```

- **Using pipenv:**
```bash
pipenv install -e .[dev]
```

### 4. Run Tests

Ensure everything is working by running:
```bash
pytest
```

### 5. Build the Package

To package the application, use:
```bash
python -m build
```

### 6. Run the Application

Navigate to the source directory and execute:
```bash
cd src
python3 -m procrastination_helper
```

---

## Team Members

| Name           | NYU Email           | GitHub Profile                                           |
|----------------|---------------------|----------------------------------------------------------|
| Chris Leu      | cl3880@nyu.edu      | [cl3880](https://github.com/cl3880)                      |
| Ava August     | aca9900@nyu.edu     | [aaugust22](https://github.com/aaugust22)                |
| Keith Dusling  | ksd332@nyu.edu      | [kdusling56](https://github.com/kdusling56)              |
| Joel Kim       | jdk91370@nyu.edu    | [joel-d-kim](https://github.com/joel-d-kim)              |

---

## Environment Variables & Starter Data
This project does not require any environment variables or a database.

## Secret Configuration Files
This project does not require any secret configuration files.

