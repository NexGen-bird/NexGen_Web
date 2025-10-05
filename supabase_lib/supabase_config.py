from supabase import create_client, Client
# from gotrue.errors import AuthApiError

# Replace these with your Supabase Project details
SUPABASE_URL = "https://dvobjzoqovdrsuzhjnkf.supabase.co"  # From the Supabase Dashboard
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2b2Jqem9xb3ZkcnN1emhqbmtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIzNzY5MjUsImV4cCI6MjA0Nzk1MjkyNX0.YiMofxYQxrp4YjO3zdSB2pThHXY62KJRppmZLxaFGBo"  # From the API Settings

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
