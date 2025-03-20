![Build Badge](https://github.com/software-students-spring2025/3-python-package-jeff-bezos/actions/workflows/build.yml/badge.svg?event=pull_request)

# Code Procrastinator

**Code Procrastinator** is a Python package that humanizes your code by giving it the ability to procrastinate—just like you! :D 

Instead of executing tasks efficiently, it gets *distracted*, mindlessly browses the internet, or justifies its procrastination with excuses. 

[PyPI Link](https://pypi.org/project/code-procrastinator/)

---
## Team Members
[Bryant To](https://github.com/bryantto08)
[Andrew Bao](https://github.com/andrew-bao)
[Jasmine Zhang](https://github.com/Jasminezhang666666)
[Imran Ahmed](https://github.com/mxa5251)

---

## **Installation**
You can install **Code Procrastinator** from **PyPI** using `pip`:
This package requires Python 3.7 or higher

```sh
pip install code-procrastinator
```

## **Contributing**
Want to improve **Code Procrastinator?** Follow these steps to set up your development environment!

### **Clone Repository**
```sh
git clone https://github.com/software-students-spring2025/3-python-package-jeff-bezos.git
cd 3-python-package-jeff-bezos
```

### **Create a Virtual Environment**
```sh
pip install pipenv
pipenv shell
```

### **Building**
We automatically upload our package to PyPi using twine.\
Before merging anything, ensure your contributions pass the unit tests

Important: PyPI will not let you upload a duplicate version, make sure to increment your version in your pyproject.toml file before pushing any changes. (Ex: 0.1.6 -> 0.1.7)
```sh
pytest procrastinator.py
```

## **Procrastinate()**
The `procrastinate` function simulates what a human might do when procrastinating—whether it's scrolling the web, making excuses, or delaying execution.

### **Usage**
To use Code Procrastinator in your own Python projects, simply import and call the procrastinate function:
```python
from code_procrastinator import procrastinate

# Make your program procrastinate for up to 10 seconds, with 3 random delays
procrastinate(10, 3)
```

### **Function Behavior**
- Randomly selects a number of **unique delays** between `0` and `max_time`.
- After each delay, it executes a **random procrastination action**.
- Available actions include:
  - Printing **excuses for procrastination**.
  - Opening a **fun website** for distraction.

### **Arguments**
| Argument    | Type | Description |
|------------|------|-------------|
| `max_time`  | `int`  | The maximum number of seconds for any delay. Must be greater than `0`. |
| `delay_count` | `int`  | The number of procrastination delays. Must be greater than `0`. |

### **Exceptions**
- **`ValueError`**: Raised if `max_time` or `delay_count` is less than or equal to `0`.

### **Return Value**
- **`set`**: A set of unique delay times used during procrastination.

---

## **Example Usage**
```python
>>> procrastinate(10, 3)
Procrastinating...
Let's take an internet break! :D https://en.wikipedia.org/wiki/Special:Random
Procrastinating...
Wow, this 4-hour video essay looks interesting...
Procrastinating...
I'll do it tomorrow
```

## **excuse_wrapper()**
The `excuse_wrapper` function will also procrasinate on providing correct output, will relay an excuse, and has a chance to completely fail on the task.

### **Usage**
Import excuse_wrapper, and use it as a decorator for the original function
```python
from code_procrastinator import excuse_wrapper
@procrastinator.excuse_wrapper
def add(x, y):
    return x + y
add(1, 2)
```
## **Example Usage**
```python
>>> add(1. 2)
Optimizing best possible answer
Processing... 25% done.
Still thinking... 50% done.
Someone just deleted my work... I need to start over again...
TBH... forget this I'll do it tomorrow.
```

