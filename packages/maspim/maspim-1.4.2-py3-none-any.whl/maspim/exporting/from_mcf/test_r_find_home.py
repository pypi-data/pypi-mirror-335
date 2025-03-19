"""Check if an R home directory is found"""
import os


def test_r_home():
    from maspim.exporting.from_mcf.helper import get_r_home

    assert os.path.samefile(get_r_home(), r'C:\Program Files\R\R-4.3.3')



if __name__ == '__main__':
    test_r_home()