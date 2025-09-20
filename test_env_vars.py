from dotenv import load_dotenv
import os

load_dotenv()

print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY'))
print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY'))
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('SUPABASE_KEY:', os.getenv('SUPABASE_KEY'))
