import random
import functools
import time
import pytest

# --- Keywords and Responses for Reaffirmation ---
POSITIVE_KEYWORDS = [
    "good", "great", "awesome", "fantastic", "encourage", "please", "reassure",
    "happy", "love", "amazing", "cheer", "brilliant", "incredible", "impressive",
    "you can", "keep going", "don't give up", "the best", "well done",
    "excellent", "super", "keep it up", "fantabulous", "rock on", "outstanding",
    "spectacular", "marvelous", "inspired", "motivated", "unstoppable", "champion",
    "you got this", "you can", "go for it", "believe in yourself", "wonderful", "positive", "energy",
    "believe", "the best", "keep it up"
]

POSITIVE_RESPONSES = [
    "Yay! Your positivity fuels me! Let's get this done!",
    "Thanks for the encouragement! I'm ready to run!",
    "With such positive vibes, I'm unstoppable!"
]

DEFAULT_RESPONSES = [
    "I don't wanna do it unless you encourage me...",
    "Maybe if you cheer me up, I'll consider it.",
    "I need some encouragement before I start.",
]

# Responses for Excuse Function

EXCUSE_INIT_MESSAGE = ["Alright, let's get started!", "Preparing to output solution...", 
                         "Optimizing best possible answer"]
EXCUSE_MESSAGE = [
            "Almost done! Just need a little more time...", 
            "Wait, I just realized there's a better way to do this... let me rethink everything.",
            "Someone just deleted my work... I need to start over again..."
        ]

EXCUSE_END_MESSAGE = ["Ok done!", "TBH... forget this I'll do it tomorrow."]

# --- Decorator to Require Positive Input ---
def require_positive_input(func):
    """
    Decorator that checks if the user's input message contains any positive keywords.
    If a positive keyword is found, it prints an encouraging message and allows the function to run. 
    Otherwise, it prints a default message and skips function execution.
    """
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in POSITIVE_KEYWORDS):
            positive_reply = random.choice(POSITIVE_RESPONSES)
            print(positive_reply)
            return func(message, *args, **kwargs)
        else:
            default_reply = random.choice(DEFAULT_RESPONSES)
            print(default_reply)
            return None
    return wrapper

@require_positive_input
def reaffirm_program(message):
    """
    Reaffirms the program and signals readiness to run after receiving a positive message.
    
    Args:
        message (str): The input message from the user.
        
    Returns:
        str: A message indicating that the program is now running.
    """
    return "Program is now running! Let's do this!"

# --- Decorator: Excuse Wrapper ---
def excuse_wrapper(func):
    """
    Decorator that prints a series of messages to simulate a delayed or distracted execution.
    Depending on a random result, it either proceeds to call the function or exits early.
    """
    @functools.wraps(func)
    def wrapper(x, y):
        # Initial Message

        print(random.choice(EXCUSE_INIT_MESSAGE))
        time.sleep(5)
        print("Processing... 25% done.")
        time.sleep(2)
        print("Still thinking... 50% done.")
        time.sleep(3)

        print(random.choice(EXCUSE_MESSAGE))
        time.sleep(5)

        # Ending Message and Decision to Execute
        res = random.randint(0, 1)
        if res == 0:
            print(EXCUSE_END_MESSAGE[0])
            time.sleep(1)
            return func(x, y)
        else:
            print(EXCUSE_END_MESSAGE[1])
    return wrapper

def procrastinate(max_time, delay_count):
    delays = set()
    while len(delays) < delay_count:
        delays.add(random.randint(0, max_time))

    for delay in delays:
        print(f"Procrastinating for {delay} seconds...")
        time.sleep(delay)
    return delays