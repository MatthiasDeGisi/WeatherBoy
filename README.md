# WeatherBoy
WeatherBoy is a Discord bot that serves one purpose: fueling a feud between two (now five or so) weather station enthusiasts. Invite the bot [here](https://discord.com/api/oauth2/authorize?client_id=1197038110417109122&permissions=414464862272&scope=bot).
## Requirements
The server that this bot runs on requires Python 3.12 and Docker is recommended. If windows is being used, change line 7 of docker-compose.yml to say `- C:\WeatherBoyData:/app/data` and create a folder to go along with it.


For development, a virtual environment is recommended. To install, run:
`pip install virtualenv`

To set up the virtual environment, run
`python -m venv env`

To activate the environment, run `env/Scripts/activate.bat` in CMD, or `env/Scripts/Activate.ps1` in PowerShell.

[Alternatively, VSCode has a built in feature for virtual environments.](https://code.visualstudio.com/docs/python/environments)

**Python packages:**


A requirements.txt file is provided. To use it, run `pip -r requirements.txt`.

**Docker**

A directory called /WeatherBoyData should be created on the server, which is used to hold persistent information for the container.
If using Windows (oof), this might not work.

To build the container: run `docker compose up -d --build`

**Token**
The Discord token must be an environment variable, either as a .env file or through GitHub Actions Secrets.

**Doppelganger**
https://discord.com/api/oauth2/authorize?client_id=1199146110615294052&permissions=1084479765568&scope=bot 