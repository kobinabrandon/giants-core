import streamlit as st


def invite_first_query():

    with st.chat_message(name="Assistant"):
        invite_message = """Hi there. I'm glad that you'd like to learn about Kwame Nkrumah. Feel free to ask your first question. 
                        I hope we can have an engaging conversation :)"""

        st.write(invite_message)
