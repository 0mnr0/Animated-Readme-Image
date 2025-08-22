from datetime import datetime, timedelta
from operator import truediv

import pymongo

allDataBases = pymongo.MongoClient("mongodb://localhost:27017/")
readmes = allDataBases["AnimatedReadme"]


class DBSHelper:
    @staticmethod
    def CreateCollection(collectionName):
        if collectionName not in readmes.list_collection_names():
            readmes.create_collection(collectionName)

    @staticmethod
    def RemoveAny_id(jsonObject):
        if jsonObject is not None: jsonObject.pop("_id", None)
        return jsonObject

DBHelper = DBSHelper()
DBHelper.CreateCollection("Users")
Users = readmes["Users"]


class ReadmeDatabase:
    @staticmethod
    def IsUserExists(userName):
        return Users.find_one({"username": userName}) is not None

    @staticmethod
    def GetAllUsers():
        return list(Users.find())

    @staticmethod
    def CreateNewUser(userName):
        user = Users.find_one({"username": userName})
        if user is None:
            Users.insert_one({"username": userName})
            return True
        return False

    @staticmethod
    def SetReadmeState(userName, state):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"state": state}})
        return True

    @staticmethod
    def GetReadmeState(userName):
        if not ReadmeDatabase.IsUserExists(userName): return None
        return Users.find_one({"username": userName})

    @staticmethod
    def GetCurrentReadme(userName):
        if not ReadmeDatabase.IsUserExists(userName): return None
        user = Users.find_one({"username": userName})
        return user.get("ReadmePath")

    @staticmethod
    def SetCurrentReadme(userName, ReadmePath):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"ReadmePath": ReadmePath}})
        return True

    @staticmethod
    def SetReadmeTime(userName, time):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"ReadmeTime": time}})
        return True

    @staticmethod
    def HaveActualReadme(userName):
        if not ReadmeDatabase.IsUserExists(userName): return False
        return ReadmeDatabase.IsFreshReadme(userName)

    @staticmethod
    def IsFreshReadme(userName):
        if not ReadmeDatabase.IsUserExists(userName): return False
        UserObject = Users.find_one({"username": userName})
        dt = datetime.strptime(UserObject.get("ReadmeTime"), "%Y-%m-%d %H:%M")
        return datetime.now() - dt < timedelta(hours=4)

    @staticmethod
    def SetCooked(userName, state):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"cooked": state}})
        return True

    @staticmethod
    def IsCooked(userName):
        if not ReadmeDatabase.IsUserExists(userName): return False
        return Users.find_one({"username": userName}).get("cooked")


for user in ReadmeDatabase.GetAllUsers():
    ReadmeDatabase.SetCooked(user.get("username"), True)
    ReadmeDatabase.SetReadmeState(user.get("username"), " [ SINCE SERVER RELOAD WAS NOT ANY EVENT ABOUT IMAGE REFRESH ]")