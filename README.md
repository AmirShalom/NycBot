# NycBot
In this repository you can find the source code for the Telegram bot for New York city. 
In the current version, the bot has the following capabilities:

- Locating the closest farmers' market to your current location.
- Listing the farmers' markets in the city by day.
- Finding the 5 free closest Wifi spots in NYC.
- Finding the 5 closest public bathrooms in NYC.

You can run the bot using the Ansible playbook deploy-app.yaml with this command:
```
ansible-playbook deploy-app.yaml -e OPENDATA_API_TOKEN='' -e TELEGRAM_API_TOKEN="" -e MAPS_API_TOKEN='' -e WORK_DIR='' --inventory '' --ask-pass --ask-become-pass
```


![image](https://user-images.githubusercontent.com/40948212/185494783-c9739e92-69e0-4775-b727-35c30d62bf11.png)

