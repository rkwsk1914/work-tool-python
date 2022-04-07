import sys
import asyncio
import time
import pprint
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

from modules.common.check_param import CheckParam
from modules.app.cache import Cache


args = sys.argv
check_param = CheckParam()

env = check_param.checkEnv(args, 'Please enter merge environment. ex)wiro-br', 1)
param = check_param.checkFormat(
    args,
    'Please enter new cache param.  ex)20220309 20220309_1 20220309-1',
    2,
    r'\d{8}(\_\d|\-\d)?',
    'Incorrect format. Please enter an 8-digit number.  ex)20220309 20220309_1 20220309-1'
)

cc = Cache(env, param)


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
