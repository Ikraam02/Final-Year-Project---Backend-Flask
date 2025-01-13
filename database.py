import pypyodbc as odbc 

# Use the correct ODBC driver name
DRIVER_NAME = 'SQL Server'  # Example, replace with your actual driver name
SERVER_NAME = 'DESKTOP-G4A2LDV'
DATABASE_NAME = 'sale_1'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

try:
    # Attempt to establish a connection
    conn = odbc.connect(connection_string)
    if conn:
        print("Connection successful!")
        
    else:
        print("Failed to connect to the database.")

except odbc.Error as e:
    print("Error:", e)
