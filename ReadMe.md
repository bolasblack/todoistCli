A simple cli client for [todoist](http://todoist.com/)

##Install:

```sh
sudo make install
```

##Usage:

Get Token:

```sh
todoist --token EMAIL PASSWORD
```

Create `.todoistCliCfg`:

```sh
echo '{"api_token":"YOUR TOKEN"}' > ~/.todoistCliCfg
```

~/.todoistCliCfg example:

    {
        //Your todoist API
        "api_token": "xxx",
        //Default project id
        "default_project": 123 (must larger than 4), 
        //Alisa project id
        "alias": {
            "test(can't be number)":1350142
        }
    }

