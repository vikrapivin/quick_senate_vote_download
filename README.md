# quick_senate_vote_download
## A small package to download the outcomes of all Senate Votes since the 101st Congress

Here I provide some example code `example_code.py` to demonstrate how to run this package. This code will download all the aggregate vote xml files for the US Senate starting at the 101st Congress.

This package was built to allow for quick analysis of how the casting vote (tiebreaking vote) in the US Senate works in practice and illuminates the actions of the Vice President during tied votes since the 101st Congress.

From this dataset one can quickly see that the Vice President has failed to cast a vote on 56 occassions since the 101st Congress. For 16 of those occassions, the Vice President's party was generally in support of the question posed. I have included some raw datasets on the details of these votes under the name of `anomalous_instances.csv` (the field separator is `[` as other characters are legal in some of the fields.

I have also provided a csv file called `all_tied_votes.csv` with the same field separator as above. This file includes all tied votes since the 101st Congress including questions that require a larger voting threshold for passage such as a tied vote on a vote requiring 3/5ths or 2/3rds of the votes to be in favor.

Copyright 2022. This code is made available under the GNU AGPL.
