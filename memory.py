from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    session_id = Column(String)  # new
    role = Column(String)
    content = Column(Text)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)



engine = create_engine("sqlite:///chat.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def save_message(username, session_id, role, content):
    session = Session()
    msg = Message(username=username, session_id=session_id, role=role, content=content)
    session.add(msg)
    session.commit()

def load_messages(username, session_id):
    session = Session()
    return session.query(Message).filter_by(username=username, session_id=session_id).all()


def clear_messages(username):
    session = Session()
    session.query(Message).filter_by(username=username).delete()
    session.commit()

def list_sessions(username):
    session = Session()
    results = session.query(Message.session_id).filter_by(username=username).distinct().all()
    return [r[0] for r in results]

def get_user_by_email(email):
    session = Session()
    return session.query(User).filter_by(email=email).first()

def get_user_by_username(username):
    session = Session()
    return session.query(User).filter_by(username=username).first()

def save_user(username, email):
    session = Session()
    # Try to find by email or username and update to avoid UNIQUE errors
    user = get_user_by_email(email)
    if user:
        # Update username if changed
        if user.username != username:
            user.username = username
            session.commit()
        return
    user = get_user_by_username(username)
    if user:
        # Update email if changed
        if user.email != email:
            user.email = email
            session.commit()
        return
    # Create new record if neither exists
    user = User(username=username, email=email)
    session.add(user)
    session.commit()


