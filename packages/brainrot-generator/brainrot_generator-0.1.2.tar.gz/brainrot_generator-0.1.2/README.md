![Build Workflow](https://github.com/software-students-spring2025/3-python-package-5bigbooms/actions/workflows/build.yaml/badge.svg)

# Brain Rot Package




A Python package that generates brainrot—random snippets of internet culture, memes, and absurdity. Perfect for adding humor to your day, generating chaotic messages, and embracing the absurdity of Tiktok culture.
## Team Members

- [Tony Liu](https://github.com/tony102809)
- [Vladimir Kartamyshev ](https://github.com/lawaldemur)
- [Clarissa Choi](https://github.com/clammy424)
- [Giulia Carvalho](https://github.com/giulia-carvalho)
## Installation

You can install brainrot-generator directly from [PyPI](INSERT LINK HERE):

```bash
pip install brainrot-generator
```

## Features

Brainrot offers multiple text transformation functions for maximum chaos:

### 1. brainrot(n)

Generates n random brainrot phrases from a predefined list.

```python
from brainrot import brainrot

# Generate 3 random brainrot phrases
result = brainrot(3)
print(result)
```

### 2. get_brain_rot_of(name)
Retrieves a brainrot quote attributed to a specific name.
```python
from brainrot import get_brain_rot_of

# Get a brainrot phrase associated with "FettyWap"
print(get_brain_rot_of("FettyWap"))
```

### 3.  random_capitalization(phrase)
Randomly capitalizes letters in a phrase.
```python
from brainrot import random_capitalization

text = "brainrot is real"
print(random_capitalization(text))
# Output: "bRaInRoT Is rEaL"
```

### 4. rotify(input_string)
Appends " ahh" to any given string.
```python
from brainrot import rotify

text = "skibidi"
print(rotify(text))
# Output: "skibidi ahh"
```

### 5.  backwards_text(text)
Reverses the text string.
```python
from brainrot import backwards_text

text = "brainrot"
print(backwards_text(text))
# Output: "torniarb"
```

### 6. generate_brain_rot(word_counter)
Generates a string with word_counter words of brainrot.
```python
from brainrot import generate_brain_rot

print(generate_brain_rot(10))
```
## Command Line Usage

You can also use brainrot from the command line:
```bash
# Install the package
pip install brainrot-generator

python -m brainrot
```

Then follow the prompts to select a function and enter your text.

## Example Program

Here's a complete example program that demonstrates all functions:

```python
# example.py
from brainrot import brainrot, get_brain_rot_of, random_capitalization, rotify, backwards_text, generate_brain_rot

def demonstrate_brainrot():
    print("1. Random Brainrot:")
    print(brainrot(3))

    print("\n2. Get Brain Rot of 'FettyWap':")
    print(get_brain_rot_of("FettyWap"))

    print("\n3. Random Capitalization:")
    text = "this is brainrot"
    print(random_capitalization(text))

    print("\n4. Rotify:")
    print(rotify("skibidi"))

    print("\n5. Backwards Text:")
    print(backwards_text("brainrot"))

    print("\n6. Generate Brain Rot (10 words):")
    print(generate_brain_rot(10))

if __name__ == "__main__":
    demonstrate_brainrot()
```

Save this as `example.py` and run it with `python example.py`.

### Building the package

To build the package:

```bash
python -m build
```

This will generate distribution files in the `dist/` directory.

### Workflow for contributions

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests if necessary

3. Run tests to ensure everything works:
   ```bash
   pytest
   ```

4. Commit your changes and push to your branch:
   ```bash
   git add .
   git commit -m "Add your meaningful commit message"
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request to the `main` branch