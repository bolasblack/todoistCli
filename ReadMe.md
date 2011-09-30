A simple cli client for [todoist](http://todoist.com/)

Install:

    sudo -s
    cp todoistCli.py /usr/bin/todoist
    chmod 755 /usr/bin/todoist


~/.todoistCliCfg example:

    {
        //Your todoist API
        "api_token":"xxx",
        //The -i option default project id
        "project_id":123 (must larger than 4)
    }
