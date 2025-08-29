from pymongo import MongoClient

class JoinReqs2:

    def __init__(self):
        from config import JOIN_REQS_DB2, FORCE_SUB_CHANNEL2
        if JOIN_REQS_DB2:
            self.client = MongoClient(JOIN_REQS_DB2)
            self.pymongo_client = MongoClient(JOIN_REQS_DB2)
            self.db = self.client["JoinReqs2"]
            self.pymongo_db = self.pymongo_client["JoinReqs2"]
            self.col = self.db[str(FORCE_SUB_CHANNEL2)]
            self.pymongo_col = self.pymongo_db[str(FORCE_SUB_CHANNEL2)]
        else:
            self.client = None
            self.pymongo_client = None
            self.db = None
            self.pymongo_db = None
            self.col = None
            self.pymongo_col = None

    def isActive(self):
        return self.client is not None

    async def add_user(self, user_id, first_name, username, date):
        try:
             self.col.insert_one({"_id": int(user_id),"user_id": int(user_id), "first_name": first_name, "username": username, "date": date})
        except:
            pass

    async def get_user(self, user_id):
        return self.col.find_one({"user_id": int(user_id)})

    async def get_all_users(self):
        return self.col.find().to_list(None)

    async def delete_user(self, user_id):
        self.col.delete_one({"user_id": int(user_id)})

    async def delete_all_users(self):
        self.col.delete_many({})

    def get_all_users_count(self):
        return self.pymongo_col.count_documents({})
