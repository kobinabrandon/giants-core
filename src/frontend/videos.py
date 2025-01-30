import streamlit as st
from streamlit_extras.colored_header import colored_header 

from src.setup.config import videos


colored_header(
    label="More Information about Nkrumah",
    description="Selected high quality resources for users who'd like to learn more"
)


def post_links_to_documentaries():

    _ = st.header(":red[Docu]:orange[ment]:green[aries]")

    col1, col2 = st.columns(2)

    for video in videos.__dict__.values():
        st.video(data=video)
