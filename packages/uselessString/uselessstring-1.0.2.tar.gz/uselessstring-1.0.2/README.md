![Build and Test](https://github.com/software-students-spring2025/3-python-package-goodgood/actions/workflows/build.yml/badge.svg)

# 🚀 uselessString Package  

## 📌 Introduction  
`uselessString` is a Python package that provides fun and useful string manipulation functions. It includes features such as **palindromes**, **word reversal**, **customized repetitiveness**, **emotive expressions**, and more.  

🔗 **PyPI Package:** [uselessString on PyPI](https://pypi.org/project/uselessString/1.0.2/)  

---

## 📦 Installation  

To install the package from **PyPI**, run:  
```bash
pip install uselessString
```

To upgrade to the latest version:  
```bash
pip install --upgrade uselessString
```

To install directly from **source (for development)**:  
```bash
git clone https://github.com/software-students-spring2025/3-python-package-goodgood.git
cd uselessString
pip install -e .
```

---

## 📖 Documentation  

### 🔹 **Functions Overview**  

| Function | Description | Example Input | Example Output |
|----------|-------------|---------------|---------------|
| `palindrome(s)` | Reverses every character in a given string | `"Hello, world!"` | `"!dlrow ,olleH"` |
| `reverse(s)` | Reverses the order of words in a string | `"Hello, world!"` | `"world! Hello,"` |
| `echo(s, i)` | Repeats the word `s`, `i` times | `("Hi", 3)` | `"Hi Hi Hi"` |
| `angry(s)` | Randomly inserts special characters to express anger | `"I am upset"` | `"I am @%! upset!"` |
| `mocking(s)` | Converts a string into alternating uppercase/lowercase | `"hello"` | `"HeLLo"` |
| `emoji(s, emotion)` | Adds an emoji corresponding to the given emotion | `("Hello", "happy")` | `"Hello 😊"` |
| `random(s)` | Shuffles the characters randomly | `"Python"` | `"nPyoth"` (randomized) |

---

## 💡 Usage  

### **Basic Example**
```python
from uselessString.palindrome import palindrome
from uselessString.reverse import reverse
from uselessString.echo import echo
from uselessString.mocking import mocking
from uselessString.angry import angry
from uselessString.emoji import emoji
from uselessString.random import randomize

test_string = "Hello, World!"
print(palindrome(test_string))   # "!dlroW ,olleH"
print(reverse(test_string))      # "World! Hello,"
print(echo("Python", 3))         # "Python Python Python"
print(mocking(test_string))      # "HeLLo, WoRLd!"
print(angry(test_string))        # "Hello, %@!World!"
print(emoji(test_string, "happy"))  # "Hello, World! 😊"
print(randomize(test_string))    # "oWlr!dHleo, " (randomized)
```

---

## 🛠️ Contributing  

We welcome all contributions! Please follow these steps to contribute:  

1. **Fork the repository**  
2. **Clone your fork**  
   ```bash
   git clone https://github.com/software-students-spring2025/3-python-package-goodgood.git
   cd uselessString
   ```
3. **Create a feature branch**  
   ```bash
   git checkout -b feature-branch-name
   ```
4. **Make your changes and commit**  
   ```bash
   git add .
   git commit -m "Added new feature XYZ"
   ```
5. **Push to your fork and create a pull request**  
   ```bash
   git push origin feature-branch-name
   ```
6. **Wait for code review and merge!** 🎉  

---

## 🔍 Running Tests  

To ensure the package is working correctly, run:  
```bash
pytest
```

---

## 📜 License  
This project is licensed under the GNU General Public License v3. See the LICENSE file for details.

---

## 👥 Contributors  
- **Tim Yan**: [GitHub](https://github.com/T1mmmmm)  
- **Bill Feng**: [GitHub](https://github.com/BillBBle)  
- **Warren Wu**: [GitHub](https://github.com/W0rren12)  
- **mh**: [GitHub](https://github.com/mh6355)  

---

