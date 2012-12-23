#!/usr/bin/env python
# coding: utf-8
import todoistSDK
import argparse
import colorama
import json
import sys
import os
import re

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


class ItemPriorityError(TodoistError):
    errorText = 'priority must be number'

class ApiTokenEmptyError(TodoistError):
    errorText = 'Need todoist api token'
# ]]]


def showProjectsList(projects):  # [[[
    projectList = "Project Id:\tName:\n"
    for project in projects:
        projectList += str(project['id']) + '\t\t' + project['name'] + '\n'
    return projectList
# ]]]


def showItemsList(todoist, projectId, isUncompletedItems=True):  # [[[
    itemsListStr = 'Item Id\t\tContent\n'
    todoistAttr = "uncompletedItems" if isUncompletedItems else 'completedItems'
    colorDict = [
        colorama.Fore.RESET,
        colorama.Fore.GREEN,
        colorama.Fore.BLUE,
        colorama.Fore.RED
    ]
    for item in getattr(todoist, todoistAttr)(projectId):
        colorId = colorama.Fore.RESET + str(item['id'])
        colorfulItem = colorDict[item['priority'] - 1] + item['content']
        itemsListStr += colorId + '\t' + colorfulItem + colorama.Fore.RESET + '\n'
    return itemsListStr
# ]]]


def aliasFilter(aliasName):  # [[[
    return getUserConfig().get('alias', {}).get(aliasName, aliasName)
# ]]]


def itemContentProcess(itemContent): # [[[
    priorityRE = re.compile('\s+!p(\d)(\s+|$)', re.IGNORECASE)
    priorityMatchList = priorityRE.findall(itemContent)
    if len(priorityMatchList):
        priority = priorityMatchList[0][0]
        content = priorityRE.sub("", itemContent, 1)
    else:
        priority = 4
        content = itemContent
    return {
        "priority": int(priority),
        "content": content
    }
# ]]]


def actionByArgv(config, args):  # [[[
    # 获取 token
    accountInfo = args.accountInfo
    if accountInfo and len(accountInfo) is 2:
        return todoistSDK.Todoist(email=accountInfo[0], password=accountInfo[1]).apiToken

    apiToken = config.get('api_token', '')
    todoist = todoistSDK.Todoist(token=apiToken)

    # item action
    for actionTodoName in ["complete", "uncomplete", "delete"]:
        itemId = getattr(args, actionTodoName + "Items")
        if itemId:
            return getattr(todoist, actionTodoName + "Items")(itemId)

    projects = todoist.project()
    defaultProject = config.get("default_project", None)
    projectId = defaultProject if defaultProject else projects[0]["id"]
    projectNameList = args.projectNameList
    # 准备 projectId
    if projectNameList and len(projectNameList) > 0:
        projectName = projectNameList[0]
        projectId = aliasFilter(projectName)

    itemContentList = args.itemContent
    # add item
    if itemContentList and len(itemContentList) > 0 and projectId:
        itemParams = itemContentProcess(itemContentList[0])
        content = itemParams['content']
        del itemParams['content']
        return todoist.addItem(projectId, content, **itemParams)

    # list projects
    if not projectNameList:
        return showProjectsList(projects)

    # list items
    if projectId:
        itemStr = showItemsList(todoist, projectId)
        return itemStr.replace('"', '\\"')

    return False
# ]]]


def argsParser(): # [[[
    parser = argparse.ArgumentParser(description=u"一个简易的 todoist cli 客户端")
    parser.add_argument("--token", metavar=("Email", "Password"), dest="accountInfo", nargs=2, help=u"输入账号密码，获取账号的 token")

    # TODO: 需要有个默认的优先级和项目，这样才能快速添加
    parser.add_argument("-a", "--add", metavar="item content", dest="itemContent", nargs=1, help=u"添加待办事项，支持部分 Web App 语法 （目前只支持设定 priority ）")
    parser.add_argument("-p", "--proj", metavar="ProjectId", dest="projectNameList", nargs="*", help=u"用于配合 -a -c -u -d 指定项目别名或者项目ID，如果没有其他参数，那么就列出该项目的待办事项，如果 -p 没有传入参数，那么就会列出所有的项目和项目ID")

    actionGroup = parser.add_mutually_exclusive_group()
    actionGroup.add_argument("-c", "--cpl", metavar="ItemId", dest="completeItems", nargs="+", type=int, help=u"将若干Item标记为完成")
    actionGroup.add_argument("-u", "--ucpl", metavar="ItemId", dest="uncompleteItems", nargs="+", type=int, help=u"将若干Item标记为未完成状态")
    actionGroup.add_argument("-d", "--del", metavar="ItemId", dest="deleteItems", nargs="+", type=int, help=u"删除若干个Item")

    return parser
# ]]]


def getUserConfig():  # [[[
    configFilePath = os.path.expanduser('~/.todoistCliCfg')
    with open(configFilePath) as f:
        config = json.loads(f.read())
    return config or {}
# ]]]


def main(args):
    parsedArgs = argsParser().parse_args(args=args)
    try:
        config = getUserConfig()
        result = actionByArgv(config, parsedArgs)
        if result is False:
            argvObj.print_help()
        else:
            try:
                print result.encode('utf-8')
            except:
                print result
    except Exception, e:
        print colorama.Fore.RED + str(e) + colorama.Fore.RESET


if __name__ == "__main__":
    main(sys.argv[1:])
