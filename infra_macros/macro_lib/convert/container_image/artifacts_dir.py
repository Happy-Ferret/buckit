#!/usr/bin/env python3
import os


def get_per_repo_artifacts_dir():
    '''
    This is intended to work:
     - under Buck's internal macro interpreter, and
     - using the system python from `facebookexperimental/buckit`.

    We cannot unit-test this because our unit-tests run via LPARS, which
    break the assumption that the Python source path is located in the repo.
    '''
    path = os.path.abspath(__file__)
    while True:
        path = os.path.dirname(path)
        if path == '/':
            raise RuntimeError(
                'Could not find .buckconfig in any ancestor of '
                f'{os.path.dirname(os.path.abspath(__file__))}'
            )
        if os.path.exists(os.path.join(path, '.buckconfig')):
            break
    return os.path.join(path, 'buck-image-out')


if __name__ == '__main__':
    print(get_per_repo_artifacts_dir())
