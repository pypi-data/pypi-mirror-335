```markdown
# Xsql

Xsql is a fast, secure, and simple database library for Python designed to overcome common issues found in other database libraries. It uses parameterized queries to prevent SQL injection and supports AES-GCM encryption for sensitive data. Additionally, it leverages all available CPU power and, if available, GPU acceleration (via cupy) for high-speed encryption and decryption.

**Project:** Xsql  
**Creator:** Mohammad Taha Gorji

---

## Features

- **Connection Pooling:** Efficiently manages multiple database connections.
- **SQL Injection Prevention:** Uses parameterized queries to safeguard against SQL injection.
- **Data Encryption:** Supports AES-GCM encryption with optional GPU acceleration.
- **Transaction Management:** Simplified transaction handling through context managers.
- **Extensible Driver System:** Built-in XsqlDriver for SQLite with easy extensibility to other databases.
- **Comprehensive API:** A full suite of methods for secure insert, select, and update operations.

---

## Installation

Users can install Xsql using pip:

```bash
pip install Xsql
```

**Dependencies:**
- Python 3.6+
- [cryptography](https://pypi.org/project/cryptography/)
- (Optional) [cupy](https://pypi.org/project/cupy/) for GPU acceleration

---

## Getting Started

Below is a simple example that demonstrates how to use Xsql. This example creates an in-memory database, sets up a table, inserts encrypted data, retrieves it, and uses transactions.

```python
import os
from xsql import XsqlDriver, Encryptor, Database

driver = XsqlDriver(":memory:")
key = os.urandom(32)
encryptor = Encryptor(key, use_gpu=True)
db = Database(driver, pool_size=3, encryption=encryptor)

db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name BLOB NOT NULL, age INTEGER NOT NULL)")
db.secure_insert("users", {"name": "Alice", "age": 30})
db.secure_insert("users", {"name": "Bob", "age": 25})

users = db.secure_select("users", ["id", "name", "age"], encrypted_cols=["name"])
print("Users:", users)

try:
    with db.transaction() as txn:
        txn.exec_query("INSERT INTO users (name, age) VALUES (?, ?)", (encryptor.encrypt("Charlie".encode('utf-8')), 22))
except Exception as e:
    print("Transaction error:", e)

users = db.secure_select("users", ["id", "name", "age"], encrypted_cols=["name"])
print("Users after transaction:", users)

db.close()
```

---

## API Documentation

### XsqlError
- **Description:** Custom exception for Xsql errors.
- **Usage:** Raised for connection issues, query execution errors, encryption/decryption failures, and more.

---

### BaseDriver (Abstract Class)
- **Description:** Defines the interface for database drivers.
- **Methods:**
  - `connect()`: Establish and return a database connection.
  - `execute(connection, query, params)`: Execute a parameterized query.
  - `commit(connection)`: Commit the current transaction.
  - `rollback(connection)`: Roll back the current transaction.
  - `close(connection)`: Close the database connection.

---

### XsqlDriver
- **Description:** Default driver for Xsql, utilizing SQLite.
- **Constructor:**
  ```python
  XsqlDriver(db_path, **options)
  ```
  - `db_path`: Path to the SQLite database file (or ":memory:" for in-memory).
  - `options`: Additional connection options.
- **Methods:** Implements all methods from `BaseDriver` (`connect`, `execute`, `commit`, `rollback`, `close`).

---

### ConnWrapper
- **Description:** A thread-safe wrapper for a database connection.
- **Methods:**
  - `exec_query(query, params=None)`: Execute a query on the connection.
  - `do_commit()`: Commit the current transaction.
  - `do_rollback()`: Roll back the current transaction.
  - `do_close()`: Close the connection.

---

### ConnPool
- **Description:** Manages a pool of database connections for improved performance in multithreaded environments.
- **Constructor:**
  ```python
  ConnPool(driver: BaseDriver, pool_size=5, timeout=30)
  ```
  - `driver`: A database driver instance (e.g., XsqlDriver).
  - `pool_size`: Number of connections in the pool.
  - `timeout`: Timeout in seconds for acquiring a connection.
- **Methods:**
  - `acquire()`: Get a connection from the pool.
  - `release(conn)`: Return a connection to the pool.
  - `close_all()`: Close all connections in the pool.

---

### DBTransaction
- **Description:** A context manager for handling database transactions.
- **Usage:**
  ```python
  with db.transaction() as txn:
      txn.exec_query(...)
  ```
- **Methods:**
  - `exec_query(query, params=None)`: Execute a query within the transaction.
  - `commit()`: Commit the transaction.
  - `rollback()`: Roll back the transaction.

---

### Encryptor
- **Description:** Provides AES-GCM encryption and decryption. Optionally uses GPU acceleration via cupy.
- **Constructor:**
  ```python
  Encryptor(key: bytes, use_gpu: bool = False)
  ```
  - `key`: Encryption key (must be 16, 24, or 32 bytes).
  - `use_gpu`: Set to True to enable GPU acceleration if cupy is installed.
- **Methods:**
  - `encrypt(data: bytes) -> bytes`: Encrypt data and return the encrypted token.
  - `decrypt(token: bytes) -> bytes`: Decrypt the token to retrieve the original data.

---

### Database
- **Description:** Main class for interacting with the Xsql database.
- **Constructor:**
  ```python
  Database(driver: BaseDriver, pool_size=5, encryption: Encryptor = None)
  ```
  - `driver`: Database driver (e.g., XsqlDriver).
  - `pool_size`: Number of connections in the pool.
  - `encryption`: An instance of `Encryptor` for encrypting sensitive data.
- **Methods:**
  - `execute(query, params=None)`: Execute non-SELECT queries (INSERT, UPDATE, DELETE).
  - `query(query, params=None)`: Execute a SELECT query and return all rows.
  - `transaction()`: Get a transaction context manager.
  - `secure_insert(table: str, data: dict)`: Securely insert data (encrypts text columns if encryption is enabled).
  - `secure_select(table: str, cols: list, encrypted_cols: list = None, where: str = "", where_params: tuple = ())`: Securely select and decrypt data.
  - `secure_update(table: str, data: dict, where: str, where_params: tuple)`: Securely update data with encryption.
  - `close()`: Close all database connections.

---

## Project-Based Tutorial

This project tutorial guides you through building a simple user management system using Xsql.

### Step 1: Setup Your Project
1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a file called `app.py`.**

### Step 2: Initialize the Database
In `app.py`, add the following code to initialize the database:

```python
import os
from xsql import XsqlDriver, Encryptor, Database

driver = XsqlDriver("users.db")
key = os.urandom(32)
encryptor = Encryptor(key, use_gpu=False)
db = Database(driver, pool_size=5, encryption=encryptor)

db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name BLOB NOT NULL, age INTEGER NOT NULL)")
```

### Step 3: Insert User Data
Securely insert user data:

```python
db.secure_insert("users", {"name": "Alice", "age": 30})
db.secure_insert("users", {"name": "Bob", "age": 25})
```

### Step 4: Retrieve and Display Data
Retrieve the data and automatically decrypt the encrypted columns:

```python
users = db.secure_select("users", ["id", "name", "age"], encrypted_cols=["name"])
print("User List:", users)
```

### Step 5: Update User Data
Securely update a user's information:

```python
db.secure_update("users", {"name": "Alice Updated"}, "id = ?", (1,))
```

### Step 6: Transaction Management
Perform multiple operations in a transaction to ensure data consistency:

```python
try:
    with db.transaction() as txn:
        txn.exec_query("INSERT INTO users (name, age) VALUES (?, ?)",
                       (encryptor.encrypt("Charlie".encode('utf-8')), 22))
except Exception as e:
    print("Transaction failed:", e)
```

### Step 7: Cleanup
When finished, close all connections:

```python
db.close()
```

---

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

---

## License

This project is licensed under the MIT License.
```