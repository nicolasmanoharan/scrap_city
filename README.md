# Data analysis

- Project: scrap_city 
- Description: The main goal of this project is to scrape Google reviews. 
- Data Source: Google reviews 
- Type of analysis: Output CSV file

This package allows you to scrape Google review data from a URL.
/!\ 

# Startup the project

The initial setup.

Create virtualenv and install the project:
```bash
sudo apt-get install virtualenv python-pip python-dev
deactivate; virtualenv ~/venv ; source ~/venv/bin/activate ;\
    pip install pip -U; pip install -r requirements.txt
```

Unittest test:
```bash
make clean install test
```

Check for scrap_city in gitlab.com/{group}.
If your project is not set please add it:

- Create a new project on `gitlab.com/{group}/scrap_city`
- Then populate it:

```bash
##   e.g. if group is "{group}" and project_name is "scrap_city"
git remote add origin git@github.com:{group}/scrap_city.git
git push -u origin master
git push -u origin --tags
```

Functionnal test with a script:

```bash
cd
mkdir tmp
cd tmp
scrap_city-run
```

# Install

Go to `https://github.com/{group}/scrap_city` to see the project, manage issues,
setup you ssh public key, ...

Create a python3 virtualenv and activate it:

```bash
sudo apt-get install virtualenv python-pip python-dev
deactivate; virtualenv -ppython3 ~/venv ; source ~/venv/bin/activate
```

Clone the project and install it:

```bash
git clone git@github.com:{group}/scrap_city.git
cd scrap_city
pip install -r requirements.txt
make clean install test                # install and test
```
Functionnal test with a script:

```bash
cd
mkdir tmp
cd tmp
scrap_city-run
```
