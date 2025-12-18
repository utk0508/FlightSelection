# FlightSelection
# Welcome to Adventure Air!
Adventure Air allows users to book flights between three major Canadian cities:
* Calgary
* Vancouver
* Toronto

In order to run the website you will need to have installed:
* Flask
* Python


### Flask
To install flask, you should open your computer's terminal and enter:
```bash
pip install Flask
```
To ensure Flask has been correctly installed run:
```bash
python -m flask --version
```
### Python
To install python, follow the steps at this link: https://www.python.org/downloads/

## Running the site
1. Click the dropdown arrow on the green "<> code" button.
2. Click download ZIP.
3. Once downloaded, open .zip file.
4. Now open your terminal/command line interface.
5. Navigate to the newly downloaded FlightSelection folder.
     If your folder is located on your desktop, you can navigate using the following command:
     ```bash
        cd Desktop/FlightSelection
      ```
     However you should modify the "cd" command based on the current directory you are in and where the folder is located on your computer.
7. Now run the command:
     ```bash
        python app.py
      ```
8. Your terminal will display a message "* Running on _link_". Copy and paste the _link_ into a browser.
9. You may now use the website.

Note: if you are recieving an error message "Access Denied" clear cache or run in an incognito window.
      
# Testing
In order to run our tests you will need to have installed:
* pytest

### pytest 
To install pytest you need to have pip installed. Confirm you have pip installed by running:
```bash
     pip --version
```
If you don't have pip follow download instructions here: https://pip.pypa.io/en/stable/cli/pip_install/

To instal pytest run the command:
```bash
     pip install pytest
```
Verify it was installed by runnning:
```bash
     pytest --version
```
## Running the tests
To run the pytest code:
1. Ensure you are in FlightSelection folder. If you are not use cd command in terminal to get there.
2. In terminal run command:
```bash
     pytest -s test_app.py
```

