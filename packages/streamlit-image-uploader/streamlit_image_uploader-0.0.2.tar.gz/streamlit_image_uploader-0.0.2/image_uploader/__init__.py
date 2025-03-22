import streamlit.components.v1 as components
import streamlit as st
import os

_RELEASE = True

if _RELEASE:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend","dist")
    _image_uploader = components.declare_component(
        "image_uploader",
        path=build_dir,
    )
else:
    _image_uploader = components.declare_component(
        "image_uploader",
        url="http://localhost:5173",
    )

def image_uploader(buttonText, dropText, allowedFormatsText, borderColor, buttonColor, buttonTextColor, hoverButtonColor, key = None):
    # if key is none provided a unique key is generated
    return _image_uploader(buttonText=buttonText, dropText=dropText, allowedFormatsText=allowedFormatsText, borderColor=borderColor, buttonColor=buttonColor, buttonTextColor=buttonTextColor, hoverButtonColor=hoverButtonColor, key=key)

if not _RELEASE:
    result = image_uploader(
        buttonText="Upload Image", 
        dropText="Drag and Drop Image Here", 
        allowedFormatsText="Allowed formats: .jpg, .png", 
        borderColor = "#CC6CE7", 
        buttonColor = "#C2DBDC", 
        buttonTextColor = "#000",
        hoverButtonColor = "#97BDBE ",
        key="1  "
        )

    st.write(result)    
