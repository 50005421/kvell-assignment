import time

import requests
import streamlit as st


BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Agent Chat", layout="wide")

if "history" not in st.session_state:
    st.session_state["history"] = []

if "last_steps" not in st.session_state:
    st.session_state["last_steps"] = []

with st.sidebar:
    st.header("Session controls")
    if st.button("Clear conversation"):
        st.session_state["history"] = []
        st.session_state["last_steps"] = []
        st.experimental_rerun()

col_chat, col_steps = st.columns([2, 1])

with col_chat:
    st.subheader("Conversation")

    # Show existing history
    for msg in st.session_state["history"]:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Assistant:** {content}")

    user_input = st.text_input(
        "Your message",
        key="user_input",
        placeholder="Ask something for the agents to work on...",
    )

    send_clicked = st.button("Send")

    if send_clicked and user_input.strip():
        st.session_state["history"].append({"role": "user", "content": user_input})

        answer_placeholder = st.empty()
        status_placeholder = st.empty()

        try:
            payload = {
                "query": user_input,
                "history": st.session_state["history"],
            }

            api_response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)

            if api_response.status_code != 200:
                raise RuntimeError(
                    f"Backend error {api_response.status_code}: {api_response.text}"
                )

            data = api_response.json()
            full_text = data.get("response", "") or ""
            streamed = ""

            for token in full_text.split():
                streamed += token + " "
                answer_placeholder.markdown(f"**Assistant (streaming):** {streamed}")
                status_placeholder.markdown("_Generating answer..._")
                time.sleep(0.03)
            final_answer = full_text.strip() or "(no answer returned)"
            status_placeholder.markdown("\n")
            answer_placeholder.markdown(f"**Assistant:** {final_answer}")

            st.session_state["history"].append({"role": "assistant", "content": final_answer})

            st.session_state["last_steps"] = data.get("steps", [])

        except Exception as e:
            st.error(f"Error while calling chat endpoint API: {e}")


# --- Steps / agents column ---
with col_steps:
    st.subheader("Agent steps, tools & valuation")

    steps = st.session_state.get("last_steps", [])

    if not steps:
        st.info("Send a message to see the agent chain, tools, and validator/valuation step.")
    else:
        steps_container = st.container()
        valuation_found = False

        for idx, step in enumerate(steps, start=1):
            s_type = step.get("type", "")
            s_name = step.get("name") or "Agent"
            s_content = step.get("content", "")

            if s_name == "Validator_Agent" or s_type == "final_answer":
                valuation_found = True
                label = f"Step {idx} · {s_name}"
            else:
                label = f"Step {idx} · {s_name}"

            with steps_container:
                st.markdown(f"**{label}**  \n`{s_type}`  \n{s_content}")
                st.markdown("---")
