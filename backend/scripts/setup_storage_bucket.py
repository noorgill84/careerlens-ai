"""
One-time setup: creates the private "resumes" Storage bucket in Supabase.

Run once per Supabase project, after `supabase/schema.sql`:
    cd backend
    python scripts/setup_storage_bucket.py

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your environment
(.env is NOT auto-loaded here — export them or `source .env` first, to
keep this script's dependencies minimal).
"""
import os
import sys


def main() -> None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in your environment.", file=sys.stderr)
        sys.exit(1)

    from supabase import create_client
    client = create_client(url, key)

    bucket_name = "resumes"
    existing = client.storage.list_buckets()
    if any(b.name == bucket_name for b in existing):
        print(f"Bucket '{bucket_name}' already exists — nothing to do.")
        return

    client.storage.create_bucket(
        bucket_name,
        options={"public": False},  # private: only accessible via the service role key (server-side)
    )
    print(f"Created private storage bucket '{bucket_name}'.")


if __name__ == "__main__":
    main()
