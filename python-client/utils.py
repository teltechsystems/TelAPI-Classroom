import random

def generate_code(code_length = 4):
    assert isinstance(code_length, int)
    
    random_chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    return ''.join([random_chars[random.randint(0, len(random_chars) - 1)] for x in range(code_length)])