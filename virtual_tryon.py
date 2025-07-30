# Install dependencies first:
# pip install streamlit opencv-python pillow numpy

import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("👕 Virtual Try-On Demo")
st.write("Upload your photo and a clothing item to preview it instantly.")

# Upload user photo
user_photo = st.file_uploader("Upload Your Full-Body Photo", type=["jpg", "jpeg", "png"])
cloth_photo = st.file_uploader("Upload Clothing Item (PNG with Transparent BG)", type=["png"])

if user_photo and cloth_photo:
    user_img = Image.open(user_photo).convert("RGBA")
    cloth_img = Image.open(cloth_photo).convert("RGBA")

    # Resize clothing to match user width
    user_width, user_height = user_img.size
    cloth_width = int(user_width * 0.6)  # Adjust % for scaling
    cloth_height = int(cloth_width * cloth_img.size[1] / cloth_img.size[0])
    cloth_img = cloth_img.resize((cloth_width, cloth_height))

    # Convert to numpy
    user_np = np.array(user_img)
    cloth_np = np.array(cloth_img)

    # Overlay clothing at chest area (tweak values to fit)
    x_offset = int(user_width * 0.2)
    y_offset = int(user_height * 0.25)

    for y in range(cloth_np.shape[0]):
        for x in range(cloth_np.shape[1]):
            if cloth_np[y, x][3] > 0:  # check alpha
                if y + y_offset < user_height and x + x_offset < user_width:
                    user_np[y + y_offset, x + x_offset] = cloth_np[y, x]

    result = Image.fromarray(user_np)

    st.image(result, caption="Your Virtual Try-On", use_column_width=True)
