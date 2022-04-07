import sys
import re

from modules.common.hearing import Hearing
from modules.common.env_list import EnvList
from modules.config.db import CMSLSIT
from modules.config.setup import SOFTBANK_DOMAIN

class CheckParam:
    def checkUrl(self, args, msg, num):
        comment_url = ''
        check = False

        if len(args) > num:
            check_resExp= re.search(SOFTBANK_DOMAIN, args[num])
            if not check_resExp is None:
                check = True

        if check == False:
            hearinger = Hearing()
            comment_url = hearinger.validateInclude(msg, SOFTBANK_DOMAIN)
        else:
            comment_url = args[num]
        return comment_url

    def checkBackLogUrl(self, args, msg, num):
        comment_url = ''
        url_check = False

        if len(args) > num:
            check_resExp= re.search(r'https://sbweb.backlog.jp', args[num])
            if not check_resExp is None:
                url_check = True

        if url_check == False:
            hearinger = Hearing()
            comment_url = hearinger.validateInclude(msg, r'https://sbweb.backlog.jp')
        else:
            comment_url = args[num]
        return comment_url

    def checkEnv(self, args, msg, num):
        merge_env = ''
        envlist = EnvList()
        env_check = False

        if len(args) > num:
            env_check = envlist.checkExistEnvironment(args[num])

        if env_check == False:
            hearinger = Hearing()
            merge_env = hearinger.select(msg, envlist.envlist)
        else:
            merge_env = args[num]
        return merge_env

    def checkCMSType(self, args, default, msg, num):
        cms_type = ''
        hearinger = Hearing()

        if len(args) > num:
            print('test', args[num])
            for type_item in CMSLSIT:
                if args[num] == type_item:
                    return args[num]
        else:
            for type_item in CMSLSIT:
                if default == type_item:
                    return default

        cms_type = hearinger.select(msg, CMSLSIT)
        return cms_type

    def check(self, args, msg, num, regexp):
        answer = ''
        check = False

        if len(args) > num:
            check_resExp= re.search(regexp, args[num])
            if not check_resExp is None:
                check = True

        if check == False:
            hearinger = Hearing()
            answer = hearinger.validateInclude(msg, regexp)
        else:
            answer = args[num]
        return answer

    def checkFormat(self, args, msg, num, regexp, error_msg):
        answer = ''
        check = False

        if len(args) > num:
            pattern = re.compile(r'^' + regexp + r'$')
            check_resExp = pattern.match(args[num])
            if not check_resExp is None:
                check = True

        if check == False:
            hearinger = Hearing()
            answer = hearinger.validateFormat(msg, regexp, error_msg)
        else:
            answer = args[num]
        return answer