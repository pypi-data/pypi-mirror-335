import pytest
from src.pybirthday.pybirthday import cake, candle, balloon, teddy

plain_teddy = "\n".join([
            r"     __",
            r"  .'`  `'.",
            r" /        \ _",
            r";      __.'` `'.",
            r"|   .'`  `'.    \ ",
            r" \ / HAPPY  \    ;",
            r"  ;          ;   |",
            r"  | BIRTHDAY |   ;   _",
            r"  ;          ;-./-_-` '-.",
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
        ])

class Tests:

    @pytest.fixture
    def example_fixture(self):
        """
        An example of a pytest fixture - a function that can be used for setup and teardown before and after test functions are run.
        """

        # place any setup you want to do before any test function that uses this fixture is run

        yield  # at th=e yield point, the test function will run and do its business

        # place with any teardown you want to do after any test function that uses this fixture has completed

    #
    # Test functions
    #

    # Test for Candles
    def test_specific_candle(self):
        """
        Test if calling 'candle(n)' returns the correct candle at index 'n'.
        """
        # Check first candle
        first_candle = candle(0)
        expected_candle = "\n".join([
            "   (  ",
            "  ) ) ",
            " ( (  ",
            "  ) ) ",
            "   V  ",
            "   |  ",
            " .-+-.",
            " |   |",
            " '---'"
        ])
        assert first_candle == expected_candle, f"Expected first candle, but got:\n{first_candle}"

    def test_out_of_range(self):
        """
        Test if calling 'candle(n)' with 'n' greater than the available styles returns the last candle.
        """
        last_candle = candle(100)
        expected_last_candle = "\n".join([
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
        ])
        assert last_candle == expected_last_candle, f"Expected last candle, but got:\n{last_candle}"
        
    def test_random_candle(self):
        """
        Test if calling 'candle()' without arguments returns a valid candle from the list.
        """
        result = candle().split("\n")
        # Define possible candle options
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
        assert any(result == candle for candle in candle_styles)


    #Test for balloons
    def test_specific_balloon(self):
        """
        Test if calling 'balloon(n)' returns the correct balloon at index 'n'.
        """
        first_balloon = balloon(0)
        expected_balloon = "\n".join([
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
        ])
        assert first_balloon == expected_balloon, f"Expected first balloon, but got:\n{first_ballon}"

    def test_random_balloon(self):
        """
        Test if calling 'balloon()' without arguments returns a valid balloon from the list.
        """
        result = balloon().split("\n")
        # Define possible balloon styles
        balloon_styles = [
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
        assert any(result == balloon for balloon in balloon_styles)
    
    def test_balloon_(self):
        """
        Test if calling 'balloon(n)' with 'n' greater than the available styles returns the last balloon.
        """
        last_balloon = balloon(999)
        expected_balloon = "\n".join(
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
        )
        assert last_balloon == expected_balloon, f"Expected last balloon but got:\n{last_balloon} "

    #TESTS FOR TEDDY
    def test_default_teddy(self):
        '''
        Testing when called without arguments.
        The default message "HAPPY BIRTHDAY" is displayed on lines 1 and 3
        '''
        default_teddy = teddy()
        expected_teddy = plain_teddy

        assert default_teddy == expected_teddy, f"Expected default teddy, but got:\n{default_teddy}"
    
    def test_message_teddy(self):
        '''
        Testing when called with valid age and name arguments.
        The default message "HAPPY BIRTHDAY" is displayed on lines 1 and 3,
        and the age and name correctly shows up centered and all caps on lines 2 and 4
        '''
        message_teddy = teddy("20th", "Lauren")
        expected_teddy = "\n".join([
            r"     __",
            r"  .'`  `'.",
            r" /        \ _",
            r";      __.'` `'.",
            r"|   .'`  `'.    \ ",
            r" \ / HAPPY  \    ;",
            r"  ;   20TH   ;   |",
            r"  | BIRTHDAY |   ;   _",
            r"  ;  LAUREN  ;-./-_-` '-.",
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
        ])

        assert message_teddy == expected_teddy, f"Expected message to contain age and name in all-caps and centered, but got:\n{message_teddy}"

    def test_invalid_arg_teddy(self):
        '''
        Testing when called with invalid age (length too long) and name (incorrect type) arguments.
        The default message "HAPPY BIRTHDAY" is displayed on lines 1 and 3,
        and the age and name are ignored
        '''
        invalid_teddy = teddy("100000000th", 20)
        expected_teddy = plain_teddy

        assert invalid_teddy == expected_teddy, f"Expected default teddy, but got:\n{invalid_teddy}"
        
        
    #Test for cake
    def test_default_cake(self):
        '''
        Testing when called without arguments.
        The default message "Hope all your birthday wishes come true!" is displayed on the last line.
        '''
        default_cake = cake()
        expected_cake = "\n".join([
            r"                0   0",
            r"                |   |",
            r"            ____|___|____",
            r"         0  |~ ~ ~ ~ ~ ~|   0",
            r"         |  |           |   |",
            r"      ___|__|___________|___|__",
            r"      |/\/\/\/\/\/\/\/\/\/\/\/|",
            r"  0   |                       |   0",
            r"  |   |/\/\/\/\/\/\/\/\/\/\/\/|   |",
            r" _|___|_______________________|___|__",
            r"|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/|",
            r"|             H a p p y             |",
            r"|         B i r t h d a y! ! !      |",
            r"| ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ |",
            r"|___________________________________|",
            r"Hope all your birthday wishes come true!"
        ])

        assert default_cake == expected_cake, f"Expected default cake, but got:\n{default_cake}"
        
    def test_message_cake(self):
        message_cake = cake("TestContent", "Hi, this is a test.")
        expected_cake = "\n".join([
                r"                0   0",
                r"                |   |",
                r"            ____|___|____",
                r"         0  |~ ~ ~ ~ ~ ~|   0",
                r"         |  |           |   |",
                r"      ___|__|___________|___|__",
                r"      |/\/\/\/\/\/\/\/\/\/\/\/|",
                r"  0   |      TESTCONTENT      |   0",
                r"  |   |/\/\/\/\/\/\/\/\/\/\/\/|   |",
                r" _|___|_______________________|___|__",
                r"|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/|",
                r"|             H a p p y             |",
                r"|         B i r t h d a y! ! !      |",
                r"| ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ |",
                r"|___________________________________|",
                r"Hi, this is a test."
            ])

        assert message_cake == expected_cake, f"Expected message to contain name and words, but got:\n{message_cake}"
        
    def test_invalid_arg_cake(self):
        '''
        Testing when called with invalid name (length too long).
        The default pattern of cake will be displayed ignoring the name.
        '''
        
        invalid_cake = cake("abcdefghijklmnopqrst", "Hi, this is a test.")
        expected_cake = "\n".join([
            r"                0   0",
            r"                |   |",
            r"            ____|___|____",
            r"         0  |~ ~ ~ ~ ~ ~|   0",
            r"         |  |           |   |",
            r"      ___|__|___________|___|__",
            r"      |/\/\/\/\/\/\/\/\/\/\/\/|",
            r"  0   |                       |   0",
            r"  |   |/\/\/\/\/\/\/\/\/\/\/\/|   |",
            r" _|___|_______________________|___|__",
            r"|/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/|",
            r"|             H a p p y             |",
            r"|         B i r t h d a y! ! !      |",
            r"| ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ |",
            r"|___________________________________|",
            r"Hi, this is a test."
        ])

        assert invalid_cake == expected_cake, f"Expected default cake with words, but got:\n{invalid_cake}"