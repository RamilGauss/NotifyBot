from DataTypes import *

class NotifyManager:
    def SetUsers(self, users: dict[int, UserInfo]):
        self.users = users

    def GetUser(self, user_id: int) -> UserInfo:
        if not user_id in self.users:
            userInfo = UserInfo(user_id, {})
            self.users[user_id] = userInfo
        return self.users[user_id]

    def GetUsers(self) -> dict[int, UserInfo]:# user_id, notifies
        return self.users