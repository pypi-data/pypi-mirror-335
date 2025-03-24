import streamlit.components.v1 as components
import os
import streamlit as st
import json

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "message_subscriber",
        url="http://localhost:3000"
    )
else:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.join(parent_dir, "message_subscriber/frontend/build")

    _component_func = components.declare_component(
        "message_subscriber",
        path=build_dir
    )


def message_subscriber(url: str, connection_timeout: int = 1000, max_retries: int = 100, key: str = None):
    """
    Create a WebSocket message subscriber that processes each unique message exactly once.
    Only tracks the last processed message ID.
    
    Args:
        url: The WebSocket URL to connect to
        key: An optional key for the component
        
    Returns:
        The WebSocket message if it hasn't been processed before, None if it has been processed
        or if there's no message
    """
    # # Create a unique key for this component instance
    # component_key = f"message_subscriber_{key if key else url}"
    # last_message_id_key = f"{component_key}_last_id"
    
    # Get message from WebSocket
    message_data = _component_func(url=url, connection_timeout=connection_timeout, max_retries=max_retries, key=key, default=None)

    return message_data
    
    # if message_data is not None:
    #     try:
    #         # Parse the message to get its ID
    #         message = json.loads(message_data)
    #         message_id = message.get('id')
            
    #         # If this is a new message (different ID from last processed)
    #         if message_id != st.session_state.get(last_message_id_key):
    #             # Update the last processed message ID
    #             st.session_state[last_message_id_key] = message_id
    #             return message_data
    #     except json.JSONDecodeError:
    #         # If message is not JSON, use the raw message as ID
    #         if message_data != st.session_state.get(last_message_id_key):
    #             st.session_state[last_message_id_key] = message_data
    #             return message_data
    
    # return None
