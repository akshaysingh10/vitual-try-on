import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

st.set_page_config(page_title="Smart Virtual Try-On", layout="centered")

st.title("👕 Virtual Try-On with Smart Fitting")
st.write("Upload your full-body photo and a clothing PNG (transparent background).")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# Upload images
user_photo = st.file_uploader("Upload Your Photo", type=["jpg", "jpeg", "png"])
cloth_photo = st.file_uploader("Upload Clothing (PNG Transparent)", type=["png"])

if user_photo and cloth_photo:
    try:
        # Convert user image
        user_img = Image.open(user_photo).convert("RGB")
        user_np = np.array(user_img)
        h, w, _ = user_np.shape

        # Pose detection
        results = pose.process(cv2.cvtColor(user_np, cv2.COLOR_RGB2BGR))

        if not results.pose_landmarks:
            st.error("⚠️ Could not detect body landmarks. Try a clearer front-facing photo.")
        else:
            landmarks = results.pose_landmarks.landmark
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            left_x, left_y = int(left_shoulder.x * w), int(left_shoulder.y * h)
            right_x, right_y = int(right_shoulder.x * w), int(right_shoulder.y * h)
            shoulder_width = abs(right_x - left_x)

            # Load clothing
            cloth_img = Image.open(cloth_photo).convert("RGBA")

            if shoulder_width < 30:
                st.error("⚠️ Shoulder width too small — try a higher quality or closer photo.")
            else:
                new_width = int(shoulder_width * 2.2)
                new_height = int(new_width * cloth_img.size[1] / cloth_img.size[0])
                cloth_img = cloth_img.resize((new_width, new_height))
                cloth_np = np.array(cloth_img)

                x_offset = max(0, int((left_x + right_x) / 2 - new_width / 2))
                y_offset = max(0, int((left_y + right_y) / 2))

                # Overlay safely
                for y in range(cloth_np.shape[0]):
                    for x in range(cloth_np.shape[1]):
                        if cloth_np[y, x][3] > 0:
                            if (y + y_offset < h) and (x + x_offset < w):
                                user_np[y + y_offset, x + x_offset] = cloth_np[y, x][:3]

                result = Image.fromarray(user_np)
                st.image(result, caption="Smart Fitted Try-On", use_column_width=True)

    except Exception as e:
        st.error(f"Unexpected error: {e}")
else:
    st.info("👆 Upload a clear, front-facing photo and a transparent clothing PNG.")
