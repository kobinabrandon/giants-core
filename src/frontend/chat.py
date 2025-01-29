import streamlit as st
from openai import OpenAI

from src.generation.main import PrimaryGenerator 
from src.setup.config import frontend_config, env_config, llm_config 


st.title("Chat")


endpoint_url: str = llm_config.endpoints_under_consideration[llm_config.preferred_model] 
client = OpenAI(base_url=endpoint_url, api_key=env_config.hugging_face_token)

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display messages from chat history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if (prompt := st.chat_input(placeholder="Your question")):

    # Add the user's message to the chat history
    st.session_state.messages.append(
        {"role": "user", "context": prompt}
    )

    # Write the user's input into a chat message container 
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message(name=frontend_config.bot_name):
        stream = client.chat.completions.create(
            model="tgi",
            top_p=0,
            temperature=0,
            max_tokens=2000,
            stream=True,
            messages=[
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ],
        )



# def response_generator()
#
# generator = PrimaryGenerator(question=question) 
#
# with st.chat_message(name=frontend_config.bot_name, avatar="🤖"): 
#     response = st.write_stream(generator.query_llm(to_frontend=True))
#
# st.session_state.messages.append(
#     {"role": "assistant", "content": response}
# )
#

