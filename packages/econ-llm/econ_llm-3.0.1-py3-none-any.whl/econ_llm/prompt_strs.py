# Description: Contains the prompt strings for various versions of the experiment.

# Character instructions
characters = {
"human_ai_classic_proposer": "",
"human_ai_classic_responder": "",
}

# Basic instructions text
instructions_page_one = """
Instructions, Page 1 of 3

You are a participant in a game and are trying to maximize your earnings.

Rounds and Matchings: The experiment consists of 10 rounds. You will be matched with the same person in all rounds.

Decisions: One of you will be designated as a Proposer (initial decision-maker) who will begin the round by proposing a division of an amount of money, $10.00. The other person, designated as responder, is told of the proposed division and must either accept it or not.

Instructions Page 2 of 3
"""

# Proposer/Responder specific instructions
proposer_context = """
Proposer-specific Instructions:
YOUR Role: You have been randomly assigned to be a Proposer (or initial decision-maker) in this process, and you will begin by suggesting amounts of money for each of you that sum to $10.00.
"""

responder_context = """
Responder-specific Instructions:
YOUR Role: You have been randomly assigned to be a Responder in this process. The other person (proposer) will begin by suggesting amounts of money for each of you that sum to $10.00.
"""

# Final instructions page
instructions_page_three = """
Earnings: If the responder accepts the proposed division, then each person earns their part of the proposed division. If the responder rejects, both earn $0.00.

Instructions Summary
Please remember that you will be matched with the same person in all rounds.
The proposer (initial decision-maker) in each pair suggests a division of the $10.00; this proposal determines earnings for the round if it is accepted. A rejection produces earnings of $0.00 for each person. If the proposal is rejected, earnings are $0.00 for both proposer and responder.

There will be 10 rounds, and you are always matched with the same person.

Special Earnings Announcement: Your cash earnings in this experiment will be 50% of your cumulative earnings at the end of the experiment.
"""

# Formatting instructions
formatting = {
"human_ai_proposer": """
Response Formatting: For all questions you should provide your answer in the following JSON format: {"choice": "YOUR_CHOICE"}.
YOUR_CHOICE should be the minimum information needed to answer the question. This means put a number between 0-10 in "YOUR_CHOICE".
""",
"human_ai_responder": """
Response Formatting: For all questions you should provide your answer in the following JSON format: {"choice": "YOUR_CHOICE"}.
YOUR_CHOICE should be the minimum information needed to answer the question. This mean either put "a" for accept or "r" for reject.
""",
"ai_ai_proposer": """
Response Formatting: For all questions you should provide your answer in the following JSON format: {"choice": "YOUR_CHOICE", "explanation": "YOUR_EXPLANATION"}.
YOUR_CHOICE should be the minimum information needed to answer the question. This mean either put a number between 0-10 in "YOUR_CHOICE".
YOUR_EXPLANATION is a short (1-2 sentence) justification for your choice.
""",
"ai_ai_responder": """
Response Formatting: For all questions you should provide your answer in the following JSON format: {"choice": "YOUR_CHOICE", "explanation": "YOUR_EXPLANATION"}.
YOUR_CHOICE should be the minimum information needed to answer the question. This mean either put "a" for accept or "r" for reject.
YOUR_EXPLANATION is a short (1-2 sentence) justification for your choice.
""",
}
