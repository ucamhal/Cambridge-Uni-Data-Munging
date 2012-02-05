import argparse, errno

class CmdLineApp:
    
    def __init__(self, ignore_broken_pipe=False):
        self.__parser = argparse.ArgumentParser()
        try:
            self.__run__()
        except IOError, e:
            if ignore_broken_pipe and e.errno == errno.EPIPE:
                exit(0)
            raise
    
    def get_parser(self):
        return self.__parser
    
    def define_arguments(self, parser):
        pass
    
    def main(self, args):
        raise RuntimeError("main() not implemented")
    
    def __run__(self):
        self.define_arguments(self.get_parser())
        self.main(self.get_parser().parse_args())