import sys
from modules.common.check_param import CheckParam
from modules.app.resourcs_check import ResourceChecK

args = sys.argv
check_param = CheckParam()

comment_url = check_param.checkBackLogUrl(args, '投入ログのURLを選択してください。事前に「投入環境」に対象の開発環境を記入してください。\nPlease enter BackLog Page URL.', 1)
cms_type = check_param.checkCMSType(args, default='', msg='比較元のCMSを選択してください。\nPlease enter your CMS Type.', num=2)

rc = ResourceChecK(comment_url, cms_type=cms_type)
rc.start()
answer = input('')