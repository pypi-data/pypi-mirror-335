# isoddeven
## A Python package to check if a number is odd or even.

[![PyPI - Version](https://img.shields.io/pypi/v/isoddeven)](https://pypi.org/project/isoddeven/)
[![Pepy Total Downloads](https://img.shields.io/pepy/dt/isoddeven)](https://pypi.org/project/isoddeven/)
[![PyPI - License](https://img.shields.io/pypi/l/isoddeven)](https://pypi.org/project/isoddeven/)
[![GitHub deployments](https://img.shields.io/github/deployments/nilaysarma/isoddeven/release)](https://github.com/nilaysarma/isoddeven/deployments/release)
[![PyPI - Status](https://img.shields.io/pypi/status/isoddeven)](https://pypi.org/project/isoddeven/)

## 🚀 Installation
You can install the package using pip:
```sh
pip install isoddeven
```
To update the package use this command:
```sh
pip install --upgrade isoddeven
```

## 📖 Usage
Here's a quick example of how to use it:
```python
from isoddeven import isoddeven

print(isoddeven.isodd(1)) # True
print(isoddeven.isodd(2)) # False
print(isoddeven.iseven(3)) # False
print(isoddeven.iseven(4)) # True
print(isoddeven.state(5)) # odd
print(isoddeven.state(6)) # even
```

## 🔷 Run in terminal
You can run it in your terminal by using it's Command Line Interface (CLI) commands:
```sh
# Checks if the number is odd or even
isoddeven <number>

# Examples
isoddeven 7
7 is odd

isoddeven 10
10 is even
```

You can use `-o` (or `--odd`) to check if the number is odd, and `-e` (or `--even`) to check if it's even. These return True or False.
```sh
# Odd Check
isoddeven -o <number>

# Even check
isoddeven -e <number>

# Examples
isoddeven -o 1
True
isoddeven -o 2
False

isoddeven -e 4
True
isoddeven -e 5
False
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/nilaysarma/isoddeven/blob/main/LICENSE) file for details.