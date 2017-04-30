from pymongo import MongoClient
from cnblogs_spider import settings

aclient = MongoClient("mongodb://{host}:{port}".format(host=settings.MONGODB_SERVER_IP,port=settings.MONGODB_SERVER_PORT))
adb = aclient[settings.MONGODB_SERVER_DB_NAME]
print("{} {} {} {}".format(settings.MONGODB_SERVER_IP, settings.MONGODB_SERVER_PORT, settings.MONGODB_SERVER_DB_NAME, settings.MONGODB_SERVER_ACCOUNT_DOC))

class mongodb_operate:

    @classmethod
    def IsAuthorAccountNameExist(cls, aname):
        items = adb[settings.MONGODB_SERVER_ACCOUNT_DOC].find_one({"AuthorAccountName":aname})
        # print("IsAuthorAccountNameExist accout {} item {}".format(aname, items))
        return 0 if items ==None else 1

    @classmethod
    def InsertAccount(cls, aaccount):
        #如果没有帐户名字段，取消插入
        if "AuthorAccountName" not in aaccount:
            return 0
        # print("InsertAccount accout {}".format(aaccount));
        adb[settings.MONGODB_SERVER_ACCOUNT_DOC].update({'AuthorAccountName':aaccount['AuthorAccountName']},aaccount,True)

    @classmethod
    def InsertAccountAvatar(cls, aavatar):
        if "AuthorAccountName" not in aavatar:
            return 0
        adb[settings.MONGODB_SERVER_AVATAR_DOC].update({'AuthorAccountName': aavatar['AuthorAccountName']}, aavatar, True)