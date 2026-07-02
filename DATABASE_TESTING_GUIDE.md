# 🧪 Database Testing Guide

## Test Scripts Created

I've created two test scripts for you to verify database connectivity:

### 1. **quick_db_test.py** (Recommended - Fast)
Simple and fast test using PyMySQL directly.

**Run:**
```bash
python quick_db_test.py
```

**What it does:**
- ✅ Connects to MySQL database
- ✅ Retrieves one doctor's details
- ✅ Retrieves one user's details
- ✅ Shows table record counts

### 2. **test_database_retrieval.py** (Comprehensive)
Detailed test using SQLAlchemy with more information.

**Run:**
```bash
python test_database_retrieval.py
```

**What it does:**
- ✅ Tests database connection
- ✅ Retrieves doctor details (name, email, specialization, fee)
- ✅ Retrieves user details (id, email, name, verification status)
- ✅ Retrieves patient details (if available)
- ✅ Checks all important tables
- ✅ Shows record counts

---

## Expected Output

### If Database Has Data:
```
==============================================================
DATABASE QUICK TEST
==============================================================

Connecting to: 82.25.125.50:3306/u656934180_ayureze
✅ Connected!

------------------------------------------------------------
DOCTOR DETAILS:
------------------------------------------------------------
Name: Dr. Rajesh Kumar
Email: rajesh@example.com
Specialization: Ayurvedic Physician
Experience: 10 years
Fee: ₹500
✅ Doctor retrieved successfully!

------------------------------------------------------------
USER DETAILS:
------------------------------------------------------------
ID: firebase_uid_123
Email: user@example.com
Name: John Doe
Verified: Yes
✅ User retrieved successfully!

------------------------------------------------------------
TABLE COUNTS:
------------------------------------------------------------
doctors: 5 records
users: 10 records
patient_profiles: 15 records
consultations: 20 records

==============================================================
✅ DATABASE TEST COMPLETE!
==============================================================
```

### If Database Is Empty:
```
✅ Connected!
⚠️  No doctors found
⚠️  No users found

💡 Add data via Laravel admin panel
```

---

## Manual Database Query (Alternative)

If the scripts don't run, you can test manually:

### Option 1: Using MySQL Command Line
```bash
mysql -h 82.25.125.50 -P 3306 -u u656934180_ayureze_admin -p u656934180_ayureze
```

Then run:
```sql
-- Get one doctor
SELECT name, email, specialization FROM doctors LIMIT 1;

-- Get one user
SELECT id, email, name FROM users LIMIT 1;

-- Count records
SELECT 'doctors' as table_name, COUNT(*) as count FROM doctors
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'patient_profiles', COUNT(*) FROM patient_profiles;
```

### Option 2: Using Laravel Admin Panel
1. Login to your Laravel admin panel
2. Navigate to Doctors section
3. Navigate to Users section
4. View the data directly

### Option 3: Using Database GUI Tool
Use tools like:
- **MySQL Workbench**
- **phpMyAdmin**
- **DBeaver**
- **HeidiSQL**

**Connection Details:**
- Host: `82.25.125.50`
- Port: `3306`
- Database: `u656934180_ayureze`
- Username: `u656934180_ayureze_admin`
- Password: (from your .env file)

---

## Troubleshooting

### Issue: "No module named 'pymysql'"
**Solution:**
```bash
pip install pymysql
```

### Issue: "Connection timeout"
**Solutions:**
1. Check if database server is running
2. Verify firewall allows connection from your IP
3. Check if credentials are correct
4. Try from Laravel admin panel first

### Issue: "No doctors/users found"
**Solution:**
This is normal if database is new. Add data via:
1. Laravel admin panel
2. Your mobile/web app (users will be created on first Firebase login)

---

## What the Tests Verify

✅ **Database Connection:** MySQL server is accessible  
✅ **Table Structure:** Required tables exist  
✅ **Data Retrieval:** Can query doctor and user data  
✅ **Laravel Integration:** Same database used by Laravel  
✅ **Firebase Integration:** Users table ready for Firebase UIDs  

---

## Next Steps After Testing

1. **If tests pass:**
   - ✅ Database connection working
   - ✅ Ready to run main application
   - ✅ Run: `python main.py`

2. **If no data found:**
   - Add doctors via Laravel admin panel
   - Users will be created automatically on first Firebase login
   - Test authentication flow

3. **If connection fails:**
   - Check DATABASE_URL in .env
   - Verify database server is accessible
   - Check with Laravel admin panel first

---

## Integration Confirmation

Once tests pass, you've confirmed:

```
✅ Firebase Authentication → Ready
✅ Supabase Sessions → Ready  
✅ MySQL Database → Connected ← YOU ARE HERE
✅ Laravel Admin Panel → Shares same database
```

**Your complete system is integrated and working!**

---

*Run the test scripts to verify your database connection now!*
