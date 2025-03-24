# Parse the logs from experiment runs

# System imports
import os, subprocess, time
# Parsing imports
import json
# Visualizing imports
import matplotlib.pyplot as plt

# Log directory
LOGS = f"{os.path.expanduser('~')}/econ-llm-data"
VISUALS = f"{os.path.expanduser('~')}/econ-llm-data/visuals"
CONVERSATIONS = f"{os.path.expanduser('~')}/econ-llm-data/conversations"

def parse(filters = []):
    """
    Parse the logs from experiment runs.

    Parameters
    ----------
    session_id : str, optional
        The experiment ID.
    user_id : str, optional
        The user ID.
    timestamp : str, optional
        The timestamp (yyyy-mm-dd-hh), 24 hours hour format.
    
    Notes
    -----
    - For all parameters, the default value means match any value.
    """
    # Get the relevant logs
    logs = []
    for log in os.listdir(LOGS):
        # Check if the log matches requirements
        add_flag = True
        if '.json' not in log:
            add_flag = False
        for filter in filters:
            if filter not in log:
                add_flag = False
        if add_flag:
            logs.append(log)
    
    # Parse the logs
    data = {}
    for log in logs:
        with open(os.path.join(LOGS, log), "r") as f:
            data[log] = json.load(f)
    
    # Print
    print(f"Found {len(logs)} logs.")
    # Return the parsed data
    return data

def visualize(data: dict):
    """
    Visualize the parsed data.

    Parameters
    ----------
    data : dict
        The parsed data from the logs.
    """
    # Create plot
    fig, ax = plt.subplots()

    # Go through each log
    for log in data:
        agent_data = data[log]
        if agent_data["agent_role"] == "responder":
            # Parse the rounds
            rounds = {elem["Round"]: elem["Amount for You"] for elem in agent_data["previous_rounds"]}
            # Make 'Accept' green and 'Reject' red
            colors = ["g" if elem["Response"] == "Accept" else "r" for elem in agent_data["previous_rounds"]]
            # Plot the rounds
            label_vals = log.split(".")[0].split("_")[1:]
            label_val = f"{label_vals[0]} {'_'.join(label_vals[1: -1])} {label_vals[-1]}"
            ax.scatter(rounds.keys(), rounds.values(), c=colors)
            ax.plot(rounds.keys(), rounds.values(), label=label_val)

    # Make sure axes have all values
    ax.set_xticks(range(1, 11))
    ax.set_yticks(range(0, 11))
    # Add labels
    ax.set_xlabel("Round")
    ax.set_ylabel("Offer for Responder")
    ax.set_title("Interaction by Round")
    ax.legend()

    # Get current timestamp
    timestamp = time.strftime('%Y-%m-%d-%H-%M')
    # Save the plot
    fp = os.path.join(VISUALS, f"visual_{timestamp}.png")
    plt.savefig(fp)

    # Close the plot
    plt.close()
    # return the filepath
    return fp

def check_conversation(data: dict):
    """
    Check the conversation for the responder.

    Parameters
    ----------
    data : dict
        The conversation data.
    """
    # Open a log
    for log_name in data:
        fn = log_name.replace(".json", ".txt")
        with open(os.path.join(CONVERSATIONS, f"convo_{fn}"), "w") as f:
            # Go through messages
            for message in data[log_name]["agent_messages"]:
                f.write(f"{message['content'][0]['text']}\n")
    
    # Return filepath
    return CONVERSATIONS

def analyzer(data):
    """
    Analyze the data for patterns.

    Parameters
    ----------
    data : dict
        The parsed data from the logs.
    """
    # track all acceptions rejection count
    offers = {} # {offer: [accepts, rejections]}

    # go through logs
    for log in data:
        agent_data = data[log]
        if agent_data["agent_role"] == "responder":
            # Parse the rounds
            for round in agent_data["previous_rounds"]:
                offer = round["Amount for You"]
                response = round["Response"]
                if offer not in offers:
                    offers[offer] = [0, 0]
                if response == "Accept":
                    offers[offer][0] += 1
                else:
                    offers[offer][1] += 1
    
    # Print the offers
    total = 0
    print("Responder Statistics:")
    for offer in range(0, 11):
        if offer in offers:
            sub_total = offers[offer][0] + offers[offer][1]
            print(f"Offer: {offer}, Accept: {(offers[offer][0] / sub_total * 100):.2f}%, {offers[offer][0]}/{sub_total}")
            total += sub_total
    print(f"Total: {total}")

if __name__ == '__main__':
    # Pull data from the remote repository
    subprocess.run(["git", "pull", "origin", "master"], cwd=LOGS, check=True)
    # Parse the logs
    data = parse(["lra10", "2025-02-06-14"])
    # Visualize the data
    # visualize(data)
    # Analyze the data
    analyzer(data)