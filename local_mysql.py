from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://u656934180_ayureze_admin:nemke2%2Dzokroj%2DFibfez@82.25.125.50:3306/u656934180_ayureze')
with engine.connect() as conn:
    res = conn.execute(text("SHOW TABLES")).mappings().all()
    tables = [list(r.values())[0] for r in res]
    print("TABLES:", tables)
