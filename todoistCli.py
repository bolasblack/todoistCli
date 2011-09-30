#!/usr/bin/env python
# coding: utf-8
import urllib2
import urllib
import json
import sys
import os

# TODO:
# 添加本地离线支持

#help:
#   sudo -s
#   cp todoistCli.py /usr/bin/todoist
#   chmod 755 /usr/bin/todoist

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


def addItemByArgvs(apiToken, argvs): #{{{
    if type(argvs[1]) is str:
    # case: -a 'content'
        priority = None
        projectId = config['project_id']
        content = argvs[1]
    elif int(argvs[1]) < 5: 
    # case: -a priority 'content'
        try:
            projectId = config['project_id']
        except KeyError:
            raise ProjectIdEmptyError
        priority = int(argvs[1])
        content = argvs[2]
    elif int(argvs[1]) > 4: 
    # case: -a projID X X
        projectId = argvs[1]
        if argvs[2] is str: 
        # case: -a projID 'content'
            priority = None
            content = argvs[2]
        else:
        #case: -a projID priority 'content'
            priority = int(argvs[2]) or None
            content = argvs[3]
    return addItem(apiToken, content, projectId, priority)
#}}}

def listItem(apiToken, argvs): #{{{
    if len(argvs) > 1:
        projectId = argvs[1]
    else:
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
    # -h 帮助
    # -p 列出项目表
    # -i project id 列出项目里的 item
    # -a project priority content 在某个项目里添加 item
    # -c item ids 完成若干 items
    # -u item ids 取消完成若干 items
    # -d item ids 删除若干 items
    # -t email password 获取 api
    #
    # @Param:config dict 配置文件的配置
    # @Param:argvs str 启动参数
    #
    # @return None
    # ======================================= }}}
    apiToken = config['api_token']
    actionArgvDict = {'-c':'complete', '-u':'uncomplete', '-d':'delete'}
    if argvs[0] == '-p':
        print showProjectsList(apiToken)
    elif argvs[0] == '-i':
        listItem(apiToken, argvs)
    elif argvs[0] == '-a':
        print addItemByArgvs(apiToken, argvs)
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
    else:
        helpStr = '-h 帮助\n-p 列出项目表\n-i project id 列出项目里的 item\n-a project priority content 在某个项目里添加 item\n-c item ids 完成若干 items\n-u item ids 取消完成若干 items\n-d item ids 删除若干 items\n-t email password 获取 api'
        print helpStr
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
    if len(sys.argv) > 1:
        argvs = sys.argv[1:]
        try:
            config = getUserConfig()
            actionByArgv(config, argvs)
        except Exception, e:
            os.system('echo -e "\e[41;37mError: ' + str(e) + '\e[0m"')
