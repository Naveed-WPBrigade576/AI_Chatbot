USERS = {
    "admin": "password123",
    "user1": "letmein"
}

def check_login(username, password):
    return USERS.get(username) == password
