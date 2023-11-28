How To Test Locally

1. Install Docker
2. Install Supabase CLI [https://github.com/supabase/cli]
3. Create local Supabase server [https://supabase.com/docs/guides/cli/local-development]
4. Make sure that your env has:

   `DEVELOPMENT_POSTGRES_URI = postgresql://postgres:postgres@127.0.0.1:54322/postgres
DEPLOYMENT_TYPE = development`

5. install pytest (just run `pip install pytest`) in the peak peeps repo
6. run `pytest tests/test_integration.py`
7. bonus points: you can test through VSCode using the left pane
