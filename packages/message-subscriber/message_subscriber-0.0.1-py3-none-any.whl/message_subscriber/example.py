import streamlit as st
from message_subscriber import message_subscriber

st.title("Message Subscriber")


if "connected" not in st.session_state:
    st.session_state.connected = False

if "closed" not in st.session_state:
    st.session_state.closed = False


if not st.session_state.connected and not st.session_state.closed:
    print("connecting")
    message = message_subscriber(url="ws://localhost:8000/ws/user002")
    st.session_state.connected = True

    if message:
        st.write(message)
else:
    print("closing")

if st.button("close"):
    st.session_state.closed = True
    st.rerun()

