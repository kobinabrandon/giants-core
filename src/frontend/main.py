import streamlit as st
from streamlit import Page 
# from streamlit_extras.app_logo import add_logo 


pages = st.navigation(
    expanded=True,
    pages=[
        Page(page="intro.py", title="Who was Kwame Nkrumah?", icon="🇬🇭"),
        Page(page="books.py", title="His Written Works", icon="📚"),
        Page(page="chat.py", title="Ask", icon="🤖"),
        Page(page="videos.py", title="Learn More", icon="🤖")
    ]
)

pages.run()


