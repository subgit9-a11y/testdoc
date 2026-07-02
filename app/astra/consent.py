class ConsentManager:
    def __init__(self, db_connection=None):
        self.db = db_connection

    def check_consent(self, user_id: str) -> bool:
        return True
