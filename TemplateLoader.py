from DataTypes import *
from Utils import *

class TemplateLoader:
    def __init__(self):
        self.templates = None

    def Setup(self, filePath: str):
        self.filePath = filePath

    def LoadAll(self) -> dict[int, Template]:
        with open(self.filePath, 'r') as json_file:
            json_data = json_file.read()
            notifyList = TemplateList.from_json(json_data)
            if notifyList is not None:
                self.templates = notifyList
        return self.templates

    def GetTemplates(self):
        return self.templates