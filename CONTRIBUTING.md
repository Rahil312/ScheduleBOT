# Contributing to ScheduleBot ! 
Thank you for taking your time for learning how to contribute. Below are some general guidelines and practices that you should keep in mind when contributing to this repository.

We request you to please follow the Code of Conduct that we have created which is located here : https://github.com/SEProjGrp5/ScheduleBot/blob/main/CODE_OF_CONDUCT.md

## Before getting started
Give the following links a read to understand the working of the project and setting up the requirements

1. Check [README.md](https://github.com/SEProjGrp5/ScheduleBot/blob/main/README.md)
2. Check [requirements.txt](https://github.com/SEProjGrp5/ScheduleBot/blob/main/requirements.txt)

## Setting Up

### Get your Discord bot 

 Follow this [tutorial](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) to create your discord bot account.

### Token
  To "login" to your bot through our program, place a file named `config.py` in your src directory with the content:
  
  ```
  token = ************(your discord bot token)
  ```
  
### Intall required packages
  ```
  pip install -r requirements.txt
  ```
### Run the schedulebot.py
  ```
  python3 schedulebot.py
  ```
  Then your scheduleBot should start working.

## Ways to Contribute

### Report bugs
Report any issues you encounter while using or contributing to this repository as a new github issue, using the Bug tag. When reporting a bug please describe:
1. Any preconditions (your operating system, status of your data, files that the program may access, and if the program is running on an external drive)
2. Sequence of actions from the initial execution of the program to the bug.
3. Expected behavior (i.e. if the bug was not there).
4. Actual behavior (i.e. the effect of the bug).

### Suggest enhancements
Suggestions are very much welcome. If you have a suggestion for this project, please report it as a github issue, using the Feature Request tag, and provide the following information:

*	Use a clear and descriptive title for the issue to identify the problem.
*	Describe the exact steps which reproduce the problem in as many details as possible. Along with it, provide the details regarding the name and version of OS, Python version, configuration of the environment, if used any.
*	Provide specific examples to demonstrate the steps. Include links to files or GitHub projects, or copy/paste able snippets, which you use in those examples. If you're providing snippets in the issue, use Markdown code blocks.
*	Describe the behavior you observed after following the steps and point out what exactly is the problem with that behavior.
*	Explain which behavior you expected to see instead and why.
*	If the problem is related to performance or memory, include details of the errors encountered with your report.
*	Can you reliably reproduce the issue? If not, provide details about how often the problem happens and under which conditions it normally happens.

#### Before Submitting An Enhancement Suggestion
- Check the Debugging guide for the corresponding project and look for the enhancement that is already available. 
- Check the FAQs on the forum for a list of common questions and problems.
- Determine which repository the enhancement should be suggested in.
- Perform a cursory search to see if the enhancement has already been suggested. 

### Contribute code
We use git flow in this repo. If you want to contribute through code, please fork an existing branch to work on your feature. If you're working on a current issue, respond to that issue with "I'm working on this". When you are done, submit a pull request to join your contribution to the branch you forked. Before submiting your request, please:
- Implement functional, passing test cases that test your contribution
- Check that all previous test cases and other status checks are passing.

## Pull Requests<a name="requests"></a>
The process described here has several goals:
- Maintain the project’s quality
- Fix problems that are important to users
- Engage the community in working toward the best possible solution
- Enable a sustainable system for the project’s maintainers to review contributions

## Style guidelines
### Git commit
- Use present tense ("Add feature", not "Added feature")
- Use imperative mood ("Move cursor to...", not "Moves cursor to...")
- Keep the first line to once sentence.

### Python style guide
Please follow the [PEP8 guide](https://www.python.org/dev/peps/pep-0008/) for Python. In addition, please follow the following conventions:
- Use underscores to separate words in non class names: n_samples rather than nsamples.
- Use relative imports for code. For test cases, use absolute imports.
- Do not use import \*, as it has been discouraged by the [official Python recommendations](https://docs.python.org/3.1/howto/doanddont.html#at-module-level).

### Documentation
- Use pdoc3

### Contact Us:
In case there is some persistent bug, please feel free to contact group - 63
•	Rohan Mehul Champaneri - rchampa2@ncsu.edu
•	Rahil Hardik Shukla - rshukla7@ncsu.edu
•	Karan Shaunak Patel - kpatel49@ncsu.edu

