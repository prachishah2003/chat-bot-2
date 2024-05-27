from PIL import Image
import io
import logging
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import re
import trialsearch as ts
import requests

temperature = 0.9
import streamlit as st

# Power tools
power_tools = [
    {"name":"Bosch Tools","link": "https://www.ibo.com/power-tools/c/3050"},
    {"name": "DeWalt 20V MAX Cordless Drill / Driver Kit", "link": "https://www.amazon.com/DEWALT-DCD771C2-20V-Lithium-Ion-Cordless/dp/B00ET5VMTU"},
    {"name": "Makita XAG04Z 18V LXT Cordless Cut-Off/Angle Grinder", "link": "https://www.homedepot.com/p/Makita-18-Volt-LXT-Lithium-Ion-Brushless-Cordless-4-1-2-in-5-in-Cut-Off-Angle-Grinder-Tool-Only-XAG04Z/205447392"},
    {"name": "Bosch ROS20VSC Palm Sander", "link": "https://www.lowes.com/pd/Bosch-2-5-Amp-Corded-5-in-Random-Orbit-Sander-with-Case/999925164"},
    {"name": "Milwaukee 2767-20 M18 Fuel High Torque 1/2\" Impact Wrench", "link": "https://www.amazon.com/Milwaukee-2767-20-Fuel-Torque-Wrench/dp/B0753Z5RHN"},
    {"name": "Black+Decker 20V MAX Cordless Reciprocating Saw", "link": "https://www.walmart.com/ip/BLACK-DECKER-20V-MAX-Cordless-Reciprocating-Saw-BDCR20C/34354758"}
]

# Hand tools
hand_tools = [
    {"name": "Stanley 16-791 Sweetheart 750 Series Socket Chisel Set", "link": "https://www.amazon.com/Stanley-16-791-Sweetheart-4-Piece-750/dp/B0030T1BR6"},
    {"name": "Klein Tools 80020 Tool Set", "link": "https://www.homedepot.com/p/Klein-Tools-8-Piece-Electrician-s-Tool-Set-80020/305054940"},
    {"name": "Irwin Vise-Grip Original Locking Pliers Set", "link": "https://www.lowes.com/pd/IRWIN-VISE-GRIP-3-Piece-Locking-Pliers-Set/1000264293"},
    {"name": "TEKTON Combination Wrench Set", "link": "https://www.amazon.com/TEKTON-Combination-Wrench-12-Inch-15-Piece/dp/B009QYF3QA"},
    {"name": "Estwing E3-16S 16 oz Straight Rip Claw Hammer", "link": "https://www.homedepot.com/p/Estwing-16-oz-Straight-Claw-Rip-Hammer-E3-16S/100351741"}
]


generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 99998,
}

st.set_page_config(page_title="Gemini Chatbot", page_icon=":gem:")

with st.sidebar:
    st.title("Gemini Setting")

    api_key = 'AIzaSyC5Mmy23tELO2hAbz0f6HNe9Nkd9KsMRyE'
    if api_key:
        genai.configure(api_key=api_key)
    else:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        else:
            st.error("Missing API key.")
    select_model = st.selectbox(
        "Select model", ["powertools__new_final111"])
    temperature = 0.9

    if select_model == "gemini-pro-vision":
        uploaded_image = st.file_uploader(
            "upload image",
            label_visibility="collapsed",
            accept_multiple_files=False,
            type=["png", "jpg"],
        )
        st.caption(
            "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
        )
        if uploaded_image:
            image_bytes = uploaded_image.read()


def get_response(messages, model="gemini-pro"):
    model = genai.GenerativeModel(model)
    res = model.generate_content(messages,
                                 generation_config=generation_config)
    return res


if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages = st.session_state["messages"]

# The vision model gemini-pro-vision is not optimized for multi-turn chat.
st.header("TINKER.BOT")
st.write("This is a Gemini LLM Chatbot for suggesting tools and providing steps to fix anything we want. This app is powered by Google's GEMINI Generative AI models. This app is built using Streamlit and hosted on Streamlit Share.")
st.markdown("""
    App built by ENTC-C Batch-3 Group 5
""")

# Initialize session state for chat history if it doesn't exist
if messages and select_model != "gemini-pro-vision":
    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "model":
            st.chat_message("assistant").markdown(parts[0])

chat_message = st.chat_input("Say something")

res = None
if chat_message:
    st.chat_message("user").markdown(chat_message)
    res_area = st.chat_message("assistant").markdown("...")

    if select_model == "gemini-pro-vision":
        if "image_bytes" in globals():
            vision_message = [chat_message,
                              Image.open(io.BytesIO(image_bytes))]
            try:
                res = get_response(vision_message, model="gemini-pro-vision")
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
        else:
            vision_message = [{"role": "user", "parts": [chat_message]}]
            st.warning(
                "Since there is no uploaded image, the result is generated by the default gemini-pro model.")
            try:
                res = get_response(vision_message)
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
    else:
        messages.append(
            {"role": "user", "parts":  [chat_message]},
        )
        try:
            res = get_response(messages)
        except google_exceptions.InvalidArgument as e:
            if "API key not valid" in str(e):
                st.error("API key not valid. Please pass a valid API key.")
            else:
                st.error("An error occurred. Please refresh your page and try again.")
        except Exception as e:
            logging.error(e)
            st.error("Error occured. Please refresh your page and try again.")
    
    if res is not None:
        res_text = ""
        for chunk in res:
            if chunk.candidates:
                res_text += chunk.text
            if res_text == "":
                res_text = "unappropriate words"
                st.error("Your words violate the rules that have been set. Please try again!")
        res_area.markdown(res_text)

        st.header("Power Tools")
        for tool in power_tools:
            st.write(f"[{tool['name']}]({tool['link']})")
        
        st.header("Hand Tools")
        for tool in hand_tools:
            st.write(f"[{tool['name']}]({tool['link']})")

    
        if select_model != "gemini-pro-vision":
            messages.append({"role": "model", "parts": [res_text]})
