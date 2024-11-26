# **TRIPLAN**

This repository contains all the information necessary to implement the database with a REST API. Please refer to the **DATABASE CREATION** and the **REST API** sections to know more.

## **DATABASE CREATION**

The files in this folder are used to generate and fill the database for our ***TRIPLAN*** travel agency. Please, read the whole document to know how to properly use these files.

### **REQUIREMENTS**
To create and fill the database you need to have **Python** installed on your PC.

Additionally, the following libraries are needed:
- `pandas`, to manage dataframes;
- `numpy`, to manage date types;
- `mysql`, to connect to the mysql server.

You can install them by running the following command on your command prompt:
```
pip install pandas numpy mysql-connector-python
```

### **HOW TO USE**
To properly generate and fill the database, please follow these steps:

1. Edit the `generate_db.py` file to include the correct parameters according to your PC:
    - Update the `mysql_password` field with the password for your mysql server.
    - Update the variables `sql_file_path` and `excel_file_path` to reflect the path of the SQL and Excel files. If you keep those files inside the same folder as the `generate_db.py` you do not need to edit the default values.

2. Run the `generate_db.py` script. There are multiple ways to do it:
    - Double clicking the file inside the files explorer.
    - Through the command window. In this case, make sure that your current working path is the same as the one for the scrip.

3. After running the script, press Enter to exit the command prompt window. You can then check that your new database has been generated:
    - Enter into your mysql server, and introduce your password.
    ```
    mysql -u root -p
    ```
    - Show all the databases.
    ```
    SHOW DATABASES;
    ```
    - Select the `DB_TRIPLAN` database.
    ```
    USE DB_TRIPLAN;
    ```
    - Show all the tables in the database.
    ```
    SHOW TABLES;
    ```
From now on, you can add, delete, update, search, etc any row in your database.

## **REST API**
To run the Rest API, simply run the file `app.py` after having created the database. Then, you can visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to interact with the system.