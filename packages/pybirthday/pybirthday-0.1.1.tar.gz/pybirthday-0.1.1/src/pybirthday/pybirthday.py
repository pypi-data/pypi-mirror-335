import random

def cake(name=None, words="Hope all your birthday wishes come true!"):
    name_on_cake = "               "
    if name is not None and isinstance(name, str) and len(name) <= 15:
        name_on_cake = f"{name.upper()}"
        name_on_cake = name_on_cake.center(15)
    cake_style = [
            r"                0   0",
            r"                |   |",
            r"            ____|___|____",
            r"         0  |~ ~ ~ ~ ~ ~|   0",
            r"         |  |           |   |",
            r"      ___|__|___________|___|__",
            r"      |/\/\/\/\/\/\/\/\/\/\/\/|",
            f"  0   |    {name_on_cake}    |   0",
            r"  |   |/\/\/\/\/\/\/\/\/\/\/\/|   |",
            r" _|___|_______________________|___|__",
            r"|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/|",
            r"|             H a p p y             |",
            r"|         B i r t h d a y! ! !      |",
            r"| ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ |",
            r"|___________________________________|",
            words
    ]
    return "\n".join(cake_style)

def candle(n=None):
    """
    Generate an ASCII art of a candle.

    This function returns an ASCII art candle either randomly or based on a specified index.
    """
    candle_styles = [
        [
            "   (  ",
            "  ) ) ",
            " ( (  ",
            "  ) ) ",
            "   V  ",
            "   |  ",
            " .-+-.",
            " |   |",
            " '---'"
        ],
        [
            "        ,        ",
            "       ( \\       ",
            "        ) \\      ",
            "       ((\\ )     ",
            "      |`-;-._    ",
            "      |`-.   )   ",
            "      |   \\ (   ",
            "      |    \\ )   ",
            "      |    |/    ",
            "      |    `|    ",
            "      |     |    ",
            "      |     |    ",
            "      |     |    ",
            "      |     |    ",
            "      |_____|    ",
            "    _(_______)_  ",
            "   |           | ",
            "   |_____________|"
        ],
        [
            "              :              ",
            "      .       :       .      ",
            "       ::.   :::   .::       ",
            "          ::  :   ::         ",
            "           :  )  :           ",
            "      :::::  (_)  :::::      ",
            "         .: .-;_ :.          ",
            "       .:   |   \\  :.        ",
            "            |    )           ",
            "            |   |     __     ",
            "          . |   |   _) .(    ",
            "         _\\/|   | _) .'_|    ",
            "          -\\|   |) .'_(      ",
            "        ~>>8o<<-'8o-'  `     ",
            "         / /,\\-(  )``.,      ",
            "         | \\.'\\/  ) :(       ",
            "         \\   `'   `) (`      ",
            "          `._____.'`./       "
        ],
        [
            "                   . . ...                   ",
            "                .:::'.`:::::.                ",
            "               ::::::  '::::::               ",
            "              :::::: J6  ::::::              ",
            "              :::::  HMw  :::::              ",
            "              :::::  WNM  :::::              ",
            "              :::::: MAM ::::::              ",
            "               :::::.`;'.:::::               ",
            "                 ::Mmmmmmm;:                 ",
            "                   KKKRRMMA                  ",
            "                   KPPPP9NM                  ",
            "                   K7IIYINN                  ",
            "                   Klll1lNJ                  ",
            "                   Klll1lNR                  ",
            "                   Kl::1lJl                  ",
            "                   L:::1:J                   ",
            "                   L:::!:J                   ",
            "                   L:::::l                   ",
            "                   l:..::l       .           ",
            "             ,nnnnml:...:lmncJP',            ",
            "  :::::::;mCCCc'pdPl:...:l9bqPyj'jm;:::::::::::::::",
            "  ::::::OPCCcc.9b::;.....;::dP ,JCC9O::::::::::::::",
            "  ::::' 98CCccc.9MkmmnnnmmJMP.JacOB8P '::::::::::::",
            "  :::    `9qmCcccc\"\"YAAAY\"\"roseCmpP'    :::::::::::",
            "  :::.     ``9mm,...     ...,mmP''     .:::::::::::",
            "  :::::..       \"YTl995PPPT77\"      ..:::::::::::::",
            "  :::::::::...                 ...:::::::::::::::::",
            "  ::::::::::::::::.........::::::::::::::::::::::::"
        ],
        [
            "     ,?    ",
            "    ( :    ",
            "     ;)    ",
            "     |     ",
            "   ,-.-j   ",
            "  ;|   |   ",
            "  `|   |   ",
            "   |   `.  ",
            "   |,; |; ,-.",
            "   |U  | /();",
            " f`-^-^-',-' ",
            "  `-----'   "
        ]
    ]

    if n is None:
        style = random.choice(candle_styles)
    elif n > len(candle_styles) - 1:
        style = candle_styles[len(candle_styles) - 1]
    else:
        style = candle_styles[n]

    return "\n".join(style)

def balloon(n=None):
    """
    Generate an ASCII art of a balloon.
    
    This function returns an ASCII art balloon either randomly or based on a specified index.
    """
    balloon_styles = [
        # Add different ASCII balloon designs here
        [
            "                          __",
            "                        ,\"  \".",
            "     _      .---.    _ /#     \\",
            "   ,' `.  ,'     `.." ".      ,--.",
            "   |#   `/ #      (#    )    /    )",
            "    `.   |         )   (`.__/    /",
            "      `. \\        (     )/'/    /",
            "        `.\\       /)   (( /    /",
            "           `.   .'(     )y    /",
            "             >_<\\  `._.'(    /",
            "             /   ) /'-`.->,-'",
            "            (   ( (   (",
            "             )     )   )",
            "                  ("
        ],
        [
            "     ,-''''-.",
            "   ,'      _ `.",
            "  /       )_)  \\",
            " :              :",
            " \\              /",
            "  \\            /",
            "   `.        ,'",
            "     `.    ,'",
            "       `.,'",
            "        /\\`.   ,-._",
            "            `-'"
        ],
        [
            "     ######",
            "   ##########",
            "  ######    _\\_",
            "  ##===----[.].]",
            "  #(     ,   _\\",
            "   #      )\\__|",
            "    \\        /",
            "     `-._``-'",
            "        >@",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |",
            "         |"
        ],
        [
            "     .;;;;;;       ;;;;;;,.",
            "   .;;;;;;;;;     ;;;;;;;;;;,",
            " .;;;;;;;;;;;;   ;;;;;;;;;;;;;.",
            " ;;;;;@;;;;;;;; ;;;;;;;;;;;;;;;'",
            " ;;;;@@;;;;;;;;;;;;;;;;;;;;;;;;'",
            " ;;;;@@;;;;;;;;;;;;;;;;;;;;;;;;'",
            " `;;;;@;;;;;;;;;;;;;;;@;;;;;;;'",
            "  `;;;;;;;;;;;;;;;;;;;@@;;;;;'",
            "    `;;;;;;;;;;;;;;;;@@;;;;'",
            "      `;;;;;;;;;;;;;@;;;;'",
            "         `;;;;;;;;;;;;'",
            "            `;;;;;;'",
            "               ;;",
            "               `",
            "              `",
            "             `",
            "            `",
            "           `",
            "          `",
            "         `",
            "         `",
            "         `",
            "          `",
            "            `.",
        ]
    ]
    
    if n is None:
        style = random.choice(balloon_styles)
    elif n > len(balloon_styles) - 1:
        style = balloon_styles[len(balloon_styles) - 1]
    else:
        style = balloon_styles[n % len(balloon_styles)]
    
    return "\n".join(style)

def teddy(age=None, name=None):
    '''
    This function returns a drawing of a teddy bear!
    The default message is "HAPPY BIRTHDAY," but you can add optional params to add
    age and name into the message.
    Both age and name need to be <=10 chars long, or else the function will ignore it
    '''
    #default message
    line2 = "          "
    line4 = "          "

    #validate params
    if age is not None and isinstance(age, (int, str)) and len(str(age)) <= 10:
        age_str = f"{str(age).upper()}"
        line2 = age_str.center(10)
    if name is not None and isinstance(name, str) and len(name) <= 10:
        name_str = f"{name.upper()}"
        line4 = name_str.center(10)

    image = [
        r"     __",
        r"  .'`  `'.",
        r" /        \ _",
        r";      __.'` `'.",
        r"|   .'`  `'.    \ ",
        r" \ / HAPPY  \    ;",
        f"  ;{line2};   |",
        r"  | BIRTHDAY |   ;   _",
        f"  ;{line4};-./-_-` '-.",
        r"  /\        /_(;'/ `\    '.",
        r" ;  '.__  .'\|| '    |     '.",
        r" |      ),\| \ \     /       \ ",
        r" ;        \ \|/   __/         \  __",
        r"  \        \||\.~'_ `'.;-.___.~'` _'~.",
        r"   '.__  _/|/|/{ (_`.'         '.`_) }",
        r"       `)/`\  \ \ .'  _ 0_._0 _  '. /     .,_",
        r"             \|| } -.'   (_)   '.- {    _{   `\ ",
        r"              \|{_ / '.___|___.' \  }  //`._   |",
        r"            /`    \     |   |     }  }:'-.  ```''--..==,",
        r"           {      ,}    \-'-/   .'  } {,`-'.       //>`\>",
        r"          {`   _./|\._.  '-'  ._ .~` /`    ;'.    //>  |>",
        r"          {     {///(  `-.-.-`  ) _.'     /   '. ||>   />",
        r"           \     \|\);-- ( ) -- (`       }      `\ \>_.'>",
        r"            ;  _/`/(__.'/`-'.,__/`,    .`         `'' '`",
        r"           .-'`     ;-.(     \_(;  \ .'     .--,",
        r"          (`-._   ./   `       '.   `-._..~` /\ \ ",
        r"           `'-;/``.              `;-'`:     |  ||",
        r"      .--._ _.' .  \      o       ;  .      |  /|",
        r"     /.-.  `     .  '._        _.'  '       \_//",
        r"     ||  \        `.   `'-----`  _.~`--..__,..'",
        r"     |\   |       .~`'--......--'",
        r"     \ '._/   _.~`",
        r"       `.__.-'"
    ]

    return "\n".join(image)