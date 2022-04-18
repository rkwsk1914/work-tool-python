import svn.local

class SvnConroller:
    def __init__(self, dir):
        self.dir = dir
        self.localClient = svn.local.LocalClient(dir)
        return

    def update(self):
        print(f'\nStart updata svn.{self.dir}')

        try:
            self.localClient.update()
        except:
            print(f'Fail updata svn.\n')
            return False
        else:
            print(f'Finish updata svn.\n')
            return True

    def diff(self, full_path_a, full_path_b):
        return

    def delete(self, full_path):
        return