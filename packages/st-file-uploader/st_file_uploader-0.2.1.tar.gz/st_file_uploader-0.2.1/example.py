import streamlit as st
import st_file_uploader as stf

# Set page title and description
st.title("Custom File Uploader Demo")
st.write("This demo shows different ways to customize the file uploader component.")

# Using fully custom version
st.subheader("Fully Custom Version")
custom = stf.create_custom_uploader(
    uploader_msg="Drop your amazing file here!",
    limit_msg="Maximum size is 200MB",
    button_msg="Select File",
    icon="MdFileUpload"
)

file_custom = custom.file_uploader(
    "Upload with custom text",
    type=["xlsx", "csv"],
    accept_multiple_files=True,
)

# Basic usage (English default)
st.subheader("Basic Usage (Default English)")
file = stf.file_uploader(
    "Upload a CSV file",
    type="csv",
)

# Using Spanish version
st.subheader("Spanish Version")
file_es = stf.es.file_uploader(
    "Sube un archivo CSV",
    type="csv",
)

# Mix of language with custom overrides
st.subheader("French with overrides")
file_fr = stf.file_uploader(
    "Télécharger un fichier",
    type=["jpg", "png", "gif"],
    accept_multiple_files=True,
    button_msg="Sélectionner une image",
)
    
# Show multiple types
st.subheader("Multiple file types demo")
file_types = stf.file_uploader(
    "Upload documents",
    type="csv",
    accept_multiple_files=True,
)
