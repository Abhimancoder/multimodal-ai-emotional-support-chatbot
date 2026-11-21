import streamlit as st
from typing import Tuple, Optional

def render_media_uploader(key_suffix: int = 0) -> Tuple[Optional[bytes], Optional[str], Optional[bytes], Optional[str]]:
    """
    Renders UI widgets for image and audio attachments with dynamic key reset.
    Returns: (image_bytes, image_name, audio_bytes, audio_name)
    """
    img_bytes, img_name = None, None
    aud_bytes, aud_name = None, None

    with st.expander("📎 Attach Media (Image or Audio)", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🖼️ Image Upload (JPEG/PNG, max 5MB)**")
            uploaded_image = st.file_uploader(
                "Choose an image",
                type=["png", "jpg", "jpeg"],
                key=f"img_uploader_{key_suffix}",
                label_visibility="collapsed"
            )
            if uploaded_image is not None:
                img_bytes = uploaded_image.getvalue()
                img_name = uploaded_image.name
                st.image(uploaded_image, caption=f"Selected: {img_name}", use_column_width=True)

        with col2:
            st.markdown("**🎙️ Voice Note / Audio (WAV/MP3, max 10MB)**")
            uploaded_audio = st.file_uploader(
                "Choose an audio file",
                type=["wav", "mp3"],
                key=f"aud_uploader_{key_suffix}",
                label_visibility="collapsed"
            )
            if uploaded_audio is not None:
                aud_bytes = uploaded_audio.getvalue()
                aud_name = uploaded_audio.name
                st.audio(uploaded_audio)

    return img_bytes, img_name, aud_bytes, aud_name
