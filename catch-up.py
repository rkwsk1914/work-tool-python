import sys
from modules.common.check_param import CheckParam
from modules.app.catch_up import CatchUp

args = sys.argv
check_param = CheckParam()

page_url = check_param.checkUrl(args, 'Please enter Page URL.', 1)
env = check_param.checkEnv(args, 'Please enter merge environment.', 2)
cms_type = check_param.checkCMSType(args, default='WIRO', msg='Please enter your CMS Type.', num=3)

cp = CatchUp(cms_type=cms_type, page_url=page_url, env=env)
cp.start()
