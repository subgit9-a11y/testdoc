from app.database import db_manager
import dotenv
dotenv.load_dotenv()

def run():
    # Re-initialize db_manager now that env is loaded
    db_manager.__init__()
    res = db_manager.client.rpc('exec_sql', {'sql_query': 'ALTER TABLE doctor_wallets ADD COLUMN IF NOT EXISTS upi_id text;'}).execute()
    print("Added upi_id to doctor_wallets:", res)

if __name__ == '__main__':
    run()
