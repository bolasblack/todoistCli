#!/usr/bin/env python
# coding: utf-8
import json, os


#edit local storage
class localFileStorage(object):
    def __init__(self, folderPath):
        self.__folderPath = folderPath if folderPath.endswith('/') else folderPath + '/'
        self.__checkPathExist(self.__folderPath)

    def set(self, fileName, inputContent):
        contentType = type(inputContent)
        assert contentType in [dict, str], 'InputContent must be dict or str'
        filePath = self.__getFilePath(fileName)
        inputJSON = json.loads(inputContent) if contentType == str else inputContent
        self.__updateByJSON(filePath, inputJSON)

    def get(self, fileName):
        filePath = self.__getFilePath(fileName)
        with open(filePath) as f:
            fileContent = f.read()
        try:
            contentJSON = json.loads(fileContent)
        except ValueError:
            contentJSON = {}
        return contentJSON

    def __getFilePath(self, fileName):
        endStr = '' if fileName.endswith('.json') else '.json'
        filePath = self.__folderPath + fileName + endStr
        self.__checkPathExist(filePath)
        return filePath

    def __checkPathExist(self, Path):
        if not os.path.exists(Path):
            os.mkdir(Path) if Path.endswith('/') else os.mknod(Path)

    def __updateByJSON(self, filePath, inputJSON):
        with open(filePath, 'r+') as f:
            try:
                fileContent = f.read()
                contentJSON = json.loads(fileContent)
            except ValueError:
                resultJSON = inputJSON
            else:
                inputKeyValueList = zip(inputJSON.keys(), inputJSON.values())
                contentKeyValueList = zip(contentJSON.keys(), contentJSON.values())
                resultJSON = dict(set(inputKeyValueList) - set(contentKeyValueList))
            finally:
                f.write(json.dumps(resultJSON))
