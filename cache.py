import sys
from modules.common.check_param import CheckParam
from modules.app.cache import Cache

args = sys.argv
check_param = CheckParam()

url = check_param.checkBackLogUrl(args, 'Please enter Page URL.', 1)
param = check_param.check(args, 'Please enter new cache param. ex)20220309 20220309_1', 2, r'\d{8}(\_\d+)*')

cc = Cache(url, param)
cc.start()
