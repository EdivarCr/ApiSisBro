from supabase import create_client

from apisisbro.core.database import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
