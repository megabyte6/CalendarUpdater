# Calendar Updater

This app is designed to pull data from the MyStudio and Homebase websites using the Selenium WebDriver and add to a Google calendar using the Google API.

## Building
### Prerequisites & Notes
1. Follow Google's [prerequisites](https://developers.google.com/calendar/api/quickstart/python#prerequisites) for access to their Calendar API.
1. Follow Google's [set up steps](https://developers.google.com/calendar/api/quickstart/python#set_up_your_environment) to ensure you have the Google Cloud project set up correctly.
1. Make sure you have `>=python3.12` installed on your computer.
1. From now on, `python` in the following commands may need to be changed to `py` or `python3` depending on your system.
1. From now on, `pip` in the following commands may need to be changed to `pip3` depending on your system.
### Alright, I got it, let's set this up
1. Download or clone this repository to your device.
1. Open a terminal in the folder once you have downloaded it (and unzipped it if needed).
1. Run the following commands to set up the environment
    1. `python -m venv .venv`
    1. `source .venv/bin/activate` or `.\.venv\Scripts\activate.ps1` (if you are on Windows, you may need to [allows scripts to run](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy#:~:text=Copy-,Set%2DExecutionPolicy%20%2DExecutionPolicy%20RemoteSigned,-%2DScope%20LocalMachine%0AGet))
    1. `pip install -r requirements.txt`
1. Run `python -m calendar_updater`
1. Now open the `settings.json` file generated in your preferred editor and fill out the fields. **Note that if `SCOPES` in `settings.json` is modified, be sure to delete `token.json` and run the program again to reauthorize.**
### I followed the steps, now how do I run the damn thing?
1. To start the app, run `python -m calendar_updater`
### Note: If running selenium in a Docker container
#### Setup
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
1. `docker pull selenium/standalone-chrome`
1. Open Docker Desktop
1. Navigate to the `Images` tab on the sidebar
1. Run the `selenium/standalone-chrome` image with the following options
    - Ports:
        - `4444:4444/tcp` (the `:4444/tcp` is already filled out for you)
    - Volumes:
        - | Host path  | Container path |
          | ---------- | -------------- |
          | `/dev/shm` | `/dev/shm`     |
    - Environment variables:
        - | Variable               | Value               |
          | ---------------------- | ------------------- |
          | `TZ`                   | `America/Vancouver` |
          | `SE_NODE_MAX_SESSIONS` | `2`                 |
1. Click `Run`.
#### Run it
If you previously followed the setup steps above and this is your first time running it, then there is no need to follow these steps.
1. Open Docker Desktop
1. Navigate to the `Containers` tab on the sidebar
1. Click the run arrow on the container you made in the setup step.
