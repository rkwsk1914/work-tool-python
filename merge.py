import sys
import re
from modules.common.hearing import Hearing
from modules.common.env_list import EnvList
from modules.merge import Merge

def checkUrl(args):
    comment_url = ''
    url_check = False

    if len(args) > 1:
        check = re.search(r'https://sbweb.backlog.jp/', args[1])
        if not check is None:
            url_check = True

    if url_check == False:
        hearinger = Hearing()
        comment_url = hearinger.validateInclude('Please enter BackLog Commit URL.', r'https://sbweb.backlog.jp/')
    else:
        comment_url = args[1]
    return comment_url

def checkEnv(args):
    merge_env = ''
    envlist = EnvList()
    env_check = False

    if len(args) > 2:
        env_check = envlist.checkExistEnvironment(args[2])

    if env_check == False:
        hearinger = Hearing()
        merge_env = hearinger.select('Please enter your Merge environment.', envlist.envlist)
    else:
        merge_env = args[2]
    return merge_env

args = sys.argv
#print(args)
#print(f'{checkUrl(args)}, {checkEnv(args)}')
mg = Merge(checkUrl(args), checkEnv(args))
mg.start()