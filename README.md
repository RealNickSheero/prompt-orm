# PromptORM

**A Python library that provides SQL-like syntax for dynamic variable parsing in LangChain/LangGraph applications.**  
It enables structured data querying within prompt templates while maintaining clean and readable code.

---

## Features

- **SQL-like syntax** for querying nested data structures  
- **Seamless integration** with LangChain prompts  
- **Support for complex filtering conditions**  
- **Dynamic field selection**  
- **Automatic type conversion**  
- **Nested object traversal**

---

## Installation

### Clone the repository:
```bash
git clone https://github.com/RealNickSheero/prompt-orm
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Quick Start

### Query Syntax
The library supports SQL-like syntax for data querying.

---

## Examples

### Basic Selection:
```python
SELECT title FROM movies
```

### Filtering:
```python
SELECT title FROM movies WHERE rating > 8.0
```

### Complex Conditions:
```python
SELECT title FROM state.movies WHERE movies.genre = Action AND movies.rating > 8.0 OR movies.year >= 2020
```

---

## Core Components

- **StateConnector**: Manages data sources and provides access to your application state.  
- **PromptWrapper**: Wraps LangChain prompts and handles variable parsing.  
- **SmartPromptVariable**: Enables dynamic variable resolution and transformation within prompts.

---

## Operators

### Condition Operators:
- `==`: Equality  
- `!=`: Inequality  
- `>`: Greater than  
- `<`: Less than  
- `>=`: Greater than or equal  
- `<=`: Less than or equal  
- `CONTAINS`: String/List contains  
- `NOT_CONTAINS`: String/List does not contain  

### Expression Operators:
- `AND`: Logical AND  
- `OR`: Logical OR  

### Object Operators:
- `+`: Addition/Concatenation  
- `-`: Subtraction  
- `*`: Multiplication  
- `/`: Division  

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## Acknowledgments

- Built on top of **LangChain** and **Glom**  
- Inspired by **SQL syntax** for intuitive data querying

---

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
