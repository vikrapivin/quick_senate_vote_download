from download_senate_votes import *

all_votes = None
for ii in range(101,118):
    for jj in range(1,3):
        if all_votes is not None:
            # print(ii, jj)
            cur_cong_session_votes = parse_senate_votes(ii,jj,verbose=False)
            cur_cong_session_votes['Congress'] = ii
            cur_cong_session_votes['Session'] = jj
            all_votes = pd.concat([all_votes, cur_cong_session_votes], ignore_index=True)
        else:
            all_votes = parse_senate_votes(ii,jj)
            all_votes['Congress'] = ii
            all_votes['Session'] = jj