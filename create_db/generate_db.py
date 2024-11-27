"""
FILL AND GENERATE DATABASE

GROUP 5
AUTHORS: Jaime Jarauta, Jesús Vidal, Gabriela del Pino, Miguel Álvarez
DATE: November 2024

DESCRIPTION: 
This script generates and fills the database that we will use for our travel agency project.

HOW TO USE IT:
To run it, first modify the USER CONFIGURABLE PARAMETERS:
- Make sure to update the password for your mysql server
- If the SQL file for the creation of the database, and the Excel file with all the values
    is in a different folder, please update their paths.
"""
import pandas as pd
import numpy as np
import mysql.connector

####################################
### USER CONFIGURABLE PARAMETERS ###
####################################

mysql_password = "1075"             # The password to your mysql server
sql_file_path = 'create_db/triplan.sql'       # Path to the SQL file that will create the DATABASE and TABLES
excel_file_path = 'create_db/triplan.xlsx'    # Path to the Excel file with all the VALUES that will be used to fill the database


####################################
###         MAIN SCRIPT          ###
####################################

# Configuration for MySQL database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": mysql_password,
    "database": "DB_TRIPLAN"
}

# Connect to MySQL
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    ###################################################################################
    ##### FIRST, CREATE THE DATABASE FROM SCRATCH, BASED ON THE SQL CREATION FILE #####
    ###################################################################################

    # Read the SQL file
    with open(sql_file_path, 'r') as file:
        sql_commands = file.read()

    # Split the commands by semicolon (;) to handle multiple commands
    commands = sql_commands.split(';')

    # Execute each command
    for command in commands:
        command = command.strip()   # Remove any leading/trailing whitespace
        if command:                 # Skip empty commands
            cursor.execute(command)

    # Commit changes
    connection.commit()
    print("SQL script executed successfully.")


    ###################################################################################
    #####           INSERT ALL VALUES INTO THE DATABASE FROM THE EXCEL            #####
    ###################################################################################

    cursor.execute(f"USE {db_config['database']}")

    # Load Excel file
    excel_file = pd.ExcelFile(excel_file_path)

    # Iterate over sheets
    for sheet_name in excel_file.sheet_names:
        # Read the sheet into a DataFrame
        df = excel_file.parse(sheet_name)

        # Define table name (use sheet name)
        table_name = sheet_name.replace(" ", "_").lower()

        print("Sheet to insert:", table_name)

        # Insert data into the table
        for _, row in df.iterrows():
            row_data = []
            for col, value in row.items():
                # Extensive debugging for each column
                # print(f"Column: {col}")
                # print(f"Value: {value}")
                # print(f"Type: {type(value)}")
                # print(f"Is datetime64? {pd.api.types.is_datetime64_any_dtype(value)}")
                
                # Additional datetime checks
                if isinstance(value, pd.Timestamp):
                    # print("Value is pandas Timestamp")
                    # Convert to string in MySQL-friendly format
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, np.datetime64):
                    print("Value is numpy datetime64")
                    # Convert numpy datetime64 to string
                    value = pd.Timestamp(value).strftime('%Y-%m-%d %H:%M:%S')
                
                row_data.append(value)

            # print("Row data to insert:", row_data)

            # Prepare the column names and placeholders for SQL insertion
            columns = ", ".join([f"{col.replace(' ', '_').lower()}" for col in df.columns])
            values = ", ".join(["%s" for _ in df.columns])
            insert_query = f"INSERT IGNORE INTO {table_name} ({columns}) VALUES ({values})"
            cursor.execute(insert_query, tuple(row_data))

    # Commit changes
    connection.commit()
    print("Data successfully imported into MySQL database.")

except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()

input('Press Enter to continue...')