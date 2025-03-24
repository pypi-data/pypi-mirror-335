# Command line interface for the package

# System imports
import os, sys, subprocess
import chromedriver_autoinstaller
# Get CWD
CWD = os.path.dirname(os.path.realpath(__file__))
# Add the CWD to the path
sys.path.append(CWD)

# Package imports
import experiment as exp # multi round ultimatum game
import parser # for log parsing

# For package version
import pkg_resources

# Define repository details
log_dir = f"{os.path.expanduser('~')}/econ-llm-data"

def upload():
    """
    Upload the results to the remote repository.
    """
    # Read the user's name and access token from secrets.txt
    with open("secrets.txt", "r") as f:
        _ = f.readline().strip()
        username, token = f.readline().strip().split(" ")
    # Define the remote repository URL
    remote_url = f"https://{username}:{token}@github.com/JawandS/econ-llm-data.git"

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_dir):
        print("Creating logs directory.")
        os.makedirs(log_dir)
    # Initialize the repository if it doesn't exist
    if not os.path.exists(os.path.join(log_dir, ".git")):
        print("Initializing repository.")
        subprocess.run(["git", "init"], cwd=log_dir, check=True)
    # Add the remote url if it doesn't exist already
    remotes = subprocess.run(["git", "remote"], cwd=log_dir, capture_output=True, text=True, check=True).stdout.splitlines()
    if "origin" not in remotes:
        print("Adding remote.")
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=log_dir, check=True)
    
    # Pull the latest changes from the remote repository
    print("Pulling changes.")
    subprocess.run(["git", "pull", "origin", "master"], cwd=log_dir, check=True)
    # Add change (if any)
    untracked_flag = subprocess.run(["git", "status", "--porcelain"], cwd=log_dir, capture_output=True, text=True, check=True).stdout.strip()
    if untracked_flag:
        # Add the changes
        subprocess.run(["git", "add", "."], cwd=log_dir, check=True)
        # Commit the changes
        subprocess.run(["git", "commit", "-m", "Upload results"], cwd=log_dir, check=True)
        # Push the changes to the remote repository
        subprocess.run(["git", "push", "-u", "origin", "master"], cwd=log_dir, check=True)
        # Print a success message
        print("Results uploaded successfully.")
    else:
        print("No changes to upload.")

def main(args: list = []):
    """
    Interpert the command line arguments. Commands:
    - upload: upload the results to the server
    - upgrade: upgrade the package
    - run: (default) run the multi-round ultimatum game experiment. 
        - Arguments: [experiment_name] [user_id] (default: xaty1 agent)
    """
    # Automatically install the latest version of chromedriver
    chromedriver_autoinstaller.install()

    # Check for args
    if not args:
        args = sys.argv[1:]
        print(F"Using command line arguments: {args}")

    # Check if the user provided the correct number of arguments
    if len(args) == 0:
        print("No commands found. Use one of the following commands: upload, upgrade, run, parse")
        return -1
    
    command = args[0]
    if command == "upload": # upload the results to the server
        print("Results upload started")
        upload()
    elif command in ["-v", "--version", "version"]:
        # print the version number
        print(f"Version: {pkg_resources.get_distribution('econ-llm').version}")
    elif command in ["upgrade", "update"]:
        print("Upgrading the package")
        # try to run the build script
        subprocess.run(["pip", "install", "--upgrade", "econ-llm"], check=True)
    elif command in ["parse", "visualize"]:
        # Parse the results
        print("Parsing the results.")
        data = parser.parse(args[1:])
        print(f"{len(data)} logs found.")
        # Visualize the results
        print("Visualizing the results.")
        fp = parser.visualize(data)
        print(f"Results stored in {fp}")
        # Check the conversation
        print("Checking the conversation.")
        fp = parser.check_conversation(data)
        print(f"Results stored in {fp}")
    elif command in ["download", "fetch", "veconlab"]:
        # get data from veconlab results
        print("Fetching data from VeconLab.")
        exp.pull_veconlab_data(session_id=args[1], password=args[2])
        print("Data fetched.")
    elif command == "setup":
        # run the setup script
        print("Please run setup script (found in respository).")
    elif command == "run":
        # Pull the latest changes from the remote repository
        print("Updating logs.")
        try:
            upload()
        except:
            print("Error updating logs, continuing with execution.")
        # Run the experiment
        print(f"Running with arguments: {args}")
        # check if version number provided
        if len(args) < 4:
            print("No version provided. Using default version (human_ai_classic).")
            exp.run_experiment(session_id=args[1], user_id=args[2])
        else:
            exp.run_experiment(session_id=args[1], user_id=args[2], version=args[3])
        # Check if the user wants to upload the results
        try:
            print("Results upload started")
            upload()
        except:
            print("Error uploading results, exiting.")
    elif command in ["help", "info", "-h", "--help"]:
        help_string = """
        Commands: 
        - upload: upload the results to the server
        - upgrade: upgrade the package
        - run: run the multi-round ultimatum game experiment. 
            - Arguments: [experiment_name] [user_id] [(optional) experiment_version (default: human_ai_classic)]
            - The proposer/responder is automatically detected on VeconLab
        - parse: parse the results and visualize them
        """
        print(help_string)
    else:
        print(f"Invalid command {command}. Use one of the following commands: upload, upgrade, run, parse")
        return -1

if __name__ == "__main__":
    main(["run", "xaty1", "agent", False]) # default experiment and user_id
