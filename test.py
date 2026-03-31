from dotenv import load_dotenv
import os
load_dotenv()
key = os.environ.get('GEMINI_API_KEY', 'NOT FOUND')
print('Key:', key[:10] + '...' if len(key) > 10 else key)

"""naisu"""
