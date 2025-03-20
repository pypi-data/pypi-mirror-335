![Python build & test](https://github.com/software-students-spring2025/3-python-package-pypacks/actions/workflows/build.yaml/badge.svg)


# PyToSlang Translator
PyToSlang is a Python package that translates text abbreviations into their full meanings and back. It also changes slang words to emojis. Instructions/requirments for the creation of this package were referenced from the class course [instructions](./instructions.md).

## Features

- Convert full sentences to text abbreviations (e.g., "I don't know" → "idk").
- Translate slang words into emojis (e.g., "goat" → "🐐").
- Convert slang back into full words (e.g., "nm" → "nothing much").
- Supports case-insensitive translations.



## Pipy Package Link:
[PyToSlang Package Link]()

## Installation:
```pip install [package name] ```

# Usage:
Here is how you can use PyToSlang in your Python code:
### Translate Full Sentences to Slang:
```python
from PyToSlang import full_to_slang

text = "I don't know what to do"
translated_text = full_to_slang(text)
print(translated_text)  # Output: "idk what to do" 
```

### Translate Slang to Full Words:
```python
from PyToSlang import slang_to_full

text = "nm"
translated_text = slang_to_full(text)
print(translated_text)  # Output: "nothing much"
```

### Translate Slang to Emoji:
```python
from PyToSlang import slang_to_emoji

text = "goat"
translated_text = slang_to_emoji(text)
print(translated_text)  # Output: "🐐"
```
### Remove Slang from Sentence:
```python
from PyToSlang import remove_slang

text = "brb im going to get food"
cleaned_text = remove_slang(text)
print(cleaned_text) # Ouput: "im going to get food"
```

## Running PyToSlang in a Virtual Environment:
1. Create a pipenv-managed virtual environment and install the package:
```sh
pipenv install PyToSlang
```
2. Activate the virtual environment:
```sh
pipenv shell
```
3. Create a Python program file (e.g., my_program.py) and import PyToSlang:
```python
from PyToSlang import full_to_slang

text = "I don't know what to do"
translated_text = full_to_slang(text)
print(translated_text)  # Output: "idk what to do"
```
4. Run your program:
```sh
python3 my_porgram.py
```

5. Exit the virtual environement when done:
```sh
exit
```

## Example Program:
You can find a complete example program demonstrating all functions of this package in the repository: [Insert Link Here]()

## Contributing:
Want to contribute? Follow these steps!
1. Fork the repository.
2. Clone your fork: git clone https://github.com/software-students-spring2025/3-python-package-pypacks.git
3. Create a new branch: ```git checkout -b feature-name```
4. Install dependencies with ```pipenv install```.
5. Run tests using ```pytest```.
6. Push to your branch and create a pull request.

## Team:
- [Ajok Thon](https://github.com/ajokt123)
- [Nyjur Majok](https://github.com/nyjur1)
- [Arkadiuz Mercado](https://github.com/ArionM27)
- [Isaac Vivar](https://github.com/isaacv3)


