import db

def create_user_token(user_id, **kwargs):
    user_token_id = db.insert("INSERT INTO user_tokens (user_id, token) VALUES(%s, UUID())", [user_id])

    for field_name in kwargs:
        db.update("UPDATE user_tokens SET " + field_name + " = %s WHERE id = %s", [kwargs[field_name], user_token_id])

    return db.fetchrow("SELECT * FROM user_tokens WHERE id = %s", [user_token_id])