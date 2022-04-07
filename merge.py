import sys
from modules.common.check_param import CheckParam
from modules.app.merge import Merge


args = sys.argv
check_param = CheckParam()

backlog_url = check_param.checkBackLogUrl(args, 'Please enter BackLog Commit URL.', 1)
merge_env = check_param.checkEnv(args, 'Please enter merge environment.', 2)

mg = Merge(backlog_url, merge_env)
mg.start()
