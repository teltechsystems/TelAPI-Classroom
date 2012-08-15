import MySQLdb
import settings
import utils

def get_connection():
    return MySQLdb.connect(**settings.DATABASE)

def insert(query, data):
    connection = get_connection()

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, data)

    insert_id = connection.insert_id()

    cursor.close()
    connection.commit()

    return insert_id

def fetchrow(query, data):
    connection = get_connection()

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, data)

    result = cursor.fetchone()

    cursor.close()

    return result

def fetchall(query, data):
    connection = get_connection()

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, data)

    result = cursor.fetchall()

    cursor.close()

    return result

def update(query, data):
    connection = get_connection()

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, data)
    cursor.close()

    connection.commit()

    return True

def get_classroom_user_code(classroom_id, user_id, short_code = None):
    if short_code is None:
        short_code = utils.generate_code()
        
    classroom_user_code_id = insert("INSERT INTO classroom_user_code (classroom_id, user_id, short_code, update_time) VALUES(%s, %s, %s, NOW()) ON DUPLICATE KEY UPDATE update_time = NOW()", [classroom_id, user_id, short_code])
    
    return fetchrow("SELECT classroom_id, user_id, short_code, update_time FROM classroom_user_code WHERE id = %s", classroom_user_code_id)