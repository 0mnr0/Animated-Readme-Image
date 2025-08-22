import json
from datetime import datetime, timedelta
from types import SimpleNamespace
import pymongo

allDataBases = pymongo.MongoClient("mongodb://localhost:27017/")
readmes = allDataBases["AnimatedReadme"]

ReadmeRefreshInterval_Minutes = 240 # 4 Hours



def NameSpaceToDict(namespace):
    return json.dumps(vars(namespace), ensure_ascii=False, indent=4)

def DictToNameSpace(dct):
    return json.loads(dct, object_hook=lambda d: SimpleNamespace(**d))

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
        return datetime.now() - dt < timedelta(hours=ReadmeRefreshInterval_Minutes/60)

    @staticmethod
    def SetCooked(userName, state):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"cooked": state}})
        return True

    @staticmethod
    def IsCooked(userName):
        if not ReadmeDatabase.IsUserExists(userName): return False
        return Users.find_one({"username": userName}).get("cooked")

    @staticmethod
    def IsAnyOneCooking():
        return len(list(Users.find({"cooked": False}))) > 0 # Someone is not "cooked" yet, so he`s cooking right now

    @staticmethod
    def UpdateReadmeLineOptions(userName, options):
        if not ReadmeDatabase.IsUserExists(userName): return None
        Users.update_one({"username": userName}, {"$set": {"options": NameSpaceToDict(options)}})
        return True

    @staticmethod
    def GetReadmeLineOptions(userName):
        if not ReadmeDatabase.IsUserExists(userName): return None
        options = Users.find_one({"username": userName}).get("options")
        return None if options is None else DictToNameSpace(options)



for __tmp__user__ in ReadmeDatabase.GetAllUsers():
    ReadmeDatabase.SetCooked(__tmp__user__.get("username"), True)
    ReadmeDatabase.SetReadmeState(__tmp__user__.get("username"), " [ SINCE SERVER RELOAD WAS NOT ANY EVENT ABOUT IMAGE REFRESH ]")



print("0mnr0 Options: ", ReadmeDatabase.GetReadmeLineOptions("0mnr0"))