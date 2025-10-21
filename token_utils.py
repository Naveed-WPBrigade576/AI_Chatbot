from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "your-secret-key"  # Store in .env
s = URLSafeTimedSerializer(SECRET_KEY)

def generate_token(email):
    return s.dumps(email, salt="email-login")

def verify_token(token, max_age=600):
    try:
        email = s.loads(token, salt="email-login", max_age=max_age)
        return email
    except Exception:
        return None
