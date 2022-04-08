import sys
import asyncio
import time
import pprint
import re

from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

from modules.common.check_param import CheckParam
from modules.common.hearing import Hearing
from modules.app.cache import Cache, CacheBacklog


cc = None
args = sys.argv
check_param = CheckParam()

def switchSet():
    hearinger = Hearing()
    answer = hearinger.select('Do you want to get the cache measure list from BackLog or SVN?', ['BackLog', 'SVN'], blank_ok=False)
    if answer == 'BackLog':
        return setBackLog()
    elif answer == 'SVN':
        return setSVN()


def setSVN():
    env = check_param.checkEnv(args, 'Please enter merge environment. ', 1)
    param = check_param.checkFormat(
        args,
        'Please enter new cache param.  ex)20220309 20220309_1 20220309-1',
        2,
        r'\d{8}(\_\d|\-\d)?',
        'Incorrect format. Please enter an 8-digit number.  ex)20220309 20220309_1 20220309-1'
    )

    return Cache(env, param)


def setBackLog():
    comment_url = check_param.checkBackLogUrl(args, 'Please enter BackLog Page URL.', 1)
    param = check_param.checkFormat(
        args,
        'Please enter new cache param.  ex)20220309 20220309_1 20220309-1',
        2,
        r'\d{8}(\_\d|\-\d)?',
        'Incorrect format. Please enter an 8-digit number.  ex)20220309 20220309_1 20220309-1'
    )
    return CacheBacklog(comment_url, param)


if len(args) > 1:
    check_backlog = re.search(r'https://sbweb.backlog.jp', args[1])
    if check_backlog is None:
        cc = setSVN()
    else:
        cc = setBackLog()
else:
    cc = switchSet()


def run_concurrent_origin(num, code_files):
    with ThreadPoolExecutor(max_workers=num, thread_name_prefix="thread") as executor:
        results = executor.map(cc.grep, code_files)
        print(results)
        #showResult(num, results)


def parallel_processing ():
    print('\nstart\n')
    start = time.time()

    num = 10

    code_files = cc.getCodeFileList(num)
    run_concurrent_origin(num, code_files)

    #cc.grep(code_files[0])

    print('\n result \n')
    pprint.pprint(cc.check_files)

    end = time.time()
    delta = end - start

    print(f'processing time: {format(round(delta,3))}')
    print(f'Number of files: {cc.count}')
    print('\nend\n')
    return


def sequential_processing():
    loop = asyncio.get_event_loop()
    gather = asyncio.gather(cc.start())
    loop.run_until_complete(gather)
    return


if __name__ == '__main__':
    #parallel_processing()

    sequential_processing()