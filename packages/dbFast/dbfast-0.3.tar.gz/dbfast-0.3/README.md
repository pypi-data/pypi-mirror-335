# dbFast

**dbFast** is a simple library for working with SQLite databases with an easy-to-use syntax.

## Installation

You can install the library via pip:
```sh
pip install dbFast
```

## Usage

A basic example of working with `dbFast`:
```python
import dbFast

# Create a database connection and a "users" table
db = dbFast.db("sqlight:///db.db", "users", username=str, password=(str, "nullable=False"))

# Adding users
db.add(username="user_1", password="123dbFast!")
db.add(username="user_2", password="user_number_2!!")

# Deleting a user
db.delete(db.get_by_one(username="user_1"))

# Updating user data
db.update(db.get_by_one(username="user_2"), password="password_2")

# Retrieving all users
users = db.get_all()
for user in users:
    print(f"{user.username}: {user.password}")
```

## Main Methods

- `db.add(**kwargs)` – adds a record to the database.
- `db.get_by_one(**kwargs)` – retrieves a single record based on a condition.
- `db.get_all(**kwargs)` – retrieves all records matching a condition.
- `db.update(instance, **kwargs)` – updates data in an existing record.
- `db.delete(instance)` – deletes a record from the database.

## Features
- Simplified syntax.
- Uses SQLite as a storage solution.
- Lightweight and easy to work with.

## License
Free to use.
