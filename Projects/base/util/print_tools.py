from textwrap import wrap
from Projects.base.util.colors import colors

def_width = 50

def wrap_it(s, clr, w=def_width, end='\n'):
    for i in wrap(s, w):
        print(clr + i, end=end)

def question_cont(s, f=str):
    while True:
        try:
            wrap_it(s, colors.QUESTIONS, end=' '); 
            val = f(input().strip())
            break
        except KeyboardInterrupt:
            exit()
        except:
            wrap_it('The input is invalid.', colors.WARNING)
    return val