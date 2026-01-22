from supabase import create_client
import streamlit as st


@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


def bucket_name() -> str:
    return st.secrets.get("UPLOAD_BUCKET", "kuki-uploads")
