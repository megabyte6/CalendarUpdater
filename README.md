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
