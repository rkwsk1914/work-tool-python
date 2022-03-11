import sys
import re

from modules.common.hearing import Hearing
from modules.catch_up import CatchUp

from modules.config.db import CMSLSIT
from modules.common.env_list import EnvList
from modules.config.setup import SOFTBANK_DOMAIN

def checkUrl(args, num):
    comment_url = ''
    url_check = False

    if len(args) > num:
        check = re.search(SOFTBANK_DOMAIN, args[num])
        if not check is None:
            url_check = True

    if url_check == False:
        hearinger = Hearing()
        comment_url = hearinger.validateInclude('Please enter Page URL.', SOFTBANK_DOMAIN)
    else:
        comment_url = args[num]
    return comment_url


def checkCMSType(args, num, default):
    cms_type = ''
    type_list = CMSLSIT
    type_check = False

    if len(args) > num:
        for type_item in type_list:
            if args[num] == type_item:
                type_check = True
    else:
        type_check = False
        cms_type = default

    if type_check == False:
        hearinger = Hearing()
        cms_type = hearinger.select('Please enter your CMS Type.', type_list)
    elif cms_type != '' and type_check == True:
        return cms_type
    else:
        cms_type = args[num]
    return cms_type

def checkEnv(args, num):
    merge_env = ''
    envlist = EnvList()
    env_check = False

    if len(args) > num:
        env_check = envlist.checkExistEnvironment(args[num])

    if env_check == False:
        hearinger = Hearing()
        merge_env = hearinger.select('Please enter your Merge environment.', envlist.envlist)
    else:
        merge_env = args[num]
    return merge_env

args = sys.argv

cms_type = checkCMSType(args, 2, 'WIRO')
page_url = checkUrl(args, 1)
env = checkEnv(args, 3)

cp = CatchUp(cms_type=cms_type, page_url=page_url, env=env)
cp.start()
