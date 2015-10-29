import os
import errno


def mkdir_p(path):
    '''Simulate mkdir_p.
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    '''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise
