"""
A simple program to download and do some basic parsing on the Senate votes.
There are a few main functions:
1. download_senate_vote -- downloads the data for a particular vote
2. download_senate_votes -- downloads the data for all votes from a particular senate session

I was personally interested in some statistics about the Vice President's casting vote. 
I implemented some very quick parsing code in parse_senate_votes
"""
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import os
import requests

def download_senate_vote(congress_number, session, vote_number, save_folder = 'senate_votes_xml/',custom_file_name=None):
    """Downloads a particular Senate vote based on the Congress number, session, and vote_number.
    Does not return anything.
    Parameters:
    congress_number: which Congress, ie. the 113th Congress would be 113
    session: which session? This is either 1 or 2.
    vote_number: which vote? All votes are sequentially numbered during a particular Congress
    TODO: add other parameters
    """
    congress_number = int(congress_number)
    session = int(session)
    if session > 2 or session < 1:
        raise ValueError('Session' + str(session) + ' not implemented. Only the first and second session are implemented.')
    if congress_number < 101 or congress_number > 117:
        raise ValueError('Congresses before the 101st or after the 117th are not implemented.')
    url = f'https://www.senate.gov/legislative/LIS/roll_call_votes/vote{congress_number}{session}/vote_{congress_number}_{session}_{vote_number:05}.xml'
    
    print(f'Downloading {congress_number} iteration of Congress, with {session} as the session number. Located at {url}.\n')
    req = requests.get(url)
    isExist = os.path.exists(save_folder)
    if not isExist:
      # Create a new directory because it does not exist 
      os.makedirs(save_folder)
      print(f"Creating the save directory {save_folder}.")
    if custom_file_name:
        fileName = custom_file_name
    else:
        fileName = f'{save_folder}{congress_number}_{session}_{vote_number:05}.xml'
    print(f'Saving file as {fileName}.')
    file = open(fileName, 'wb')
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()

def download_senate_votes(congress_number, session, save_folder = 'senate_votes_xml/',custom_file_name=None):
    """Downloads all Senate votes based on Congress number and session.
    Does not return anything.
    Parameters:
    congress_number: which Congress, ie. the 113th Congress would be 113
    session: which session? This is either 1 or 2.
    TODO: add other parameters
    """
    congress_number = int(congress_number)
    session = int(session)
    if session > 2 or session < 1:
        raise ValueError('Session' + str(session) + ' not implemented. Only the first and second session are implemented.')
    if congress_number < 101 or congress_number > 117:
        raise ValueError('Congresses before the 101st or after the 117th are not implemented.')
    url = f'https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{congress_number}_{session}.xml'
    
    print(f'Downloading {congress_number} iteration of Congress, with {session} as the session number. Located at {url}.\n')
    req = requests.get(url)
    isExist = os.path.exists(save_folder)
    if not isExist:
      # Create a new directory because it does not exist 
      os.makedirs(save_folder)
      print(f"Creating the save directory {save_folder}.")
    if custom_file_name:
        fileName = custom_file_name
    else:
        fileName = f'{save_folder}{congress_number}_{session}.xml'
    print(f'Saving file as {fileName}.')
    file = open(fileName, 'wb')
    for chunk in req.iter_content(100000):
        file.write(chunk)
    file.close()

class NoVoteError(Exception):
    pass
def vote_to_bool(vote_str):
    if vote_str == 'Yea':
        return True
    elif vote_str == 'Nay':
        return False
    elif vote_str == '':
        raise NoVoteError('VP did not Vote')
    else:
        raise ValueError("Vote String not defined for " + vote_str)
def majority_req_is_majority(majority_str):
    if majority_str == '1/2':
        return True
    elif majority_str == '3/5':
        return False
    elif majority_str == '2/3':
        return False
    else:
        raise ValueError("Majority string not defined for " + majority_str)
def parse_tie_vote(congress_number, session, vote_number, save_folder = 'senate_votes_xml/',custom_file_name=None,verbose=False):
    congress_number = int(congress_number)
    session = int(session)
    infile_name = f"senate_votes_xml/{congress_number}_{session}_{vote_number:05}.xml"
    try:
        infile = open(infile_name)
    except FileNotFoundError:
        download_senate_vote(congress_number, session, vote_number, save_folder = save_folder,custom_file_name=custom_file_name)
        infile = open(infile_name)
    contents = infile.read()
    soup = BeautifulSoup(contents,'xml')
    vote_cast = soup.find_all('vote_cast')
    party_votes = np.zeros((2,3))
    for ii in range(0,len(vote_cast)):
        party = vote_cast[ii].parent.party.get_text()
        vote = vote_cast[ii].get_text()
        if party == 'D':
            if vote =='Yea':
                party_votes[0,0] = party_votes[0,0] + 1
            if vote =='Nay':
                party_votes[1,0] = party_votes[1,0] + 1
        elif party == 'R':
            if vote =='Yea':
                party_votes[0,1] = party_votes[0,1] + 1
            if vote =='Nay':
                party_votes[1,1] = party_votes[1,1] + 1
        else:
            if vote =='Yea':
                party_votes[0,2] = party_votes[0,2] + 1
            if vote =='Nay':
                party_votes[1,2] = party_votes[1,2] + 1
    casting_vote = soup.find('tie_breaker')
    maj_string = casting_vote.parent.majority_requirement.get_text()
    if majority_req_is_majority(maj_string) == False:
        return (False, maj_string, party_votes)
    try:
        casting_vote_txt = casting_vote.tie_breaker_vote.get_text()
        if verbose:
            print(casting_vote.parent)
        vote_to_bool(casting_vote_txt)
    except NoVoteError:
        return (False, 'Did not vote', party_votes)
    casting_vote_authority = casting_vote.by_whom.get_text()
    return casting_vote_txt, casting_vote_authority, party_votes

def vote_outcome(result_string):
    if result_string == 'Confirmed':
        return True
    elif result_string == 'Agreed to':
        return True
    elif result_string == 'Passed':
        return True
    elif result_string == 'Rejected':
        return False
    elif result_string == 'Sustained':
        return True
    elif result_string == 'Not Well Taken':
        return False
    elif result_string == 'Not Sustained':
        return False
    elif result_string == 'Not Guilty':
        return False
    elif result_string == 'Guilty':
        return True
    elif result_string == 'Held Germane':
        return True
    elif result_string == 'Held Nongermane':
        return False
    elif result_string == 'Veto Sustained':
        return False
    elif result_string == 'Veto Overridden':
        return True
    elif result_string == 'Well Taken':
        return True
    else:
        print(result_string)
        raise ValueError("result_string in vote_outcome unknown")

def parse_senate_votes(congress_number, session, save_folder = 'senate_votes_xml/',custom_file_name=None,verbose=False):
    """Downloads parses all Senate votes for a particular Congress and session of Congress.
    Returns a pandas array with information about that Congress. Most of the information returned
    is geared to the actions of the Senate when the vote is tied.
    Parameters:
    congress_number: which Congress, ie. the 113th Congress would be 113
    session: which session? This is either 1 or 2.
    TODO: add other parameters
    Returns:
    TODO: add details about returned pandas array
    """
    congress_number = int(congress_number)
    session = int(session)
    infile_name = f"senate_votes_xml/{congress_number}_{session}.xml"
    try:
        infile = open(infile_name)
    except FileNotFoundError:
        download_senate_votes(congress_number, session, save_folder = save_folder,custom_file_name=custom_file_name)
        infile = open(infile_name)
    contents = infile.read()
    soup = BeautifulSoup(contents,'xml')
    vote_totals = soup.find_all('vote_tally')
    vote_information = pd.DataFrame({
        'Yeas': np.full(len(vote_totals),np.nan,dtype='int64'),
        'Nays': np.zeros(len(vote_totals),dtype='int64'),
        'Outcome': np.zeros(len(vote_totals),dtype='bool'),
        'Issue': np.zeros(len(vote_totals),dtype='str'),
        'Title': np.zeros(len(vote_totals),dtype='str'),
        'Vote number': np.zeros(len(vote_totals),dtype='int64')})
    for ii in range(0, len(vote_totals)):
        vote_information.at[ii,'Title'] = vote_totals[ii].parent.title.get_text()
        if vote_information.at[ii,'Title'] == 'Vote data is unavailable due to secret session.':
            continue
        vote_information.at[ii,'Yeas'] = int(vote_totals[ii].yeas.get_text())
        vote_information.at[ii,'Nays'] = int(vote_totals[ii].nays.get_text())
        vote_information.at[ii,'Outcome'] = vote_outcome(vote_totals[ii].parent.result.get_text())
        vote_information.at[ii,'Vote number'] = int(vote_totals[ii].parent.vote_number.get_text())
        if verbose:
            print(f'Current vote number {vote_information.at[ii,"Vote number"]}.')
        vote_information.at[ii,'Issue'] = vote_totals[ii].parent.issue.get_text()
        if vote_information.at[ii,'Yeas'] == vote_information.at[ii,'Nays']:
            casting_vote, casting_vote_authority, party_votes = parse_tie_vote(congress_number, session, vote_information.at[ii,'Vote number'], save_folder = save_folder,custom_file_name=custom_file_name,verbose=verbose)
            vote_information.at[ii,'Democratic Party Yeas'] = party_votes[0,0]
            vote_information.at[ii,'Democratic Party Nays'] = party_votes[1,0]
            vote_information.at[ii,'Republican Party Yeas'] = party_votes[0,1]
            vote_information.at[ii,'Republican Party Nays'] = party_votes[1,1]
            vote_information.at[ii,'Other Party Yeas'] = party_votes[0,2]
            vote_information.at[ii,'Other Party Nays'] = party_votes[1,2]
            if casting_vote:
                vote_information.at[ii,'Tiebreaking Vote'] = casting_vote
                vote_information.at[ii,'Tiebreaking Authority'] = casting_vote_authority
                vote_information.at[ii,'Vote Threshold Required'] = '1/2'
            else:
                if casting_vote_authority == 'Did not vote':
                    vote_information.at[ii,'Tiebreaking Vote'] = 'Did not vote'
                    vote_information.at[ii,'Vote Threshold Required'] = '1/2'
                else:
                    vote_information.at[ii,'Vote Threshold Required'] = casting_vote_authority
    return vote_information



            