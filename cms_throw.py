import sys
import re
from modules.common.hearing import Hearing
from modules.cms import CmsThrow

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

def checkCMSType(args):
    cms_type = ''
    type_list = ('WIRO', 'Sitecore')
    type_check = False

    if len(args) > 2:
        for type_item in type_list:
            if args[2] == type_item:
                type_check = True

    if type_check == False:
        hearinger = Hearing()
        cms_type = hearinger.select('Please enter your CMS Type.', type_list)
    else:
        cms_type = args[2]
    return cms_type

args = sys.argv
#print(args)
#print(f'{checkUrl(args)}, {checkCMSType(args)}')
cms = CmsThrow(checkUrl(args), cms_type=checkCMSType(args))
cms.start()