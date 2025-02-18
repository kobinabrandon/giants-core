import streamlit as st
from openai import OpenAI
from loguru import logger

from src.generation.main import PrimaryGenerator 
from src.generation.memory import EmbeddingBased
from src.setup.config import frontend_config, env_config, hf_config 


st.title("Chat")


endpoint_url: str = hf_config.endpoints_under_consideration[hf_config.preferred_model] 
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

    memory = EmbeddingBased(vector_db_name="chroma")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [] 
        
    # # Add the user's message to the chat history
    # st.session_state.messages.append(
    #     {"role": "user", "content": prompt}
    # )

    # Write the user's input into a chat message container 
    with st.chat_message("user"):
        st.markdown(prompt)

    # st.session_state["chat_history"].append(
    #     {
    #         "role": "user", "content": st.session_state["chat_input"]
    #     }
    # )
    #

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
        
    generator = PrimaryGenerator(question=prompt) 


    if "chat_history" in st.session_state:
        with st.chat_message(name=frontend_config.bot_name, avatar="🤖"): 
            with st.spinner("Thinking..."):
                response = st.write_stream(generator.query_llm(to_frontend=True))

                st.session_state["chat_history"].append(
                    {"role": frontend_config.bot_name, "content": response}
                )


    # else:

        memory.store_interaction(user_message=prompt, bot_response=response) 


