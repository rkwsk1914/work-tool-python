import sys
from modules.common.check_param import CheckParam
from modules.app.merge import Merge


args = sys.argv
check_param = CheckParam()

backlog_url = check_param.checkBackLogUrl(args, 'Please enter BackLog Commit URL.', 1)
merge_env = check_param.checkEnv(args, 'Please enter merge environment.', 2)
fouce_copy = check_param.checkSelection(args, msg='Do you want to force a copy?.', default='no', selection=['yes', 'no', 'y', 'n'], num=3)

mg = Merge(backlog_url, merge_env, fouce_copy)
mg.start()
