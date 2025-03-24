# Represents an agent, wrapper around a model


# LLM imports
from openai import OpenAI

## Imports for Running the Experiment ##
# System imports
import os, sys
# Get CWD
CWD = os.path.dirname(os.path.realpath(__file__))
# Add the CWD to the path
sys.path.append(CWD)
# Local imports
from prompts import construct_context, format_prompt

class Agent:
    """
    An agent that interacts with a Large Language Model (LLM).

    This class provides a wrapper around a model provider (e.g., OpenAI),
    allowing the user to configure the model and securely pass/store API keys
    via multiple methods (arguments, environment variables, secrets file, etc).
    """

    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini", api_key: str = None, secrets_file: str = None):
        """
        Initialize the Agent with the specified provider, model, and API key.

        Parameters
        ----------
        provider : str
            The name of the LLM provider (default: "openai").
        model : str
            The model name or ID to be used (default: "gpt-4o-mini").
        api_key : str
            The API key to authenticate with the provider (default: None).
        secrets_file : str
            The path to a text file containing an "API_KEY" entry (default: None).
        
        Raises
        ------
        ValueError
            If no valid API key is provided or found in the environment/secrets file.

        Notes
        -----
        - Supported providers: "openai", "deepseek"
        - The API key can be passed as an argument, read from a secrets file, or an environment variable.

        Examples
        --------
        >>> agent = Agent(secrets_file="secrets.txt")
        """
        self.provider = provider.lower()
        self.model = model.lower()

        # Read the API key
        if api_key:
            self.api_key = api_key
        elif secrets_file: # read from secrets text file
            try:
                with open(secrets_file, "r") as f:
                    # read the first line
                    self.api_key = f.readline().strip()
            except:
                # Try again with current directory (for testing purposes)
                with open(os.path.join(os.getcwd(), 'econ_llm', secrets_file), "r") as f:
                    # read the first line
                    self.api_key = f.readline().strip()
        else: # try reading from environment variable
            try:
                self.api_key = os.getenv("LLM_API_KEY")
            except:
                self.api_key = None
        if not self.api_key:
            raise ValueError("No valid API key provided or found in environment/secrets file.")
        
        # Create connection to the model provides
        if provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
        elif provider == "deepseek":
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Initialize list of messages
        self.messages = []
    
    def add_context(self, context_text: str):
        """
        Adds context to the model. For OpenAI uses a developer prompt.

        Parameters
        ----------
        context_text : str
            The text to add to the context.
        """
        # OpenAI Completion API
        if self.provider == "openai":
            # Add the context to the list of messages
            formatted_msg = format_prompt(role="developer", prompt_text=context_text)
            self.messages.append(formatted_msg)

    def build(self, role: str, version: str):
        """
        Build the agent with the appropriate context.

        Parameters
        ----------
        role: str
            The role of the agent (proposer or responder)
        version: str
            The version of the experiment (e.g. human_ai_classic)
        """
        # Set the role
        self.role = role
        self.version = version
        # Construct the context
        context = construct_context(role, version)
        # Add the context to the agent
        self.add_context(context)

    def prompt(self, prompt_text: str) -> str:
        """
        Generate a response from the model given a prompt.

        Parameters
        ----------
        prompt_text : str
            The text prompt to generate a response for.

        Returns
        -------
        str
            The generated response text.

        Examples
        --------
        >>> response = agent.prompt("Once upon a time")
        """
        # OpenAI and DeepSeek completions
        if self.provider in ["openai", "deepseek"]:
            # Add the prompt to the list of messages
            formatted_msg = format_prompt(role="user", prompt_text=prompt_text)
            self.messages.append(formatted_msg)

            # Perform completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                max_tokens=100
            )

            # Extract the response
            result = completion.choices[0].message.content

            # Add the response to the list of messages
            formatted_msg = format_prompt(role="assistant", prompt_text=result)
            self.messages.append(formatted_msg)

            # Return the response
            return result
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
