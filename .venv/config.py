import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_GEMINI = os.getenv('GOOGLE_API_KEY')
API_KEY_GOOGLE_SEARCH = os.getenv('GOOGLE_SEARCH_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')