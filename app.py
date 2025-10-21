import streamlit as st
from auth import check_login
from memory import save_message, load_messages
import importlib
import graph as chat_graph_module
from langchain_core.messages import SystemMessage, HumanMessage
import uuid 
from memory import list_sessions 
from token_utils import generate_token, verify_token
from memory import save_user, get_user_by_email
from utils import is_valid_email
from email_utils import send_login_email

st.set_page_config(page_title="LangGraph Chatbot", layout="centered")
# Login

query_params = st.query_params
token = query_params.get("token", None)

# Handle magic link
if token:
    email = verify_token(token)
    if email:
        user = get_user_by_email(email)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.username
            st.session_state.email = email
            st.query_params.clear()
            st.rerun()
        else:
            st.error("User not found.")
    else:
        st.error("Invalid or expired token.")

# Show login form if not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.title("🔐 Email Login")
    username = st.text_input("Username")
    email = st.text_input("Email")

    if st.button("Send Magic Link"):
        if not is_valid_email(email):
            st.error("Invalid email format.")
        else:
            save_user(username, email)
            token = generate_token(email)
            try:
                send_login_email(email, token)
                st.success("Check your email for the login link!")
            except Exception as e:
                st.error("Failed to send email. Please verify SMTP settings and app password.")
                st.exception(e)
    st.stop()


# Chat page
st.title("💬 LangGraph Chatbot")



st.sidebar.header("💬 Chat Sessions")

# Create or select a session
if "session_id" not in st.session_state:
    st.session_state.session_id = None

sessions = list_sessions(st.session_state.username)

selected_session = st.sidebar.selectbox("Select a session", sessions + ["➕ Start new chat"])

# Handle new session
if selected_session == "➕ Start new chat":
    new_id = str(uuid.uuid4())[:8]  # short session ID
    st.session_state.session_id = new_id
    st.session_state.chat_state = {"messages": []}
else:
    st.session_state.session_id = selected_session


with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        from memory import clear_messages
        clear_messages(st.session_state.username)  # Delete from DB
        st.session_state.chat_state = {"messages": []}  # Clear in-memory
        st.rerun()


# Ensure we use the latest graph definition (handles Streamlit's module caching)
importlib.reload(chat_graph_module)
chat_graph = chat_graph_module.create_chat_graph()

# Load history
if "chat_state" not in st.session_state:
    st.session_state.chat_state = {"messages": []}
    previous = load_messages(st.session_state.username, st.session_state.session_id)

    for msg in previous:
        role = msg.role
        if role == "user":
            st.session_state.chat_state["messages"].append(HumanMessage(content=msg.content))
        else:
            st.session_state.chat_state["messages"].append(SystemMessage(content=msg.content))

# Show messages
for m in st.session_state.chat_state["messages"]:
    role = "You" if isinstance(m, HumanMessage) else "Bot"
    st.chat_message(role).write(m.content)

# Handle new input
if prompt := st.chat_input("Type a message..."):
    st.chat_message("You").write(prompt)
    st.session_state.chat_state["messages"].append(HumanMessage(content=prompt))
    save_message(st.session_state.username, st.session_state.session_id, "user", prompt)



    result = chat_graph.invoke(st.session_state.chat_state)
    reply_msg = result["messages"][-1].content

    st.chat_message("Bot").write(reply_msg)
    st.session_state.chat_state = result
    save_message(st.session_state.username, st.session_state.session_id, "bot", reply_msg)




