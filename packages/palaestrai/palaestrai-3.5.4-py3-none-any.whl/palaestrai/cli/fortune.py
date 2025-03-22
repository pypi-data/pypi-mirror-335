import random

COOKIES = [
    """"
    There is more treasure in books 
    than in all the pirate's loot on Treasure Island." 
    --- Walt Disney
    """,
    """
    "It’s funny that pirates were always going around searching 
    for treasure, and they never realized that the real treasure 
    was the fond memories they were creating." 
    --- Jack Handey
    """,
    """
    "You got the makings of greatness in you, 
    but you got to take the helm and chart your own course!" 
    --- Long John Silver
    """,
    """
    "Nobody will believe it’s possible until we show them." 
    --- Captain Flint, Black Sails
    """,
    """
    "For every complex problem, 
    there is an answer that is clear, simple, and wrong."
    --- H. L. Mencken
    """,
    """
    "We make a living by what we get, 
    but we make a life by what we give."
    --- Winston Churchill
    """,
    """
    "Only those who will risk going too far 
    can possibly find out how far one can go."
    --- T. S. Eliot
    """,
    """
    "It's not that I'm so smart, 
    it's just that I stay with problems longer."
    --- Albert Einstein
    """,
    """
    "The ninety and nine are with dreams, 
    content but the hope of the world made new, 
    is the hundredth man who is grimly bent on 
    making those dreams come true."
    --- Edgar Allan Poe
    """,
    """
    "Email to T-"
    --- A./E.
    """,
    """
    "How much is the fish?"
    --- Scooter
    """,
    """
    "... We are not now that strength which in old days
    Moved earth and heaven, that which we are, we are;
    One equal temper of heroic hearts,
    Made weak by time and fate, but strong in will
    To strive, to seek, to find, and not to yield."
    --- Ulysses: Alfred, Lord Tennyson
    """,
    """
    "Nobody expects the Spanish Inquisition!"
    --- Monty Python: Cardinal Ximenez
    """,
    """
    "With enough coffee, you can face everything
    -- even Mondays!"
    --- Garfield
    """,
    """
    palaestrAI is user friendly! 
    It's just picky about who its friends are.
    --- E.
    """,
]


def get_cookie() -> str:
    return random.choice(COOKIES)
