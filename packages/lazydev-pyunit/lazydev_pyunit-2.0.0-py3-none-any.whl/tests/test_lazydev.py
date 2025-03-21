import pytest

from lazydev.lazydev import lazy_commit_message, lazy_pull_request, procrastination_tip, lazy_test_excuse

#   |-------------------------------|
#   | Tests for lazy_commit_message |
#   |-------------------------------|

#Ensures Keyword is in the commit message when added
def test_commit_keyword():
    keyword = "keyword"
    message = lazy_commit_message(keyword)
    assert keyword in message, f"'{keyword}' not in '{message}'"
    assert isinstance(message, str), "message needs to be a string"

#Ensures output is formatted properly when there is no keyword
def test_commit_no_keyword():
    message = lazy_commit_message()
    assert message, "there should be a message"
    assert not message.startswith(":"), "the colon shouldnt appear if no keyword"
    assert isinstance(message, str), "message needs to be a string"

#Ensures the message is not the same each time
def test_commit_message_random():
    message1 = lazy_commit_message("keyword")
    message2 = lazy_commit_message("keyword")
    assert message1 != message2, "messages should be different each time"

#   |-------------------------------|
#   |  Tests for lazy_pull_request  |
#   |-------------------------------|

#Ensures words are in pr title when given
def test_pr_words_given():
    verb = "test verb"
    noun = "test noun"
    message = lazy_pull_request(verb,noun)
    assert verb in message, f"'{verb}' not in '{message}'"
    assert noun in message, f"'{verb}' not in '{message}'"
    assert isinstance(message, str), "message needs to be a string"

#Ensures output is formatted properly with only given verb input 
def test_pr_verb_given():
    verb = "test verb"
    message = lazy_pull_request(verb)
    assert verb in message, f"'{verb}' not in '{message}'"
    assert message, "there should be a message"
    assert isinstance(message, str), "message needs to be a string"

#Ensures output is formatted properly with only given verb input 
def test_pr_noun_given():
    noun = "test noun"
    message = lazy_pull_request(inputNoun=noun)
    assert noun in message, f"'{noun}' not in '{message}'"
    assert message, "there should be a message"
    assert isinstance(message, str), "message needs to be a string"

#Ensures the message is not the same each time without given arguments
def test_pr_random():
    message1 = lazy_pull_request()
    message2 = lazy_pull_request()
    assert message1 != message2, "messages should be different each time"

#   |---------------------------------|
#   |  Tests for procrastination_tip  |
#   |---------------------------------|

# Ensures the message is different each time.
def test_procrastination_tip_random():
    keyword = "keyword"
    message1 = procrastination_tip(keyword)
    message2 = procrastination_tip(keyword)
    assert message1 != message2, "messages should be different each time"

# Checks to see all the placeholder variables were replaced from their respective lists.
def test_procrastination_tip_replace():
    for i in range(5):
        tip = procrastination_tip()
        assert "{loc}" not in tip, "{loc} was not replaced"
        assert "{work}" not in tip, "{work} was not replaced"
        assert "{rest}" not in tip, "{rest} was not replaced"
        assert "{snacks}" not in tip, "{snacks} was not replaced"
        assert "{drinks}" not in tip, "{drinks} was not replaced"
        assert "{socials}" not in tip, "{socials} was not replaced"
        assert "{days}" not in tip, "{days} was not replaced"

# Checks to see that the output is not empty - there was no failure that prevented the variables from being initialized and returned.
def test_procrastination_tip_not_empty():
    for i in range(10):
        assert len(procrastination_tip()) > 0, "message should not be empty" 

# Checks to see that the formatting is preserved in case the function and tips list is ever appended to.
def test_procrastination_tip_format():
    for i in range(20):
        message = procrastination_tip()
        assert message[0].isupper(), "message starts with a capital letter"
        assert message[-1] == ".", "message should end with a period"

#   |-------------------------------|
#   |  Tests for lazy_test_excuse   |
#   |-------------------------------|

#test if the function returns string 
def test_excuse_is_not_empty():
    excuse=lazy_test_excuse()
    assert isinstance(excuse,str),"Excuse should be string"

#checks if the reason input is embedded 
def test_excuse_reason():
    reason="My dog ate my code"
    excuse=lazy_test_excuse(reason)
    assert reason in excuse, f"'{reason} should be in the {excuse}'"

# This is to make sure the reason and excuse is grammatically correct
def test_structured_sentence():
    excuse=lazy_test_excuse()
    assert excuse,"Excuse should not be empty"
    assert excuse[0].isupper(),f"Excuse should start with a capital letter: {excuse}"
    assert excuse[-1] in {".", "!"}

# remove duplicates by running methods 10 times and confirming if any excuses are
def test_excuse_variability():
    excuses = {lazy_test_excuse() for _ in range(10)}
    assert len(excuses) > 1, "Excuses should not be identical across multiple calls"
