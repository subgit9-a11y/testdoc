class RAGMemory:
    def __init__(self, db_connection=None, max_history=10):
        self.db = db_connection
        self.max_history = max_history
        self._local_storage = {}

    def get_history(self, user_id: str):
        return self._local_storage.get(user_id, [])

    def add_message(self, user_id: str, role: str, content: str):
        if user_id not in self._local_storage:
            self._local_storage[user_id] = []
        
        self._local_storage[user_id].append({"role": role, "content": content})
        
        # Trim history
        if len(self._local_storage[user_id]) > self.max_history:
            self._local_storage[user_id] = self._local_storage[user_id][-self.max_history:]
