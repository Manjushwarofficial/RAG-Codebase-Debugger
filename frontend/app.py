import streamlit as st
import requests

API_URL = "http://13.60.217.117:8000/query"

st.title("RAG Codebase Debugger")
st.write("Ask questions about the codebase and get answers based on the context of the code.")
st.markdown("Codebase Link : [Click here](https://github.com/vaibhav-yerkar/Wolfenstein3D_Clone)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about the code base."):
    st.session_state.messages.append({"role": "human", "content": prompt})
    with st.chat_message("human"):
        st.markdown(prompt)

    with st.chat_message("ai"):
        with st.spinner("Fanthoming..."):
            try:
                response = requests.post(API_URL, json={"query": prompt}, timeout=120)
                response.raise_for_status()
                data = response.json()
                if "answer" in data:
                    ans = data["answer"]
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "ai", "content": ans})
                else:
                    st.error(f"Backend error: {data.get('error', 'Unknown error')}")        
            except requests.exceptions.Timeout:
                st.error("The backend took too long to respond (timed out after 60s).")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is it running on port 8000?")
            except requests.exceptions.RequestException as e:
                st.error(f"Request error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")