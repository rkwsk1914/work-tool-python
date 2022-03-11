import sys
import re
from modules.common.hearing import Hearing
from modules.resourcs_check import ResourceChecK
from modules.config.db import CMSLSIT

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

def checkCMSType(args, default):
    cms_type = ''
    type_list = CMSLSIT
    type_check = False

    if len(args) > 2:
        for type_item in type_list:
            if args[2] == type_item:
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
        cms_type = args[2]
    return cms_type

args = sys.argv
#print(args)
#print(f'{checkUrl(args)}, {checkCMSType(args, 'WIRO')}')

comment_url = checkUrl(args)
cms_type = checkCMSType(args, 'WIRO')

rc = ResourceChecK(comment_url, cms_type=cms_type)
rc.start()