from PIL import Image
import io
import logging
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions


# Define the Bosch tool names and buy links
tool_info = [
    {"name": "Bosch GSB 500W 500 RE Tool Set And Masonry Drill Bit Set Combo", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
    {"name": "Bosch Hand Tool Kit (Blue, 12 Pieces) And Bosch 66041612 Screwdriver Bits Set", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
    {"name": "BOSCH 46 Piece Screwdriver Set Hand Tool Kit", "link": "https://www.flipkart.com/bosch-46-piece-screwdriver-set-hand-tool-kit/p/itmfb8445yx2dspa"},
    {"name": "Bosch GSB 500W 500 RE Corded-Electric Drill Tool Set + Bosch GO 2 Professional Kit", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
    {"name": "Bosch 40 Piece X-Line Titanium Set Hand Tool Kit", "link": "https://www.flipkart.com/bosch-40-piece-x-line-titanium-set-hand-tool-kit/p/itmf3x6zgqzjxhjg"},
    {"name": "Bosch GSB 180-LI 18V Cordless Impact Drill & Bosch Hand Tool Kit (Blue, 12 Pieces) & Bosch 2608590090 Masonry Drill Bit Set (5-Pieces)", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
    {"name": "Bosch 2608587521 65 mm PH2 Screwdriver Bit Set", "link": "https://www.industrybuying.com/screwdriver-bits-bosch-HA.SC.SC04.524981/"},
    {"name": "Bosch Professional 12-In-1 Multitool Set, Pack Of 1", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
    {"name": "BOSCH 2608603412 4 Inch Metal Cutting Wheel 10Pc Set Metal Cutter", "link": "https://www.flipkart.com/bosch-2608603412-4-inch-metal-cutting-wheel-10pc-set-metal-cutter/p/itmfb8445yx2dspa"},
    {"name": "Bosch 2607017063 Screwdriver Bit Set (Grey, 32-Pieces)", "link": "https://www.amazon.in/dp/B07Q2YVZ8L"},
]


temperature = 0.9

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
        "Select model", ["gemini-pro", "gemini-pro-vision","powertools__new_final111"])
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
        # Display the tool names and links
        st.title("Bosch Tool Sets")
        for tool in tool_info:
            st.write(f"**{tool['name']}**: Buy here")
        if select_model != "gemini-pro-vision":
            messages.append({"role": "model", "parts": [res_text]})
