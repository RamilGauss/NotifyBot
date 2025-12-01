import json
import os

from DataTypes import *

def get_files_by_extension_single_dir(directory_path, extension):
    files_with_extension = []
    for filename in os.listdir(directory_path):
        if filename.endswith(extension) and os.path.isfile(os.path.join(directory_path, filename)):
            files_with_extension.append(os.path.join(directory_path, filename))
    return files_with_extension

class NotifyLoader:
    def __init__(self):
        self.users = {}

    def Setup(self, dirPath: str) -> dict[int, UserInfo]:
        self.dirPath = dirPath

    def LoadAll(self) -> dict[int, UserInfo]:
        self.users = {}
        fileNames = get_files_by_extension_single_dir(self.dirPath, "json")
        for fileName in fileNames:
            with open(fileName, 'r') as json_file:
                json_data = json_file.read()
                notifyList = UserInfo.from_json(json_data)
                if notifyList is not None:
                    self.users[notifyList.user_id] = notifyList
        return self.users

    def Save(self, notifyList: UserInfo):
        fileName = os.path.join(self.dirPath, f"{self.dirPath}/{notifyList.user_id}.json")
        with open(fileName, 'w') as json_file:
            json.dump(notifyList.__dict__,  json_file, default=lambda o: o.__dict__, indent=4, sort_keys=True)
