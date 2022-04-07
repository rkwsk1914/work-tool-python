import sys

from modules.common.check_param import CheckParam
from modules.app.cms import CMSController

args = sys.argv
check_param = CheckParam()

comment_url = check_param.checkBackLogUrl(args, 'Please enter BackLog Page URL.', 1)
cms_type = check_param.checkCMSType(args, default='Sitecore_PROD', msg='Please enter your CMS Type.', num=2)

cms = CMSController(comment_url, cms_type=cms_type)
cms.start()
