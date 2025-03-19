# DemoPackage-cs467

[![Build and Test](https://github.com/software-students-spring2025/3-python-package-cs467/actions/workflows/build.yaml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-cs467/actions/workflows/build.yaml)

A fun Python package that enhances developer workflows with banners, random fortunes, emojis, a daily planner, and a password strength checker.

## 📌 Overview
DemoPackage-cs467 is a lightweight and entertaining Python package designed to add a bit of fun to a developer's workflow. It provides:
- **Fortune Cookie Generator**: Get random, amusing developer fortunes.
- **Emoji Generator**: Generate relevant emojis based on keywords.
- **Owl Banner Generator**: Display a stylish ASCII owl banner with project info.
- **Daily Planner**: Reads user input and generate daily planner sorted by priority level of each task
- **Password Strength Checker**: Evaluates the strength of a password

## 📥 Installation
You can install the package directly from PyPI using pip:
```sh
pip install demopackage-cs467
```
Or install from source:
```sh
# Clone the repository
git clone https://github.com/software-students-spring2025/3-python-package-cs467.git
cd 3-python-package-cs467

# Install in development mode
pip install -e .
```

## 🚀 Usage
### 1. Fortune Cookie Generator
```python
from DemoPackage.furtune_cookie import dev_fortune_cookie

print(dev_fortune_cookie("general"))  # Get a general fortune
```

### 2. Emoji Generator
```python
from DemoPackage.generate_emoji import generate_emoji

print(generate_emoji("laugh"))  # Returns a laughing emoji
```

### 3. Owl Banner Generator
```python
from DemoPackage.owl_banner import gl_banner

gl_banner(1)  # Displays an ASCII owl banner with project info
```

### 4. Daily Planner
```python
from DemoPackage.daily_planner import daily_planner

print(daily_planner(username)) # Displays a formated daily planner
```

### 5. Password Strength Checker
```python
from DemoPackage.password_strength import password_strength

print(password_strength(password)) # returns the strength of 'password'
```

## 🛠 Development Setup
If you wish to contribute, set up your development environment as follows:
```sh
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
pip install pytest build twine
```

### 🧪 Running Tests
```sh
pytest
```

## 👥 Contributors
- [Michael Liu](https://github.com/Michaelliu1017) - Owl Banner Generator
- [Jiangbo Shen](https://github.com/js-montgomery) - Daily Planner & Password Strength Checker
- [Polaris Wu](https://github.com/Polaris-Wu450) - Fortune Cookie Generator
- [Felix Guo](https://github.com/Fel1xgte) - Emoji Generator

## ⚙️ Configuration & Environment Variables
No additional environment variables are required. The package runs out of the box.

## 🔑 License
This project is licensed under the GNU General Public License v3. See the LICENSE file for details.
