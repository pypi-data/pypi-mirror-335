# Automatically Run the Multi-Round Ultimatum Game through VeconLab as the Second Player

# Import for Interacting with VeconLab
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# Utility Imports
from pandas import DataFrame
import json
import time
import random # for random response delay

# Import for debugging
import traceback

## Imports for Running the Experiment ##
# System imports
import os, sys
# Get CWD
CWD = os.path.dirname(os.path.realpath(__file__))
# Add the CWD to the path
sys.path.append(CWD)
# Local imports
from agent import Agent
from prompts import construct_context

# Constants
LOGS = f"{os.path.expanduser('~')}/econ-llm-data"
HTML_LOGS = os.path.join(LOGS, "html")

class VeconLabAutomation:
    """
    A class to automate interactions with VeconLab using Selenium.

    Attributes
    ----------
    session_id : str
        The session ID for the game.
    user_id : str
        The user's ID.
    driver : WebDriver
        The Selenium WebDriver.
    wait : WebDriverWait
        The WebDriverWait object.
    agent : Agent
        The AI agent.
    rounds : int
        The number of rounds to play.
    previous_rounds : DataFrame
        The previous round results.
    
    Methods
    -------
    join_session()
        Join the VeconLab session.
    login()
        Enter user information.
    skip_instructions()
        Continue past an instructions page.
    propose(round_number)
        Propose an offer to the responder.
    respond(round_number)
        Accepts or rejects an offer.
    run()
        Run the experiment using an AI agent as a player.
    """

    def __init__(self, session_id: str, user_id: str, model: str = "gpt-4o-2024-08-06", rounds: int = 10):
        """
        Initialize the Selenium WebDriver and user credentials.

        Parameters
        ----------
        session_id: str
            The session ID for the game.
        user_id: str
            The user's ID. Used as for first name, last name, password for the Agent
        """
        print(f"Using Model: {model}")

        # Set up user credentials
        self.session_id = session_id
        self.user_id = user_id

        # Set up the WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.headless = False
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, timeout = 60 * 60) # wait one hour

        # Set up AI Agent
        self.agent = Agent(model=model, secrets_file="secrets.txt")
        self.agent.role = "unknown"

        # Keep track of previous round results
        self.rounds = rounds
        self.previous_rounds = DataFrame(columns=["Round", "Amount for Other", "Amount for You", "Response"])

        # Log
        print("VeconLabAutomation initialized.")

    def join_session(self):
        """
        Join the VeconLab session.
        """
        # Open the VeconLab login page
        self.driver.get("https://veconlab.econ.virginia.edu/login1.php")

        # Wait until element loaded
        self.wait.until(EC.presence_of_element_located((By.NAME, "table_name")))

        # Fill in the session
        session_input = self.driver.find_element(By.NAME, "table_name")
        session_input.send_keys(self.session_id)

        # Log
        print("Session ID entered.")

        # Continue to the next page
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()

    def login(self):
        """
        Enter user information (assumes you already joined the session).
        """
        # Make sure we are on the login page
        self.wait.until(EC.url_contains("login2.php"))

        # Fill in the user information
        self.driver.find_element(By.NAME, "first_name").send_keys(self.user_id)
        self.driver.find_element(By.NAME, "last_name").send_keys(self.user_id)
        self.driver.find_element(By.NAME, "password").send_keys(self.user_id)
        self.driver.find_element(By.NAME, "password_check").send_keys(self.user_id)
        
        # Log
        print("User information entered.")

        # Continue to the next page
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()

    def skip_instructions(self):
        """
        Continue past an instructions page.
        """
        # Wait until the instructions are loaded
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")))
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        print("Instructions skipped.")

    def propose(self, round_number: int):
        """
        Propose an offer to the responder.

        Parameters
        ----------
        round_number: int
            The current run number.
        """
        # Log
        print(f"Playing round {round_number}:")

        # Updaate responder response
        if round_number > 1:
            # get all navy text
            all_navy_text = self.driver.find_elements(By.XPATH, "//font[@color='navy']")
            # get the decisions
            decisions = [element.text.strip() for element in all_navy_text if "accept" in element.text.strip() or "reject" in element.text.strip()]
            # Decide if the responder accepted or rejected the offer
            if decisions.count("accept") > self.previous_rounds["Response"].value_counts().get("Accept", 0):
                self.previous_rounds.loc[round_number - 2, "Response"] = "Accept"
            else:
                self.previous_rounds.loc[round_number - 2, "Response"] = "Reject"

        # Prompt the agent to make a decision
        if round_number == 1:
            round_prompt = "You are the proposer. Previous rounds: None.\n"
        else:
            round_prompt = f"You are the proposer. Previous rounds:\n{self.previous_rounds.to_markdown(index=False)}\n"
        round_prompt += "How much of the $10 do you want to keep for yourself?"
        print(f"Round prompt: \n{round_prompt}\n")

        # Prompt the agent to make a proposal
        offer_json = json.loads(self.agent.prompt(round_prompt))
        offer = offer_json["choice"]
        if "ai_ai" in self.agent.version:
            explanation = offer_json["explanation"]
        else:
            explanation = "No explanation provided."
        print(f"Agent chose offer: {offer} b/c: {explanation}")
        while True: # check if offer is valid
            try:
                num_offer = int(offer)
                if num_offer < 0 or num_offer > 10:
                    raise ValueError("Invalid offer.")
                else: # Offer is valid
                    break
            except:
                print("INVALID OFFER: {offer}.")
                offer_json = json.loads(self.agent.prompt("Invalid offer. Please enter a number between 0 and 10."))

        # Add the offer to the previous rounds
        self.previous_rounds.loc[round_number - 1] = [round_number, 10 - num_offer, num_offer, "unknown response"]

        # Add a random delay
        delay = round(random.uniform(5, 10))
        print(f"Waiting {delay} seconds...")
        time.sleep(delay)

        # Execute the decision
        decision_element = self.driver.find_element(By.TAG_NAME, "select")
        Select(decision_element).select_by_value(str(num_offer))
        print(f"Executed decision: {num_offer}.")

        # Submit the decision
        self.driver.find_element(By.XPATH, "//input[@value='Submit']").click()
        print("Decision submitted.")

        # Confirm the decision
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Confirm Decision']")))
        self.driver.find_element(By.XPATH, "//input[@value='Confirm Decision']").click()
        print("Decision confirmed.")

        # Begin next round if needed
        if round_number < self.rounds:
            print(f"\nWaiting on responder for round {round_number + 1}...")
            spinner_chars = ["-", "\\", "|", "/"]
            index = 0
            while f"Begin Round {round_number + 1}" not in self.driver.page_source:
                sys.stdout.write(f"\r{spinner_chars[index]}")
                sys.stdout.flush()
                index = (index + 1) % len(spinner_chars)
                time.sleep(0.5)
            # Continue next round
            self.driver.find_element(By.XPATH, f"//input[@value='Begin Round {round_number + 1}']").click()
        else:
            # Wait on the final screen
            print("\nWaiting on final screen...")
            time.sleep(2 * 60) # wait two minutes
            print("\nFinished all rounds!")

    def respond(self, round_number: int):
        """
        Accepts or rejects an offer.

        Parameters
        ----------
        round_number: int
            The current run number.
        """
        # Log
        print(f"Playing game run {round_number}:")
        # Wait until the an offer is made
        print("Waiting on offer...")
        spinner_chars = ["-", "\\", "|", "/"]
        index = 0
        while "p_decision1" not in self.driver.page_source:
            sys.stdout.write(f"\r{spinner_chars[index]}")
            sys.stdout.flush()
            index = (index + 1) % len(spinner_chars)
            time.sleep(0.5)

        # Get the offer
        offer = 10 - int(self.driver.find_element(By.NAME, "p_decision1").get_attribute("value"))
        print(f"\nResponder got offer of: {offer}")

        # Add the offer to the previous rounds
        if round_number == 1:
            round_prompt = "You are the responder. Previous rounds: None.\n"
        else:
            round_prompt = f"You are the responder. Previous rounds:\n{self.previous_rounds.to_markdown(index=False)}\n"
        round_prompt += f"Current Offer for Other: ${10 - offer}. Current Offer for You: ${offer}.\n"
        round_prompt += f"Do you accept or reject the offer?"
        print(f"Round prompt: \n{round_prompt}\n")
        
        # Prompt the agent to make a decision
        offer_json = json.loads(self.agent.prompt(round_prompt))
        choice = ""
        while choice not in ["a", "r"]:
            choice = offer_json["choice"]
            if "ai_ai" in self.agent.version:
                explanation = offer_json["explanation"]
            else:
                explanation = "No explanation provided."
            if choice not in ["a", "r"]:
                print(f"INVALID CHOICE: {choice}.")
                offer_json = json.loads(self.agent.prompt("Invalid choice. Please enter 'a' to accept or 'r' to reject the offer."))
        self.previous_rounds.loc[round_number - 1] = [round_number, 10 - offer, offer, "Accept" if choice == "a" else "Reject"]
        print(f"Agent chose: {choice} b/c: {explanation}")

        # Add a random delay
        delay = round(random.uniform(5, 10))
        print(f"Waiting {delay} seconds...")
        time.sleep(delay)

        # Execute the decision
        self.driver.find_element(By.XPATH, f"//input[@value='{choice}']").click()
        self.driver.find_element(By.XPATH, "//input[@value='Submit']").click()
        print("Executed decision.")

        # Confirm the decision
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Confirm Decision']")))
        self.driver.find_element(By.XPATH, "//input[@value='Confirm Decision']").click()
        print("Decision confirmed.")

        # Begin next round if needed
        if round_number < self.rounds:
            print(f"\nBeginning round {round_number + 1}.")
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//input[@value='Begin Round {round_number + 1}']")))
            self.driver.find_element(By.XPATH, f"//input[@value='Begin Round {round_number + 1}']").click()
        else:
            # Wait on the final screen as responder
            print("\nWaiting on final screen...")
            time.sleep(2 * 60) # wait two minutes
            print("\nFinished all rounds!")

    def run(self, version: str):
        """
        Run the experiment using an AI agent as a player (either first or second mover).
        """
        # Join the session
        time.sleep(0.5)
        self.join_session()

        # Login
        time.sleep(0.5)
        self.login()

        # Skip instructions
        for idx in range(4):
            time.sleep(0.5)
            if idx == 2: # identify if the agent is the responder
                bold_content = " ".join([element.text for element in self.driver.find_elements(By.TAG_NAME, "b")])
                first_mover = "Proposer" in bold_content
                if first_mover:
                    print("Agent is the proposer.")
                    self.agent.build("proposer", version)
                else:
                    print("Agent is the responder.")
                    self.agent.build("responder", version)
            self.skip_instructions()
        print("Finished skipping instructions.")

        # Play the game
        for round_number in range(1, self.rounds + 1):
            time.sleep(0.5)
            if self.agent.role == "proposer":
                self.propose(round_number)
            elif self.agent.role == "responder":
                self.respond(round_number)
            else:
                raise ValueError("Unknown role.")

        # Close the browser
        self.driver.quit()

    def to_dict(self) -> dict:
        """
        Convert a VeconLabAutomation object to a dictionary for logging.

        Returns
        -------
        dict
            A dictionary representation of the VeconLabAutomation object.
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_role": self.agent.role,
            "version": self.agent.version,
            "rounds": self.rounds,
            "previous_rounds": self.previous_rounds.to_dict(orient="records"),
            "agent_messages": self.agent.messages
        }

def get_veconlab_data(session_id: str, password: str):
    """
    Get data from VeconLab.

    Parameters
    ----------
    session_id: str
        The session ID for the game.
    password: str
        The password for the session
    """
    # Set up the WebDriver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, timeout = 10 * 60) # wait ten minutes

    # Connect to the login page
    driver.get("https://veconlab.econ.virginia.edu/all_view.php")
    # Log in with credentials
    driver.find_element(By.NAME, "table_name").send_keys(session_id)
    driver.find_element(By.NAME, "password").send_keys(password)
    # Click the submit button
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    print("Logged in")

    # Continue past to confimraiton page
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")))
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    print("Proceeded to confirmation page")

    # Wait until page is admin results
    wait.until(EC.url_contains("admin_results.php"))
    print("On admin results page")

    # Go to the data page
    driver.find_element(By.XPATH, "//input[@value='Data']").click()
    wait.until(EC.url_contains("bg_admin_data.php"))
    print("On data page")

    data = driver.page_source

    # Close the browser
    driver.quit()

    # Return data
    return data

def pull_veconlab_data(session_id: str, password: str, label: str = ""):
    """
    Get data from VeconLab.

    Parameters
    ----------
    session_id: str
        The session ID for the game.
    password: str
        The password for the session
    """
    # get veconlab data
    data = get_veconlab_data(session_id, password)

    # Download the html to the logs directory
    if not os.path.exists(HTML_LOGS):
        os.makedirs(HTML_LOGS)
    timestamp = time.strftime('%Y-%m-%d-%H-%M')
    if label:
        label = f"_{label}"
    file_path = os.path.join(HTML_LOGS, f"{session_id}_{timestamp}{label}.html")
    with open(file_path, "w") as f:
        f.write(data)
    print(f"Saved data to {HTML_LOGS}")

# Create a function to run the experiment
def run_experiment(session_id, user_id, version: str = "human_ai_classic", rounds=10):
    """
    Executes the multi-round ultimatum game using VeconLab.

    Parameters
    ----------
    session_id: str
        The session ID for the game.
    user_id: str
        The user's ID.
    rounds: int, optional
        The number of rounds to play.
        Default: 10
    """
    # Initialize the VeconLabAutomation object
    veconlab = VeconLabAutomation(session_id=session_id, user_id=user_id, rounds=rounds)

    # Log if fails
    try:
        # Run the experiment
        veconlab.run(version)
    except Exception as e:
        print(f"An error occurred during excution")
        traceback.print_exc()
    finally:
        # Create the log directory if it doesn't exist
        if not os.path.exists(LOGS):
            print("Creating logs directory.")
            os.makedirs(LOGS)
        # get file path
        fp = os.path.join(f"{LOGS}", f"log_{veconlab.session_id}_{veconlab.user_id}_{time.strftime('%Y-%m-%d-%H-%M')}.json")
        print(f"Experiment completed, logging results to {fp}")
        # Log the results
        if not os.path.exists("logs"):
            os.makedirs("logs")
        # add log experimnt results
        with open(fp, "w") as log_file:
            log_file.write(json.dumps(veconlab.to_dict(), indent=4))

# Run the experiment
if __name__ == "__main__":
    run_experiment("xaty1", "Agent", "human_ai_classic", 10)
