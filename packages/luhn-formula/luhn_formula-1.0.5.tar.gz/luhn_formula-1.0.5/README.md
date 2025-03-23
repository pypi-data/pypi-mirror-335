# luhn-formula
Another python package of number validator and check digit generator based on Luhn's formula 😉. Luhn's formula was designed to protect against accidental input errors.

![Licence](https://img.shields.io/github/license/code-127/luhn-formula-py)
![PyPI](https://img.shields.io/pypi/v/luhn-formula?label=pypi%20luhn-formula)
![PyPI - Downloads](https://img.shields.io/pypi/dm/luhn-formula)
[![Python package](https://github.com/code-127/luhn-formula-py/actions/workflows/python-package.yml/badge.svg)](https://github.com/code-127/luhn-formula-py/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/code-127/luhn-formula-py/actions/workflows/python-publish.yml/badge.svg)](https://github.com/code-127/luhn-formula-py/actions/workflows/python-publish.yml)

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

## Usage
### install
    pip install luhn-formula
    
or
    
    git clone git@github.com:code-127/luhn-formula-py.git
### Example
    >>> from luhnformula import luhnformula as lf
    >>> lf.getcheckdigit("12345")
    '5'
    >>> lf.addcheckdigit("12345")
    '123455'
    >>> lf.isvalid("123455")
    True
## Function
### checksum(number: str) -> int
    Checksum vith the luhn formula
    Args:
        number : Number to calculate
    return:
        Result of luhn formula
    
### isvalid(number: str) -> bool:
    Validate number with the Luhn formula.
    Args:
        number: Number to validate.
    Returns:
        ``True`` when the: number is valid, otherwise ``False``.
### getcheckdigit(number: str) -> str:
    Generate check digit with the Luhn formula for a number.
    Args:
        number: Number used to generate the check digit.
    Return:
        the check digit for a number.
    Raise error:
        ValueError : Invalid number.
### addcheckdigit(number: str) -> str:
    Generate and add check digit with the luhn formula for a number
    Args:
        number: Number used to generate the check digit.
    Return:
        the number with the check digit.
    Raise error:
        ValueError : Invalid number.
