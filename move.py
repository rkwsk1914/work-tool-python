import sys
from modules.common.check_param import CheckParam
from modules.app.move_page import MovePage

args = sys.argv
check_param = CheckParam()

previous_url = check_param.checkUrl(args, 'Please enter previous Page URL.', 1)
previous_env = check_param.checkEnv(args, 'Please enter previous environment.', 2)
destination_url = check_param.checkUrl(args, 'Please enter destination Page URL.', 3)
destination_env = check_param.checkEnv(args, 'Please enter destination environment.', 4)

mp = MovePage(
    destination_url=destination_url,
    previous_url=previous_url,
    destination_env=destination_env,
    previous_env=previous_env)
mp.start()
