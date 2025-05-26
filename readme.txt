# SpeedGauge

SpeedGauge is a Python application designed to analize the speedGauge csv reports my company gets. It helps clean up that huge csv into individualized reports that provide drivers with a cleaner way of seeing their standing.

## instalation

to set up virtual environment:
	python3 -m venv venvFiles
	
	this will put all the virtual environment stuff into the venvFiles


1. ok, to use the virtual
environment, use: source venvFiles/bin/activate

2. on a new clone you gotta run a few commands. First is to install dependencies from the requirements.txt file.

	1. Activate the virtual environment: source venvFiles/bin/activate
	2. install dependencies: pip install -r requirements.txt

3. Install dependencies
pip install -r requirements.txt

4. download the csv files. ** eventually i want to make a dedicated database that i can connect to. then this part will change to just connecting to the database.

5. Then you gotta run the initialization file to build all the directories and db and stuff

git commands:

    git status
    git add .  (this adds all changes)
    git commit -m "commit message"
    git push

