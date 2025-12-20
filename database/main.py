"""
*
*   Handling of the WebApp internal SQLite Database.
*
"""
import os, sqlite3

# Global Variables
CONNECTION = None


def get_tables() -> list:
    """
    Check for the tables present in the SQLite instance

    Returns:
        list : The tables in the SQLite instance.
    """
    global CONNECTION

    cursor = CONNECTION.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    tables = cursor.fetchall()    

    return tables


def create_tables( tables : dict ) -> bool:
    """
    Creates new tables according to the queries given in `tables` arg.
        
    Args:
        tables : dict - Dictionary where the key is the table name and the value is the CREATE query.
    
    Returns:
        bool : True upon success  
    """
    global CONNECTION
    
    cursor = CONNECTION.cursor()            
    
    try:
        for table_name in tables:
            
            # Check if table exists already.
            table_in_database_query  = query_database( f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ table_name }';" )
            table_in_database_result = len( table_in_database_query )
            if table_in_database_result == 1:
                print( "[SQLITE][+] Table exists: ", table_name )  
                continue
            
            # Create a new table
            cursor.execute( tables[table_name] )
            print( "[SQLITE][+] Table: ", table_name, "created" )           

        # Commit changes
        CONNECTION.commit()
        cursor.close()

    except Exception as e:
        print( "[SQLITE][!] Error when creating tables,", e )
        return False
    
    return True


def query_database( query:str, user_input:tuple = None ) -> list:
    """
    Run specified query in the Database.

    Args:
        query      : str   - Query to be ran.
        user_input : tuple - User input, if necessary

    Returns:
        list : the results of the query.
    """
    
    global CONNECTION
    
    rows   : list = []
    cursor        = CONNECTION.cursor()
    
    try:
        
        # No user input, just a query
        if not user_input:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
    
        # If user input is given, use it in query
        cursor.execute(query, user_input)
        rows = cursor.fetchall()
        return rows
    
    except Exception as e:
        print( f"[SQLITE][!] Ran into an issue while running execute({ query }). Details: ", e )
        return []
    

def insert_data( query:str, data ) -> int:
    """
    Insert data into a table using premade queries.

    Args:
        query : str        - The insert query for the data
        data  : tuple,list - The data being inserted. Either in format tuple or list.

    Returns:
        bool : True upon success
    """
    global CONNECTION

    row_id = -1
    cursor = CONNECTION.cursor()

    try:
       # If data is of type tuple, use execute
        if type(data) == tuple:
            cursor.execute( query, data )
            CONNECTION.commit()
        
        # If data is of type list, use executemany
        if type(data) == list:
            cursor.executemany( query, data )
            CONNECTION.commit()

        return cursor.lastrowid

    except Exception as e:
        CONNECTION.rollback()
        print( f"[SQLITE][!] Ran into an issue while running execute({ query }), with data {data}, details: ", e )
        return row_id
    
    return row_id


def update_data( query:str, data ) -> tuple:
    """
    Update data in a table using premade queries.

    Args:
        query : str   - The insert query for the data
        data  : tuple - The data being inserted. 

    Returns:
        bool : Upon success
    """
    
    global CONNECTION
 
    cursor = CONNECTION.cursor()
    
    try:
        # If data is not of type tuple, skip interaction.
        if type(data) == tuple:
            cursor.execute( query, data )
            CONNECTION.commit()

    except Exception as e:
        CONNECTION.rollback()
        print( f"[SQLITE][!] Ran into an issue while running execute({ query }), with data {data}, details: ", e )
        return False

    print( f"[SQLITE][>] Rows updated: { cursor.rowcount }" )    
    return True


def initialize_db( tables, db_name : str = "data/database.db" ) -> bool:
    """
    Prepare the SQLite3 Database for use.

    Args:
        tables  : dict - Dictionary where the key is the table name and the value is the CREATE query. 
        db_name : str  - Name of the SQLite database file.

    Returns 
        bool : Boolean upon success.
    """
    
    global CONNECTION

    database_file_exists : bool = None
   
    print( "[SQLITE][>] Connecting to database...")
    try:        
        
        # Ensure the .db file is present. If not, create a new one.
        database_file_exists = os.path.exists( db_name )
        if not database_file_exists:
            with open(db_name, "w+") as file: file.write("")
            print("[SQLITE][>] Database file not found, created a new one.")
        
        # Connect to the database.
        CONNECTION = sqlite3.connect( db_name, check_same_thread=False )
        print( "[SQLITE][>] Connection to the database made" )
                
        # Create/Check for the presence of the tables.
        if not create_tables( tables ):
            return False
        
        print( "[SQLITE][>] Desired tables present." )

    except Exception as error:
        print(f"Error: {error}")
        return False

    print( "[SQLITE][*] Database ready!" )
    return True