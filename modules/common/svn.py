import svn.local

class SvnConroller:
    def __init__(self, dir):
        self.dir = dir
        self.localClient = svn.local.LocalClient(dir)
        return

    def update(self):
        print(f'\nStart updata svn.{self.dir}')
        self.localClient.update()
        print(f'Finish updata svn.\n')
        return

    def diff(self, full_path_a, full_path_b):
        return

    def delete(self, full_path):
        return