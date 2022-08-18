# NycBot
In this repository you can find the source code of the Telegram bot for New York city.
In the current version the bot have these capabilities:

- Finding the closest farmers' market to your current location
- Listing the farmers' markets in the city by days 
- Finding the 5 closest to you free Wifi in NYC
- Finding the 5 closest to you public bathroom in NYC

You can run the bot using the Ansible playbook deploy-app.yaml with this command:
```
ansible-playbook deploy-app.yaml -e OPENDATA_API_TOKEN='' -e TELEGRAM_API_TOKEN="" -e MAPS_API_TOKEN='' -e WORK_DIR='' --inventory '' --ask-pass --ask-become-pass
```

![image](https://user-images.githubusercontent.com/40948212/185494783-c9739e92-69e0-4775-b727-35c30d62bf11.png)

