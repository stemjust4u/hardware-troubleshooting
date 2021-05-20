class pcolor:
    ''' Add color to print statements '''
    LBLUE = '\33[36m'   # Close to CYAN
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    DBLUE = '\33[34m'
    WOLB = '\33[46m'    # White On LightBlue
    LPURPLE = '\033[95m'
    PURPLE = '\33[35m'
    WOP = '\33[45m'     # White On Purple
    GREEN = '\033[92m'
    DGREEN = '\33[32m'
    WOG = '\33[42m'     # White On Green
    YELLOW = '\033[93m'
    YELLOW2 = '\33[33m'
    RED = '\033[91m'
    DRED = '\33[31m'
    WOR = '\33[41m'     # White On Red
    BOW = '\33[7m'      # Black On White
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def rtcdate(tpl):
    return "{:4}-{}-{} {:2}:{:02d}:{:02d}.{}".format(tpl[0], tpl[1], tpl[2], tpl[4], tpl[5], tpl[6], tpl[7])

def localdate(tpl):
    return "{:4}-{}-{} {:2}:{:02d}:{:02d}".format(tpl[0], tpl[1], tpl[2], tpl[3], tpl[4], tpl[5])

def valmap(value, istart, istop, ostart, ostop):
        return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))