#!/usr/bin/env python
# coding: utf-8
import urllib2
import urllib
import json

class ProjectIdEmptyError( Exception ): #{{{
    def __init__( self, message = None ):
        self.message = message

    def __str__( self ):
        return self.message or 'Need project id'
#}}}

def showApiToken( email, password ): #{{{
    # =======================================
    # @Description:return api_token
    #
    # @Param:str email
    # @Param:str password
    #
    # @return str
    # =======================================
    apiUrlStr = 'login'
    paramsDict = {'email':email, 'password':password}
    jsonData = request(apiUrlStr, paramsDict)
    return jsonData['api_token']
#}}}

def showProjectsList( apiToken ): #{{{
    # =======================================
    # @Description:return project id and name list
    #
    # @Param:str apiToken 
    #
    # @return str
    # =======================================
    apiUrlStr = 'getProjects'
    paramsDict = {'token':apiToken}
    jsonData = request(apiUrlStr, paramsDict)
    projectList = "Project Id:\tName:\n"
    for project in jsonData:
        projectList += str(project['id']) + '\t\t' + project['name'] + '\n'
    return projectList
#}}}

def showItemsList( apiToken, projectId, isUncompletedItems = True ): #{{{
    # =======================================
    # @Description:return items list in a project
    #
    # @Param:str apiToken
    # @Param:str projectId
    # @Param:bool isUncompletedItems
    #
    # @return str
    # =======================================
    assert type(projectId) == int, 'projectId must be int'
    apiUrlStr = 'getUncompletedItems' if isUncompletedItems else 'getCompletedItems'
    paramsDict = {'token':apiToken, 'project_id':projectId}
    jsonData = request(apiUrlStr, paramsDict)
    itemsListStr = ' Item Id\tContent\n'
    for item in jsonData:
        colorDict = {'4':'31', '3':'34', '2':'32', '1':'0;0;0'}
        colorId = '\e[0;0;0m ' + str(item['id'])
        colorfulItem = '\e[' + colorDict[str(item['priority'])] + 'm ' + item['content']
        itemsListStr += colorId + '\t' + colorfulItem + '\n'
    return itemsListStr
#}}}

def actionItems( apiToken, itemIds, action = 'complete'): #{{{
    # =======================================
    # @Description:make items complete/uncomplete
    #
    # @Param:str apiToken
    # @Param:str/int itemId
    # @Param:bool isMakeItemComplete
    #
    # @return str
    # =======================================
    for itemId in itemIds:
        assert type(itemId) == int, 'itemId must be int'
    actionDict = {'complete':'completeItems', 
                  'uncomplete':'uncompleteItems', 
                  'delete':'deleteItems'}
    apiUrlStr = actionDict[action]
    paramsDict = {'token':apiToken, 'ids':itemIds}
    result = request(apiUrlStr, paramsDict)
    return result
#}}}

def addItem( apiToken, content, projectId, priority = 4 ): #{{{
    # =======================================
    # @Description:addItem 
    #
    # @Param:str apiToken
    # @Param:str projectId
    # @Param:str content
    # @Param:str priority
    #
    # @return dict or str
    # =======================================
    assert type(projectId) == int, 'projectId must be int'
    priority = priority or 4
    assert type(priority) == int, 'priority must be int'
    priorityLv = [4, 3, 2, 1][priority - 1] #API的priority正好和web端相反
    apiUrlStr = 'addItem'
    paramsDict = {'token':apiToken, 
                  'project_id':projectId, 
                  'content':content, 
                  'priority':priorityLv}
    result = request(apiUrlStr, paramsDict)
    return result
#}}}

def request( apiUrlStr, paramsDict ): #{{{
    # =======================================
    # @Description:request 
    #
    # @Param:str apiUrlStr
    # @Param:dict paramsDict
    #
    # @return json or str
    # =======================================
    apiUrl = 'http://todoist.com/API/'
    requestUrl = apiUrl + apiUrlStr
    data = urllib.urlencode(paramsDict)
    req = urllib2.Request(requestUrl, data)
    response = urllib2.urlopen(req).read()
    try:
        result = json.loads(response)
    except:
        result = response
    finally:
        return result
#}}}

