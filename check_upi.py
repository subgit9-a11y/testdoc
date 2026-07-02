from app.database import db_manager
import dotenv

dotenv.load_dotenv()
db_manager.__init__()

res = db_manager.client.table('doctor_wallets').select('upi_id').limit(1).execute()
print("Query successful! Data:", res.data)
