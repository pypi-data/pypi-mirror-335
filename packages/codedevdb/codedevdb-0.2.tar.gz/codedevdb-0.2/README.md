# codedevdb Library

![PyPI - Version](https://img.shields.io/pypi/v/CodeDevDB?color=blue&label=version) ![PyPI - Downloads](https://img.shields.io/pypi/dm/codedevdb?color=green&label=downloads)
![PyPI - License](https://img.shields.io/pypi/l/CodeDevDB?color=blue)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/CodeDevDB?color=blue)


**codedevdb** is a powerful and easy-to-use Python library for managing SQLite databases. It provides a clean and intuitive interface for database operations, including connection management, query execution, table creation, data insertion, updating, deletion, and more. The library is designed to simplify database interactions while maintaining flexibility and efficiency.

---

## 🚀 Features
- ✅ **Simple SQLite Database Management**: Easily connect to and manage SQLite databases.
- ✅ **Context Manager for Connection Handling**: Automatically handles database connections and transactions.
- ✅ **CRUD Operations**: Create, Read, Update, and Delete data with simple methods.
- ✅ **Table Management**: Create, modify, and drop tables with ease.
- ✅ **Bulk Insertion**: Insert multiple records in a single operation.
- ✅ **Index Creation**: Improve query performance with custom indexes.
- ✅ **Backup and Restore**: Backup and restore your database with a single method.
- ✅ **Schema Inspection**: Retrieve table schema information.
- ✅ **Error Handling**: Robust error handling with rollback support.

---

## 📦 Installation
You can install **codedevdb** via `pip`:

```bash
pip install codedevdb
```

---

## 🔥 Usage

### Importing the Library
```python
import codedevdb
```

### Connecting to a Database
```python
# Connect to a SQLite database (or create it if it doesn't exist)
db = codedevdb('mydatabase.db')
```

### Creating a Table
```python
# Create a table with columns
db.create('users', id='INTEGER PRIMARY KEY', name='TEXT NOT NULL', age='INTEGER')
```

### Inserting Data
```python
# Insert a single record
db.insert('users', name='John', age=30)

# Insert multiple records
data = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob', 'age': 28}
]
db.insert_bulk('users', data)
```

### Fetching Data
```python
# Fetch all records from the table
result = db.select('users')
print(result)

# Fetch specific columns with a condition
result = db.select('users', where="age > 25", columns=['name', 'age'])
print(result)
```

### Updating Data
```python
# Update records
db.update('users', where="name = 'John'", age=31)
```

### Deleting Data
```python
# Delete records
db.delete('users', where="name = 'John'")
```

### Counting Records
```python
# Count records
count = db.count('users', where="age > 25")
print(f"Number of users above 25: {count}")
```

### Checking if Records Exist
```python
# Check if a record exists
exists = db.exists('users', where="name = 'Alice'")
print(f"Does Alice exist? {exists}")
```

### Dropping a Table
```python
# Drop a table
db.drop_table('users')
```

### Truncating a Table
```python
# Truncate a table (delete all records)
db.truncate('users')
```

### Inspecting Table Schema
```python
# Get table schema
schema = db.schema('users')
print(schema)
```

### Creating an Index
```python
# Create an index on a column
db.create_index('users', 'idx_name', ['name'])
```

### Backup and Restore
```python
# Backup the database
db.backup('backup.db')

# Restore the database
db.restore('backup.db')
```

---

## 🌍 Compatibility
- **Python**: 3.8+
- **Databases**: SQLite3

---

## 🎯 Contribution
We welcome contributions! If you'd like to contribute to **CodeDevDB**, please open an issue or submit a pull request on GitHub.

---

## 📄 License
**CodeDevDB** is released under the MIT License.

---

## 📞 Contact
For any questions or support, feel free to reach out:
- **Telegram Account**: [@midoghanam](https://t.me/midoghanam)
- **Telegram Channel**: [@mido_ghanam](https://t.me/mido_ghanam)

---

## Best Regards ♡
Thank you for using **CodeDevDB**! We hope it simplifies your database management tasks and makes your development process smoother. If you have any feedback or suggestions, please don't hesitate to reach out. Happy coding! 🚀