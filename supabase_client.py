import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url_supabase = os.getenv('URL_SUPABASE')
key_supabase = os.getenv('KEY_SUPABASE')

supabase = create_client(url_supabase, key_supabase)
