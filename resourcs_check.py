import sys
from modules.common.check_param import CheckParam
from modules.app.resourcs_check import ResourceChecK

args = sys.argv
check_param = CheckParam()

comment_url = check_param.checkBackLogUrl(args, 'Please enter BackLog Page URL.', 1)
cms_type = check_param.checkCMSType(args, default='WIRO', msg='Please enter your CMS Type.', num=2)

rc = ResourceChecK(comment_url, cms_type=cms_type)
rc.start()
