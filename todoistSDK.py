# coding: utf-8

import urllib2
import urllib
import json
import pdb

def firstCharUpper(string):
    listStr = list(string)
    listStr[0] = string[0].upper()
    return ''.join(listStr)

# [[[ Error
class TodoistError(Exception):
    error = 'TodoistError'

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return "[TodoistError]: " + self.message or self.error

class LoginError(TodoistError):
    returnStr = "LOGIN_ERROR"
    error = "Login error"

class ProjectNotFound(TodoistError):
    returnStr = "ERROR_PROJECT_NOT_FOUND"
    error = "Project not found"

class NameIsEmpty(TodoistError):
    returnStr = "ERROR_NAME_IS_EMPTY"
    error = "Name is empty"

class WrongDateSyntax(TodoistError):
    returnStr = "ERROR_WRONG_DATE_SYNTAX"
    error = "Wrong date syntax"

class ItemNotFound(TodoistError):
    returnStr = "ERROR_ITEM_NOT_FOUND"
    error = "Item not found"
# ]]]

class Todoist(object):
    apiBaseUrl = 'http://todoist.com/API/'
    apiToken = None

    def __init__(self, **kwargs): # [[[
        self.debugMode = kwargs.get("debugMode", False)
        if "email" in kwargs and "password" in kwargs:
            jsonData = self._request('login', kwargs)
            self.apiToken = jsonData['api_token']
        elif "token" in kwargs:
            self.apiToken = kwargs["token"]
        else:
            raise LoginError
    # ]]]

    def _request(self, apiUrlStr, paramsDict={}): #[[[
        paramsDict = dict(paramsDict)
        if self.apiToken and 'token' not in paramsDict:
            paramsDict["token"] = self.apiToken

        requestUrl = self.apiBaseUrl + apiUrlStr
        data = urllib.urlencode(paramsDict)
        if self.debugMode:
            print "requestUrl: ", requestUrl
            print "data: ", data
        req = urllib2.Request(requestUrl, data)
        response = urllib2.urlopen(req).read()
        try:
            return json.loads(response)
        except:
            return response
    # ]]]

    # project [[[
    def addProject(self, name, **params):
        params["name"] = name
        return self._request("appProjcet", params)

    def deleteProject(self, projectId):
        params = {"project_id": projectId}
        return self._request("deleteProject", param)

    def project(self, projectId=None, **paramsDict):
        if not projectId and not paramsDict:
            return self._request('getProjects')
        elif projectId and not paramsDict:
            apiUrlStr = 'getProject'
            paramsDict = {'project_id': projectId}
        elif projectId and paramsDict:
            apiUrlStr = 'updateProject'
            paramsDict["project_id"] = projectId
        return self._request(apiUrlStr, paramsDict)
    # ]]]

    # label [[[
    def addLabel(self, name, **paramsDict):
        paramsDict['name'] = name
        return self._request('addLabel', paramsDict)

    def deleteLabel(self, name):
        paramsDict['name'] = name
        return self._request('deleteLabel', paramsDict)

    def labels(self, projectId, **paramsDict):
        paramsDict['project_id'] = projectId
        return self._request('getLabels', paramsDict)
    # ]]]

    # item [[[
    def addItem(self, projectId, content, **paramsDict):
        if 'priority' in paramsDict:
            priority = int(paramsDict.get('priority', 4))
            priority = priority if 0 < priority < 5 else 4
            paramsDict['priority'] = [4, 3, 2, 1][priority - 1]

        paramsDict['project_id'] = int(projectId)
        paramsDict['content'] = content
        return self._request('addItem', paramsDict)

    def item(self, itemId, **paramsDict):
        if paramsDict == {}:
            paramsDict['ids'] = [itemId]
            itemList = self._request('getItemsById', paramsDict)
            return itemList[0]
        else:
            paramsDict['id'] = itemId
            return self._request('updateItem', paramsDict)

    def moveItems(self, itemIds, targetProjectId, sourceProjectId=None):
        paramsDict = {"to_project":  targetProjectId}
        if sourceProjectId:
            paramsDict["project_items"] = {}
            paramsDict[sourceProjectId] = itemIds
        else:
            itemsData = self.getItemsById(itemIds)
            paramsDict["project_items"] = self._generateProjectItems(itemsData)
        return self._request('moveItems', paramsDict)

    def getItemsById(self, ids):
        paramsDict['ids'] = ids
        return self._request('getItemsById', paramsDict)
    # ]]]

    def __getattr__(self, name):
        if name in ["completeItems", "uncompleteItems", "deleteItems"]:
            def fn(ids):
                paramsDict = {'ids': ids}
                return self._request(name, paramsDict)
            return fn
        if name in ['uncompletedItems', 'completedItems']:
            def fn(projectId):
                apiUrlStr = 'get%s' % firstCharUpper(name)
                paramsDict = {'project_id': projectId}
                return self._request(apiUrlStr, paramsDict)
            return fn
        raise AttributeError

    def _generateProjectItems(self, itemsData):
        projectItems = {}
        for item in itemsData:
            if item['project_id'] not in projectItems:
                projectItems[item['project_id']] = []
            projectItems[item['project_id']].append(item['id'])
        projectItems
