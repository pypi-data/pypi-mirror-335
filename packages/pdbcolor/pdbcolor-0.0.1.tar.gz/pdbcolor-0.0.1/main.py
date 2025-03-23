from sys import breakpointhook
import pdbcolor


def myfunc():
    x = 1
    y = 2
    print(x + y)

if __name__ == "__main__":
    # from pdbcolor import PdbColor; PdbColor().set_trace()
    breakpoint()
    myfunc()
