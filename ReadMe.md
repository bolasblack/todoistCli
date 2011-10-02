A simple cli client for [todoist](http://todoist.com/)

Install:

    chmod a+x install.sh
    sudo ./install.sh

~/.todoistCliCfg example:

    {
        //Your todoist API
        "api_token":"xxx",
        //The -i option default project id
        "project_id":123 (must larger than 4), 
        //Can alisa project id
        "alisa":{
            "test":1350142
        }
    }

**key of alisa dict must be string**

以下列出使用方法，如果没有输入 Project id 则会使用配置文件设定的默认 Project

> todoist [-l] [Project id/alisa] 列出项目里的 Item  
todoist -p 列出项目表  
todoist -a [Project id/alisa] [priority] content 在某个项目里添加 Item  
todoist -c Item ids 完成若干 Items  
todoist -u Item ids 取消完成若干 Items  
todoist -d Item ids 删除若干 Items  
todoist -t Email Password 获取 Api Token  
todoist -h 帮助
