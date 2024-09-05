import pyodbc

def get_connection():
    # ['SQL Server', 'SQL Server Native Client 11.0', 'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server']
    
    server = "AFONSOCR"
    database = "DETShop"
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no;'

    conn = pyodbc.connect(connectionString)

    return conn