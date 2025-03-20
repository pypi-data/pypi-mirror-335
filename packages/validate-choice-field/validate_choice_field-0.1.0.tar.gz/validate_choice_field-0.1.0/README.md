# validate_choice_field

## 📌 Introduction
`validate_choice_field` package provides a simple and efficient way to validate user-submitted data against predefined choices in a Django model choice field. It ensures that the posted data matches one of the available choices and returns the corresponding value required for database storage. If no match is found, it returns **None**.

### How It Works

Django’s **choices** field consists of two parts:

* **Value (Stored in Database)** – The actual data saved in the database.
* **Display Label** – The human-readable version shown in forms and admin panels.

For example, in a Django model:
```python

# Define choices
DURATION_TYPE_CHOICE = ( 
    ("Hour", "1 Hour"), 
    ("Day", "1 Day"),
)

class Event(models.Model):
    duration = models.CharField(max_length=250, choices=DURATION_TYPE_CHOICE)
```
In this case, **"Hour"** is stored in the database, while **"1 Hour"** is displayed to users.

#### how to use

```sh
pip install validate_choice_function
```

```python
from validate_choice_function import get_choice

print("If choice matches",get_choice(DURATION_TYPE_CHOICE,"1 Hour"))
# Output: "Hour"

print("If choice does not matches",get_choice(DURATION_TYPE_CHOICE,"Hour dcd"))
# Output: None

```

This function accepts two parameters:

* **choices**: A list of tuples representing the available choices, where each tuple consists of a database value and its corresponding display value.

* **posted_value**: The value submitted by the user, which needs to be validated.

The function compares the **posted_value** against the choices. If a match is found, it returns the corresponding database value. If no match is found, it returns **None**.

### Purpose of This Package

When handling API requests, it is crucial to validate input values before saving them to the database. This package ensures that:

- The submitted value exists in the predefined choices.
- If a match is found, it returns the corresponding value for storage.
- If no match is found, it returns **None**, preventing invalid data from being saved.

### Benefits

* **Simplifies choice validation** – Reduces manual validation logic.
* **Enhances data integrity** – Ensures only valid choices are stored.
* **Improves code maintainability** – Provides a reusable and structured approach for handling choice fields in Django applications.



## 🚀 Installation
Install the package via pip:

```sh
pip install my_package
