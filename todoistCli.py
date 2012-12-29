#!/usr/bin/env python
# coding: utf-8
"""
一个简易的 todoist cli 客户端

Usage:
  todoist [-l]
  todoist -p <project>
  todoist [-p <project>] <content>
  todoist [-p <project>] -a <content>
  todoist -c <item> [<item>...]
  todoist -u <item> [<item>...]
  todoist -d <item> [<item>...]
  todoist --token <email> <password>
  todoist -h | --help
  todoist --version

Options:
  -h, --help                  显示帮助信息
  -l, --list                  列出所有的项目
  -p, --proj <project>        用于配合 -a 指定项目别名或者项目ID，如果没有其他参数，那么就列出该项目的待办事项，如果 -p 没有传入参数，那么就会列出所有的项目和项目ID
  -a, --add <content>         添加待办事项，如果不传入项目ID，则添加至列表最上方的项目
  -c, --cpl <item> ...        将若干Item标记为完成
  -u, --ucpl <item> ...       将若干Item标记为未完成状态
  -d, --del <item> ...        删除若干个Item
  --token <email> <password>  输入账号密码，获取账号的 token
  --version                   输出版本号
"""

from docopt import docopt
import todoistSDK
import colorama
import json
import sys
import os
import re

# TODO:添加本地离线支持（缓存）
#   用户 -i 时能够立刻列出来
#   用户 action 了以后自动更新缓存
#   离线的时候使用缓存，能上网了再和服务器交互


debugMode = False


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


def showProjectsList(projects): # [[[
    projectList = "Project Id:\tName:\n"
    for project in projects:
        projectList += str(project['id']) + '\t\t' + project['name'] + '\n'
    return projectList
# ]]]


def showItemsList(todoist, projectId, isUncompletedItems=True): # [[[
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


def aliasFilter(aliasName): # [[[
    return getUserConfig().get('alias', {}).get(aliasName)
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


def addItem(todoist, projectId, itemContent): # [[[
    itemParams = itemContentProcess(itemContent)
    content = itemParams['content']
    del itemParams['content']
    return todoist.addItem(projectId, content, **itemParams)
# ]]]


def getUserConfig(): # [[[
    configFilePath = os.path.expanduser('~/.todoistCliCfg')
    with open(configFilePath) as f:
        config = json.loads(f.read())
    return config or {}
# ]]]


def getTodoist(**kwargs): # [[[
    global debugMode

    if "email" in kwargs and "password" in kwargs:
        return todoistSDK.Todoist(
          email=kwargs['email'],
          password=kwargs['password'],
          debugMode=debugMode
        )

    apiToken = getUserConfig().get('api_token', '')
    return todoistSDK.Todoist(
      debugMode=debugMode,
      token=apiToken
    )
# ]]]


def parseProjectId(inputProjectId, defaultProjectId, projects): # [[[
    if inputProjectId is None:
        return defaultProjectId if defaultProjectId else projects[0]["id"]
    aliasProjectId = aliasFilter(inputProjectId)
    if aliasProjectId:
        return aliasProjectId
    filterRightProject = lambda projectInfo: projectInfo['name'] == inputProjectId.decode('utf-8')
    rightProjects = filter(filterRightProject, projects)
    if len(rightProjects):
        return rightProjects[0]['id']
    if inputProjectId.isdigit():
        return inputProjectId
# ]]]


def actionByArgv(args): # [[[
    # 获取 token
    email = args['--token']
    password = args['<password>']
    if email and password:
        return getTodoist(email=email, password=password).apiToken

    config = getUserConfig()
    todoist = getTodoist()

    # item action
    optionDict = {
        "--cpl": "completeItems",
        "--ucpl": "uncompleteItems",
        "--del": "deleteItems"
    }
    for option in optionDict.keys():
        if args[option]:
            itemIds = args['<item>'] or []
            itemIds.append(args[option])
            itemIds = map(int, itemIds)
            return getattr(todoist, optionDict[option])(itemIds)

    projects = todoist.project()
    if args['--list']:
        return showProjectsList(projects)

    # 准备 projectId
    defaultProjectId = config.get("default_project", None)
    projectId = parseProjectId(args['--proj'], defaultProjectId, projects)

    # add item
    itemContent = args['--add'] or args['<content>']
    if itemContent and projectId:
        addItem(todoist, projectId, itemContent)

    # list items
    if projectId:
        itemStr = showItemsList(todoist, projectId)
        return itemStr.replace('"', '\\"')

    return False
# ]]]


def main(args):
    global debugMode

    if len(args) and args[0] == '--debug':
        debugMode = True
        del args[0]
    try:
        parsedArgs = docopt(__doc__, argv=args, help=True, version='0.0.2')
        if debugMode:
            print parsedArgs

        if not len(args):
            parsedArgs['--list'] = True
        result = actionByArgv(parsedArgs)
        if result is False:
            print __doc__
            return
        try:
            print result.encode('utf-8')
        except:
            print result
    except Exception, e:
        print colorama.Fore.RED + str(e) + colorama.Fore.RESET


if __name__ == "__main__":
    main(sys.argv[1:])
