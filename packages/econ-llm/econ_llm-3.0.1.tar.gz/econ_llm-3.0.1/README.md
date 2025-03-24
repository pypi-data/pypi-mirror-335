# econ-llm
A python package that uses LLM agents to automate experiments using the VEcon Lab Website.

## Installation
To install the package, run the following command:
```bash
pip install econ-llm
```

## Dependencies
### Python Dependeny
```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
```
### secrets.txt
```text
OpenAI_API_KEY
GitHub_Username GitHub_Access_Token
```

`secrets.txt` should be in the same directory as execution.

### Upload
Assumes git credentials are set
```bash
git config --global user.email "YOUR_EMAIL"
git config --global user.name "YOUR_NAME"
git config pull.rebase true
```

## Commands
### Run
To run an experiment (multi-round ultimatum game), use the following command:
```bash
econ-llm run [experiment_id] [user_id] [(optional) experiment_version]
```
The agent automatically detects if it is a proposer or responder. Versions supported:
- "human_ai_classic": (default) matches instructions given to humans

### Upload
Upload output to `econ-llm-data` using the following command:
```bash
econ-llm upload
```

### Visualize
Visualize the output using the following command:
```bash
econ-llm visualize [filter one] [filter two] ...
```
Filters are used to select the data to visualize. For example, to select logs from a specific user on a specific day, use the following command:
```bash
econ-llm visualize [user_id] [yyyy-mm-dd]
```
`parse` can also be used in place of `visualize`. Both commands produce in the conversation in a readable format.

### Upgrade
To update the package, use the following command:
```bash
econ-llm upgrade
```

### Download
To get data from VeconLab, use the following command:
```bash
econ-llm download [session_id] [admin_password]
```

## Suggested Process Flow
Add agents as needed:
```bash
econ-llm run [experiment_id] [user_id]
```
Visualize the data:
```bash
econ-llm visualize
```
Get the data from VeconLab:
```bash
econ-llm download [session_id] [admin_password]
```
Make sure data is uploaded:
```bash
econ-llm upload
```

## Output
The output will be saved in the `~/econ-llm-data` directory. File names contains experiment_id, user_id, and timestamp. Metadata includes the previous and the role of the agent.

## Specification
The package is currently using `gpt-4o-2024-08-06` as the model from OpenAI.

## Change Log
### Version 3.X.X - critical fix for the proposer history
NOTE: running proposer in version previous to this will not produce valid results.
- 3.0.1
    - Update proposer history to correctly track value for you/other

### Version 2.X.X - production release
### Version 2.0.X
- 2.0.7
    - Add delay for the responder on the final page
    - Update data pull from VeconLab
- 2.0.6
    - Make sure it runs in visible mode
    - Add a delay for the proposer on the final page
- 2.0.5
    - Stable version for experiments
- 2.0.4
    - Add a 5-10 second random delay before sending a message
- 2.0.3
    - Remove misleading version after upgrade
- 2.0.2
    - Add `version` command to check the version of the package
    - Fix issues with git initialization
- 2.0.1
    - Stable version used for AI-responder experiments

### Version 1.X.X

### Version 1.2.X - bug fix with proposer
- 1.2.6
    - Update logs before running experiment
- 1.2.5
    - Add `download` command to get data from VeconLab
- 1.2.4
    - Fix typo with '%%'
- 1.2.3
    - Add a parse command to make the conversations human readable
    - Use markdown for past results
- 1.2.2
    - Update how context is built/stored
    - Critical fixes to the context for proposer/responder
- 1.2.1
    - Fix bug with the proposer not getting all information
    - Add delays in interactions
    - Add spinner when proposer is waiting on a response

#### Version 1.1.X
- 1.1.3:
    - Add visualizer command
- 1.1.2: 
    - Update logging structure
    - Add log parsing
    - Auality of life improvements 
        - Use aboslute import paths
        - Better argument parsing
- 1.1.1: 
    - Initial prototype release
