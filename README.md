# WeatherBoy
WeatherBoy is a Discord bot that serves one purpose: fueling a feud between two weather station enthusiasts. Invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=1197038110417109122&permissions=414464862272&scope=bot).
## Requirements
The server that this bot runs on requires Python 3.11 and Docker is recommended. If using Docker, I have not been successful getting it to work on Windows unless the `volumes` section is removed from docker-compose.yml.


For development, a virtual environment is recommended. To install, run:
`pip install virtualenv`

To set up the virtual environment, run
`python -m venv env`

To activate the environment, run `env/Scripts/activate.bat` in CMD, or `env/Scripts/Activate.ps1` in PowerShell.

[Alternatively, VSCode has a built in feature for virtual environments.](https://code.visualstudio.com/docs/python/environments)

**Python packages:**

A requirements.txt file is provided. To use it, run `pip -r requirements.txt`.

In case you don't want to use the requirements.txt file, the requirements are listed below: 

Discord.py is required. To install, run `pip install discord.py`

Dotenv is required. To install, run `pip install python-dotenv`

Requests is required. To install, run `pip install requests`

**Docker**

A directory called /WeatherBoyData should be created on the server, which is used to hold persistent information for the container.
If using Windows (oof), this might not work.

To build the container: run `docker compose up -d --build`
