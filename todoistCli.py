#!/usr/bin/env python
# coding: utf-8
import argparse
import urllib2
import urllib
import json
import sys
import os
import re

import pdb

# TODO:添加本地离线支持（缓存）
#   用户 -i 时能够立刻列出来
#   用户 action 了以后自动更新缓存
#   离线的时候使用缓存，能上网了再和服务器交互


# [[[ Error
class TodoistError(Exception):
    errorText = 'TodoistError'

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.errorText


class ProjectIdError(TodoistError):
    errorText = 'Need project id or alias name'


class ProjectAliasError(TodoistError):
    errorText = "Project alias can't be number"


class TaskIdError(TodoistError):
    errorText = 'Need task id'


class TaskPriorityError(TodoistError):
    errorText = 'priority must be number'


class ApiTokenEmptyError(TodoistError):
    errorText = 'Need todoist api token'
# ]]]


def showApiToken(email, password):  # [[[
    # =======================================
    # @Description:return api_token
    #
    # @Param:str email
    # @Param:str password
    #
    # @return str
    # =======================================
    apiUrlStr = 'login'
    paramsDict = {'email': email, 'password': password}
    jsonData = request(apiUrlStr, paramsDict)
    return jsonData['api_token']
# ]]]


def showProjectsList(apiToken):  # [[[
    # =======================================
    # @Description:return project id and name list
    #
    # @Param:str apiToken
    #
    # @return str
    # =======================================
    apiUrlStr = 'getProjects'
    paramsDict = {'token': apiToken}
    jsonData = request(apiUrlStr, paramsDict)
    projectList = "Project Id:\tName:\n"
    for project in jsonData:
        projectList += str(project['id']) + '\t\t' + project['name'] + '\n'
    return projectList
# ]]]


def showTasksList(apiToken, projectId, isUncompletedTasks=True):  # [[[
    # =======================================
    # @Description:return tasks list in a project
    #
    # @Param:str apiToken
    # @Param:str projectId
    # @Param:bool isUncompletedTasks
    #
    # @return str
    # =======================================
    if type(projectId) is not int:
        raise ProjectIdError
    apiUrlStr = 'getUncompletedItems' if isUncompletedTasks else 'getCompletedItems'
    paramsDict = {'token': apiToken, 'project_id': projectId}
    jsonData = request(apiUrlStr, paramsDict)
    tasksListStr = ' Task Id\tContent\n'
    for task in jsonData:
        colorDict = {'4': '31', '3': '34', '2': '32', '1': '0;0;0'}
        colorId = '\e[0;0;0m ' + str(task['id'])
        colorfulTask = '\e[' + colorDict[str(task['priority'])] + 'm ' + task['content']
        tasksListStr += colorId + '\t' + colorfulTask + '\n'
    return tasksListStr
# ]]]


def actionTasks(apiToken, taskIds, action='complete'):  # [[[
    # =======================================
    # @Description:make tasks complete/uncomplete
    #
    # @Param:str apiToken
    # @Param:str/int taskId
    # @Param:str action
    #
    # @return str
    # =======================================
    def checkTaskId(taskId):
        if type(taskId) is not int:
            raise TaskIdError
    map(checkTaskId, taskIds)
    actionDict = {'complete': 'completeItems',
                  'uncomplete': 'uncompleteItems',
                  'delete': 'deleteItems'}
    apiUrlStr = actionDict[action]
    paramsDict = {'token': apiToken, 'ids': taskIds}
    result = request(apiUrlStr, paramsDict)
    return result
# ]]]


def addTask(apiToken, taskParams):  # [[[
    # =======================================
    # @Description:addTask
    #
    # @Param:str apiToken
    # @Param:dict taskParams = {'project_id':...,
    #                           'priority':...,
    #                           'content':...}
    #
    # @return dict or str
    # =======================================
    projectId = taskParams['projectId']
    if type(projectId) is not int:
        raise ProjectIdError('projectId must be int')
    priority = taskParams['priority'] or 4
    if type(priority) is not int:
        raise TaskPriorityError('priority must be int')
    content = taskParams['content']
    priorityLv = [4, 3, 2, 1][priority - 1] # API的priority正好和web端相反
    apiUrlStr = 'addItem'
    paramsDict = {'token': apiToken,
                  'project_id': projectId,
                  'content': content,
                  'priority': priorityLv}
    result = request(apiUrlStr, paramsDict)
    return result
# ]]]


def request(apiUrlStr, paramsDict):  # [[[
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
# ]]]


def aliasFilter(aliasName):  # [[[
    def checkKey(configKey):
        if type(configKey) is not str:
            raise ProjectAliasError
        if configKey.isdigit():
            raise ProjectAliasError
    config = getUserConfig()
    map(checkKey, config.keys())
    if 'alias' in config.keys():
        aliasDict = config['alias']
        return aliasDict[strAliasName] if strAliasName in aliasDict.keys() else aliasName
    else:
        return aliasName
# ]]]


def taskContentProcess(taskContent): # [[[
    priorityRE = re.compile('\s+!p(\d)(\s+|$)', re.IGNORECASE)
    priority = priorityRE.findall(taskContent)[0][0]
    content = priorityRE.sub("", taskContent, 1)
    return {
        "priority": int(priority),
        "content": content
    }
# ]]]


def actionByArgv(config, args):  # [[[
    # ======================================= {{{
    # @Description:call function by argv
    #
    # @Param:config dict 配置文件的配置
    # @Param:args str 启动参数
    #
    # @return None
    # ======================================= }}}
    if 'api_token' not in config:
        raise ApiTokenEmptyError
    apiToken = config['api_token']
    accountInfo = args.accountInfo
    projectNameList = args.projectNameList
    taskContentList = args.taskContent
    # 获取 token
    if accountInfo and len(accountInfo) > 2:
        username = accountInfo[0]
        password = accountInfo[1]
        return showApiToken(username, password)
    # 准备 projectId
    if type(projectNameList) is list:
        if len(projectNameList) > 0:
            projectName = projectNameList[0]
            projectId = aliasFilter(projectName)
        else:
            return showProjectsList(apiToken)
    # add task
    if taskContentList and len(taskContentList) > 0 and projectId is not None:
        taskParams = taskContentProcess(taskContentList[0])
        taskParams["projectId"] = projectId
        return addTask(apiToken, taskParams)
    # task action
    for actionTodoName in ["complete", "uncomplete", "delete"]:
        actionTodoArgs = args.__getattribute__(actionTodoName + "Tasks")
        if actionTodoArgs and len(actionTodoArgs) > 0:
            return actionTasks(apiToken, actionTodoArgs, actionTodoName)
    # list tasks
    if projectId is not None:
        taskStr = showTasksList(apiToken, projectId)
        return taskStr.replace('"', '\\"')
    pdb.set_trace()
    return False
# ]]]


def parseArgs(): # [[[
    parser = argparse.ArgumentParser(description=u"一个简易的 todoist cli 客户端")
    parser.add_argument("--token", metavar=("Username", "Password"), dest="accountInfo", nargs=2, help=u"输入账号密码，获取账号的 token")

    # TODO: 需要有个默认的优先级和项目，这样才能快速添加
    parser.add_argument("-a", "--add", metavar="task content", dest="taskContent", nargs=1, help=u"添加待办事项，支持部分 Web App 语法 （目前只支持设定 priority ）")
    parser.add_argument("-p", "--proj", metavar="ProjectId", dest="projectNameList", nargs="*", help=u"用于配合 -a -c -u -d 指定项目别名或者项目ID，如果没有其他参数，那么就列出该项目的待办事项，如果 -p 没有传入参数，那么就会列出所有的项目和项目ID")

    actionGroup = parser.add_mutually_exclusive_group()
    actionGroup.add_argument("-c", "--cpl", metavar="TaskId", dest="completeTasks", nargs="+", type=int, help=u"将若干Task标记为完成")
    actionGroup.add_argument("-u", "--ucpl", metavar="TaskId", dest="uncompleteTasks", nargs="+", type=int, help=u"将若干Task标记为未完成状态")
    actionGroup.add_argument("-d", "--del", metavar="TaskId", dest="deleteTasks", nargs="+", type=int, help=u"删除若干个Task")

    return parser
# ]]]


def getUserConfig():  # [[[
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
# ]]]

if __name__ == "__main__":
    argvObj = parseArgs()
    args = argvObj.parse_args()
    try:
        config = getUserConfig()
        result = actionByArgv(config, args)
        if result is False:
            argvObj.print_help()
        else:
            os.system('echo -e "' + result.encode("utf-8") + '"')
    except Exception, e:
        os.system('echo -e "\e[41;37mError: ' + str(e) + '\e[0m"')
