
# 🎵 Song Singer Generator

[![CI](https://github.com/software-students-spring2025/3-python-package-solapis/actions/workflows/ci.yml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-solapis/actions/workflows/ci.yml)

---

**Song Singer Generator** is a Python package that allows you to create and manage song collections by genre and artist. It enables developers to:
- Add new artists and songs  
- Search for specific names  
- Generate random songs and singers  

---

## 📦 **Package on PyPI**
👉 [**Visit the PyPI Page**](https://pypi.org/project/songsingergenerator/)  

---

## 🚀 **Installation**  
You can install the package directly from PyPI:

```bash
pip install songsingergenerator
```
---

## 💡 **How to Use**  
Here's how you can import and use the package in your Python project:

### ➡️ **Importing the package:**
```python
from songsingergenerator import music
```

### ➡️ **Example Code:**
Example for adding a new singer and song:
```python
from songsingergenerator.music import add_singer, random_song, random_singer, find_singer

# Add a singer and their songs
add_singer("Adele", "pop", ["Hello", "Someone Like You", "Rolling in the Deep"])

# Get a random song from the 'pop' genre
print(random_song("pop"))

# Get a random singer from the 'pop' genre
print(random_singer("pop"))

# Find a singer containing the word 'Adele'
print(find_singer("Adele"))
```

---

## 🛠️ **Available Functions**
| Function | Description | Example |
|----------|-------------|---------|
| `add_singer(singer, genre, songs=None)` | Adds a new singer and their songs to the collection. | `add_singer("Adele", "pop", ["Hello"])` |
| `random_song(genre=None)` | Returns a random song from a specific genre (or any genre if none is specified). | `random_song("pop")` |
| `random_singer(genre=None)` | Returns a random singer from a specific genre. | `random_singer("pop")` |
| `find_singer(keyword)` | Searches for singers whose names contain the specified substring. | `find_singer("Adele")` |

---

## 🏗️ **Contributing**  
We welcome contributions! Here’s how to get started:

### 1. **Clone the repository**:
```bash
git clone https://github.com/software-students-spring2025/3-python-package-solapis.git
cd 3-python-package-solapis
```

---

### 2. **Set up the virtual environment**  
We use **Pipenv** for managing dependencies.

- **Install Pipenv:**  
  ```bash
  pip install pipenv
  ```

- **Install dependencies (including build):**  
  ```bash
  pipenv install --dev build
  ```

### 3. **Activate the environment**  
Activate the Pipenv virtual environment:  
```bash
pipenv shell
```

### 4. **Build the package**  
Use `build` to create package artifacts:  
```bash
pipenv run python -m build
```

### 5. **Prepare and run tests**  
Before running tests, install the package in editable mode. Then, run tests using `pytest`:  
```bash
pipenv run pip install -e .
pipenv run pytest test/
```

---

## 👥 **Team**
| Name | GitHub Profile |
|------|----------------|
| **Yang Hu** | [@younghu312](https://github.com/younghu312) |
| **Ziqi Huang** | [@RyanH0417](https://github.com/RyanH0417) |
| **Zirui Han** | [@ZiruiHan](https://github.com/ZiruiHan) |
| **Zichao Jin** | [@ZichaoJin](https://github.com/ZichaoJin) |

---

## 🌐 **Running the Project**
To run the project locally:
1. Clone the repository.
2. Set up the virtual environment with Pipenv.
3. Run the test suite to make sure everything is working:
```bash
pipenv run pytest test/
```

4. Import the package and use it as described in the **How to Use** section.

