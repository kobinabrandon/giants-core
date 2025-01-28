import time
import streamlit as st

from src.generation.main import PrimaryGenerator 


def invite_first_query(
    invite_message: str ="Feel free to ask your first question. I hope we can have an engaging conversation about Dr Nkrumah:)" 
):

    st.title("Chat")

    with st.chat_message(name="Assistant"):
        st.write(invite_message)


    prompt = st.chat_input(placeholder="Your question") 


# def get_response(question: str):
   # PrimaryGenerator(question=question, ) 
