# List of prompts for the AI agnents

## Local Imports ##
# System imports
import os, sys
# Get CWD
CWD = os.path.dirname(os.path.realpath(__file__))
# Add the CWD to the path
sys.path.append(CWD)
# Local imports
import prompt_strs as db

def construct_context(role: str, version: str) -> str:
    """
    Construct the context text for the prompt.

    Parameters
    ----------
    role : str
        The role of the agent (proposer or responder)
    version : str
        The version of the experiment (e.g. human_ai_classic)
    """
    # Get the id
    id = f"{version}_{role}"

    # Add role
    context = db.characters[id]

    # Get the base context text
    context += db.instructions_page_one

    # Get the role-specificcontext text
    if role == "proposer":
        context += db.proposer_context
    elif role == "responder":
        context += db.responder_context
    else:
        raise ValueError(f"Invalid role: {role}")
    
    # Add the third page
    context += db.instructions_page_three

    # Add formatting
    if "human_ai" in version:
        context += db.formatting[f"human_ai_{role}"]
    elif "ai_ai" in version:
        context += db.formatting[f"ai_ai_{role}"]
    else:
        raise ValueError(f"Invalid version: {version}")

    return context

def format_prompt(role: str = "user", prompt_text: str = "") -> dict:
    """
    Format the prompt text for the OpenAI API. Used for priority messages.

    Parameters
    ----------
    role : str
        The role of the user generating the prompt (default is "user").
    prompt_text : str
        The text prompt to generate a response for.

    Returns
    -------
    dict
        The formatted prompt for the OpenAI API.

    Examples
    --------
    >>> response = agent.format_dev("Once upon a time")
    """
    # Gaurd against empty prompt text
    if not prompt_text:
        raise ValueError("Prompt text cannot be empty.")
    
    # Validate role
    role = role.lower()
    if role not in ["user", "developer", "assistant"]:
        raise ValueError(f"Invalid role: {role}")
    
    # Format the prompt based on the role
    message = {
        "role": role,
        "content": [
            {
                "type": "text",
                "text": prompt_text
            }
        ]
    }
    return message

if __name__ == "__main__":
    print(construct_context("proposer", "human_ai_classic"))
    # print(construct_context("responder", "human_ai_classic"))
    # print(format_prompt("user", "What is the meaning of life?"))
