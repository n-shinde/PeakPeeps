How To Test Locally

1. Install Docker
2. Install Supabase CLI [https://github.com/supabase/cli]
3. Create local Supabase server [https://supabase.com/docs/guides/cli/local-development]
4. Copy our schema design into the test server
   1. access the local supabase studio at [http://localhost:54323/project/default]
   1. Making sure to create tables that have foreign keys last, go through our dataFiles/schema.sql file and copy and paste each table creation statement and run the query to create each table. You might encounter an error if you try to create a table that relies on a table that hasn't been created yet
5. Make sure that your env has:

   `DEVELOPMENT_POSTGRES_URI = postgresql://postgres:postgres@127.0.0.1:54322/postgres

   DEPLOYMENT_TYPE = development`

6. run `pip install -r requirements.txt` (a couple of new packages are needed for testing)
7. run `pytest tests/test_integration.py`
8. bonus points: you can test through VSCode using the left pane
