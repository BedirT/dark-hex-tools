'''
Single py file to combine all pONE projects.

The file will direct user on a menu to find the options the user is
interested in.
'''
from Projects.pONE.user_tools.glance import glance
from Projects.base.util.cPlot import heat_map
from Projects.base.util.colors import colors
from Projects.pONE.user_tools.trainer import train_pONE
from Projects.pONE.user_tools.play import play_pONE

from Projects.base.util.print_tools import wrap_it, question_cont

def_width = 50
print(colors.BOLD + colors.TITLE + '{:^{}}'.format('pONE', def_width) + colors.ENDC)

mid_text = 'Please choose the action you want to follow from the menu provided. \
If you see any error & you have any suggestions please do let me know via an issue \
@BedirT'
wrap_it(mid_text, colors.MIDTEXT)

the_menu = ['Use the item numbers to enter the value (i.e. 1)', 
'\t1) Train with pONE', 
'\t2) Play against pONE',
'\t3) Have a glance at the data', 
'\t4) Plot heatmaps']
for menu_item in the_menu:
    wrap_it(menu_item, colors.QUESTIONS)

input_q = 'Please enter a value:'
wrap_it(input_q, colors.QUESTIONS, end=' ')
choice = False
while not choice:
    choice = input().strip()
    if choice == '1':
        # run training
        input_menu = ['Here we will need some inputs to be able to continue running the training.',
                      'Please enter number of columns:',
                      'Please enter number of rows:',
                      'Please enter the output destination (optional - leave it empty):']
        wrap_it(input_menu[0], colors.MIDTEXT)
        cols = question_cont(input_menu[1], int)
        rows = question_cont(input_menu[2], int)
        input_file = question_cont(input_menu[3])
        train_pONE(input_file, rows, cols)
    elif choice == '2':
        input_menu = ['Here we will need some inputs to be able to continue running the training.',
                      'Please enter the input file destination (optional-leave empty to download):']
        wrap_it(input_menu[0], colors.MIDTEXT)
        input_file = question_cont(input_menu[1])
        play_pONE(input_file)
        # run play pone
    elif choice == '3':
        input_menu = ['Here we will need some inputs to be able to continue running the training.',
                      'Please enter the input file destination (optional-leave empty to download):']
        wrap_it(input_menu[0], colors.MIDTEXT)
        input_file = question_cont(input_menu[1])
        glance(input_file)
    elif choice == '4':
        input_menu = ['Here we will need some inputs to be able to continue running the training.',
                      '\tPlease enter the input file destination (optional - leave it empty (will run 4x3 board by default)):']
        wrap_it(input_menu[0], colors.MIDTEXT)
        input_file = question_cont(input_menu[1])
        if not input_file:
            input_file = 'Exp_Results/pONE/4x3/default_file.pkl'
        heat_map(input_file)
    else:
        print('Invalid input, please try again.')
        choice = False
