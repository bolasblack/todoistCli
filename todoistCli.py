#!/usr/bin/env python
# coding: utf-8
import libTodoist as todoist
import json
import sys
import os

# TODO:
# 添加本地离线支持

def addItem(apiToken, argvs): #{{{
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
            raise todoist.ProjectIdEmptyError
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
    return todoist.addItem(apiToken, content, projectId, priority)
#}}}

def listItem(apiToken, argvs): #{{{
    if len(argvs) > 1:
        projectId = argvs[1]
    else:
        try:
            projectId = config['project_id']
        except KeyError:
            raise todoist.ProjectIdEmptyError
    taskStr = todoist.showItemsList(apiToken, projectId).encode('utf-8')
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
        print todoist.showProjectsList(apiToken)
    elif argvs[0] == '-i':
        listItem(apiToken, argvs)
    elif argvs[0] == '-a':
        print addItem(apiToken, argvs)
    elif argvs[0] == '-t':
        email = argvs[1]
        password = argvs[2]
        print 'Your api token : ' + todoist.showApiToken(email, password)
    elif argvs[0] in actionArgvDict.keys():
        idsList = []
        action = actionArgvDict[argvs[0]]
        for id in argvs[1:]:
            intId = int(id)
            idsList.append(intId)
        print todoist.actionItems(apiToken, idsList, action)
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
