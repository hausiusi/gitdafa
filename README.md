# Gitdafa

![GitHub Created At](https://img.shields.io/github/created-at/hausiusi/gitdafa)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hausiusi/gitdafa)
![GitHub branch check runs](https://img.shields.io/github/check-runs/hausiusi/gitdafa/master)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/hausiusi/gitdafa)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-closed/hausiusi/gitdafa?color=lightgray)
![GitHub License](https://img.shields.io/github/license/hausiusi/gitdafa)

# Table of contents
1. [What is Gitdafa?](#what-is-gitdafa)
2. [How to run](#how-to-run)
   1. [Requirements](#requirements)
   2. [Windows](#windows)
   3. [Linux](#linux)
3. [Usage examples](#usage-examples)
4. [Tests](#tests)
5. [Contribution](#contribution)

## What is Gitdafa

Gitdafa is a friendly tool for diving into the statistics of your git projects. 
While we know that metrics like lines of code and commit counts aren’t the ultimate 
measure of developer performance, they can still provide fascinating insights for 
anyone curious about the numbers behind the code contribution.

With Gitdafa, you can uncover trends in contributions, explore how work is distributed
among team members, and track changes over time.
It’s handy for stats' enthusiasts or anyone who just wants a deeper understanding 
of their project’s activity.

The tool is flexible and customizable, so you can focus on what matters most to you:
specific files, directories, or even filtering out unimportant data. Whether you’re
interested in contributions by author, activity by month, or want to nerd out
over the stats, Gitdafa makes it easy and fun to explore the git project.


## How to run

### Requirements

1. Python3 (3.7, 3.8, or 3.9)
2. Git (version 2.23 or higher)

To run this script, Python3 must be installed. The Python3 versions that we have 
tested are 3.7, 3.8, or 3.9.

For managing with a specific Python version, we recommend pyenv.

Before installing the project [requirements](requirements.txt) it's highly 
recommended to create a virtual environment
```commandline
cd gitdafa
python -m venv .venv
./venv/scripts/activate
pip install -r ./requirements.txt
```

### Windows
Windows usually doesn't come with Git installed. Git for windows can be downloaded
from [here](https://git-scm.com/download/win) or could be installed by typing in the 
PowerShell (that is running with administrator privileges) the following command:

`winget install --id Git.Git -e --source winget`

Follow the installation instructions and check **_add environment variables_** checkbox
during setup. If this step was missed to the PATH environment variable can be added
manually these two: `C:\Program Files\Git\usr\bin\` and `C:\Program Files\Git\cmd`

### Linux
Running the script on linux should be quite straightforward, and no specific 
installations need to be performed.

## Usage examples
The script must be run from the main directory (where the run.py is located).

To get familiar with available arguments `python run.py --help`

Bellow is an example command to the C# project

```commandline
python .\run.py -pd C:\path\to\Csharp\target\project\ -id bin obj tools .git .vs libs -ie .sln .dll .log .pdf .settings .user .ico .exe .csproj .resx .png .config .p7s .nupkg .xml ._
```
where:
* -pd C:\path\to\Csharp\target\project\ - targets to the project directory
* -id bin obj tools .git .vs libs - gets the list of directories that must be omitted
* -ie .sln .dll .log .pdf .settings .user .ico .exe .csproj .resx .png .config .p7s .nupkg .xml ._ - get the list of file extensions to be ignored

The processing output will be printed in command line and also under the **_results/_**
directory these stats with the date, runtime arguments and configuration is saved

Currently, the analyzer supports more than 20 extensions. New types/languages
can be added to **_./config/known_types.json_** file

## Tests

Tests are placed in **_./tests_** folder.<br>
To run all: `pytest ./tests`

## Contribution
Contributions are welcome:
* Bug reports
* Ideas
* Bug fixes
* Feature additions
* New language descriptions
* New tests
* Documentation updates
* etc
