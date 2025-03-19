from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

# global variables
certainty_check = 0
answer_found = None
debug_flag = False
key_words_list = []


@inlineCallbacks
def key_words(
    session,
    question=None,
    question_lang="en",
    key_words=None,
    key_words_lang="en",
    time=3,
    certainty=0,
    debug=False,
):
    """
    This function asks a question and waits for the user to respond with a keyword from the list of keywords.

    Args:
        session (Component): The session object.
        question (str): The question to be asked.
        question_lang (str): The language the question needs to be read in.
        key_words (list): A list of keywords to be checked in the user response.
        key_words_lang: The language the key words need to be listened in.
        time (int): The time to wait for the user response in seconds.
        certainty (int): Only the words with a certainty higher than the specified number are chosen.
        debug (bool): A flag to print debug information.

    Returns:
        str: The keyword found in the user response.

    """

    global certainty_check
    global answer_found
    global debug_flag
    global key_words_list

    # # check if the arguments are of the correct type
    if not isinstance(question, str):
        raise TypeError("question is not a string")
    if not isinstance(key_words, list):
        raise TypeError("key_words is not a list")
    # check if the list contains only strings
    else:
        for word in key_words:
            if not isinstance(word, str):
                raise TypeError("key_words is not a list of strings")
    if not isinstance(time, int):
        raise TypeError("time is not an integer")
    if not isinstance(certainty, float):
        raise TypeError("certainty is not an integer")
    if not isinstance(debug, bool):
        raise TypeError("debug is not a boolean")

    certainty_check = certainty
    debug_flag = debug
    key_words_list = key_words

    yield session.call("rie.dialogue.say", text=question, lang=question_lang)

    yield session.call("rie.dialogue.config.language", lang=key_words_lang)

    yield session.subscribe(key_words_listen, "rie.dialogue.stt.stream")
    yield session.call("rie.dialogue.stt.stream")

    # record answers for the amount of time specified in seconds
    yield sleep(delay=time)

    if answer_found == None:
        print("No answer found")
    else:
        print("The keyword found: " + answer_found)

    session.call("rie.dialogue.stt.close")

    return answer_found


def check_words(frame_text):
    """
    This function checks if the words in the user response are in the list of keywords.

    Args:
        frame_text (str): The text found in the user response.

    Returns:
        None
    """
    global answer_found
    global key_words_list

    for word in frame_text.split():
        word = word.lower()
        if word in key_words_list:
            answer_found = word
            break

    pass


def key_words_listen(frame):
    """
    This function listens to the user response and checks if the words are in the list of keywords. It checks for 3 conditions:
    1. The text found is not an empty string
    2. The text found is Final (all words heard are concatenated in one string)
    3. The user wants to choose words based on the certainty

    Args:
        frame (dictionary): The frame dictionary from the robot's camera stream

    Returns:
        None
    """
    global debug_flag
    global certainty_check

    if (
        not frame["data"]["body"]["text"] == ""
        and frame["data"]["body"]["final"]
        and "certainty" in frame["data"]["body"]
        and frame["data"]["body"]["certainty"] > certainty_check
    ):
        # check the words in the text found
        check_words(frame["data"]["body"]["text"])

    if debug_flag:
        print("The user input is:")
        print(frame["data"]["body"]["text"])

    pass
