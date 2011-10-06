#!/usr/bin/env python
# coding: utf-8
import urllib2
import urllib
import json
import sys
import os

# TODO:添加本地离线支持（缓存）
#   用户 -i 时能够立刻列出来
#   用户 action 了以后自动更新缓存
#   离线的时候使用缓存，能上网了再和服务器交互

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

def addItem( apiToken, itemParams ): #{{{
    # =======================================
    # @Description:addItem 
    #
    # @Param:str apiToken
    # @Param:dict itemParams = {'project_id':..., 
    #                           'priority':..., 
    #                           'content':...}
    #
    # @return dict or str
    # =======================================
    projectId = itemParams['project_id']
    assert type(projectId) == int, 'projectId must be int'
    priority = itemParams['priority'] or 4
    assert type(priority) == int, 'priority must be int'
    content = itemParams['content']
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


def aliasFilter( aliasName ): #{{{
    try:
        config = getUserConfig()
        aliasDict = config['alias']
    except KeyError:
        return aliasName
    else:
        for k in aliasDict.keys():
            try:
                int(k)
                raise Exception, 'Project id alias must be string'
            except ValueError:
                pass
        if aliasName in aliasDict.keys():
            return aliasDict[aliasName]
        else:
            return aliasName
#}}}

def addItemByArgvs( apiToken, argvs, config ): #{{{
    # case: -a 'content' or 'content'
    def contentHandler( argvs ): #{{{
        priority = None
        projectId = config['project_id']
        content = argvs[0] if not argvs[0] == '-a' else argvs[1]
        return {'project_id':projectId, 
                'priority':priority, 
                'content':content}
    #}}}

    # case: X X 'content'
    def argvsHandler( argvs ): #{{{
        try:
            if int(argvs[0]) < 5:
            # case: priority X 'content'
                itemParams = priorityHandler(argvs)
            else:
            # case: projID X 'content'
                itemParams = projIDHandler(argvs)
            return itemParams
        except ValueError:
         # case: projAlias X 'content'
            argvs[0] = aliasFilter(argvs[0])
            itemParams = projIDHandler(argvs)
            return itemParams
    #}}}
        
    # case: priority X X
    def priorityHandler( argvs ): #{{{
        priority = int(argvs[0])
        if len(argvs) < 3:
        # case: priority 'content'
            try:
                projectId = config['project_id']
            except KeyError:
                raise ProjectIdEmptyError
            content = argvs[1]
        else:
        # case: priority projectId 'content'
            projectId = argvs[1]
            content = argvs[2]
        return {'project_id':projectId, 
                'priority':priority, 
                'content':content}
    #}}}

    # case: projID X X
    def projIDHandler( argvs ): #{{{
        projectId = argvs[0]
        if type(argvs[1]) is str: 
        # case: projID 'content'
            priority = None
            content = argvs[1]
        else:
        #case: projID priority 'content'
            priority = int(argvs[1]) or None
            content = argvs[2]
        return {'project_id':projectId, 
                'priority':priority, 
                'content':content}
    #}}}

    if len(argvs) < 3:
    # case: 'content' or -a 'content'
        itemParams = contentHandler(argvs)
    elif not argvs[0] == '-a':
    # case: X X 'content'
        itemParams = argvsHandler(argvs)
    else:
    # case: -a X X 'content'
        itemParams = argvsHandler(argvs[1:])
    return addItem(apiToken, itemParams)
#}}}

def listItem( apiToken, argvs ): #{{{
    if len(argvs) > 1:
    # case: -l test/123456
        projectId = aliasFilter(argvs[1])
    else:
    # case: -l
        try:
            projectId = config['project_id']
        except KeyError:
            raise ProjectIdEmptyError
    taskStr = showItemsList(apiToken, projectId).encode('utf-8')
    taskStr = taskStr.replace('"', '\\"')
    os.system('echo -e "' + taskStr + '"') 
#}}}

def actionByArgv( config, argvs ): #{{{
    # ======================================= {{{
    # @Description:call function by argv
    #
    # @Param:config dict 配置文件的配置
    # @Param:argvs str 启动参数
    #
    # @return None
    # ======================================= }}}
    apiToken = config['api_token']
    actionArgvDict = {'-c':'complete', '-u':'uncomplete', '-d':'delete'}
    if len(argvs) == 0 or argvs[0] == '-l':
        listItem(apiToken, argvs)
    elif argvs[0] == '-p':
        print showProjectsList(apiToken)
    elif argvs[0] == '-t':
        email = argvs[1]
        password = argvs[2]
        print 'Your api token : ' + showApiToken(email, password)
    elif argvs[0] in actionArgvDict.keys():
        idsList = []
        action = actionArgvDict[argvs[0]]
        for id in argvs[1:]:
            intId = int(id)
            idsList.append(intId)
        print actionItems(apiToken, idsList, action)
    elif argvs[0] == '-h':
        helpStr = '''Usage:
        [-l] [Project id] 列出项目里的 Item
        -p 列出 Project 和 Project id
        -a [Project id] [priority] content 在某个项目里添加 Item
        -c Item ids 完成若干 Items
        -u Item ids 取消完成若干 Items
        -d Item ids 删除若干 Items
        -t email password 获取 Api Token
        -h 帮助'''
        print helpStr
    else: # 其他任意字符串，包括 -a
        print addItemByArgvs(apiToken, argvs, config)
#}}}

def getUserConfig(): #{{{
    # =======================================
    # @Description:get user's config file content
    #
    # ~/.todoistCliCfg example:
    #{
    #   "api_token":"xxx",
    #   "project_id":123 (must larger than 4)
    #}
    #
    # @return dict
    # =======================================
    configFilePath = os.path.expanduser('~/.todoistCliCfg')
    with open(configFilePath) as f:
        config = json.loads(f.read())
    return config
#}}}

if __name__ == "__main__":
    argvs = sys.argv[1:]
    try:
        config = getUserConfig()
        actionByArgv(config, argvs)
    except Exception, e:
        os.system('echo -e "\e[41;37mError: ' + str(e) + '\e[0m"')
