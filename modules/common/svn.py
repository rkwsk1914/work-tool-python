import svn.local
import subprocess

from modules.common.spinner import Spinner

class SvnConroller:
    def __init__(self, dir):
        self.dir = dir
        try:
            self.localClient = svn.local.LocalClient(dir)
        except Exception as e:
            self.showError(e)
        return

    def showError(self, e):
        print('=== エラー内容 ===')
        print('type:' + str(type(e)))
        print('args:' + str(e.args))
        if 'message' in str(e):
            print('message:' + str(e.message))
        print('e   :' + str(e))
        return

    def cleanup(self):
        print(f'\nCleanup updata svn.{self.dir}')
        cmd = f'svn cleanup {self.dir}'
        try:
            #cp = subprocess.run(cmd, capture_output=True)
            self.localClient.cleanup()
        except Exception as e:
            print(f'\nFail cleanup svn.\n')
            self.showError(e)
            return False
        else:
            print(f'\nReStart updata svn.{self.dir}')

            try:
                self.localClient.update()
            except Exception as e:
                print(f'\nFail updata svn.\n')
                self.showError(e)
                return self.cleanup()
            else:
                print(f'Finish updata svn.\n')
                return True

    def update(self):
        print(f'\nStart updata svn.{self.dir}')

        try:
            self.localClient.update()
        except Exception as e:
            print(f'\nFail updata svn.\n')
            self.showError(e)
            #self.cleanup()
            return False
        else:
            print(f'Finish updata svn.\n')
            return True

    def diff(self, full_path_a, full_path_b):
        return

    def delete(self, full_path):
        return