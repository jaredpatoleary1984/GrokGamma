Python 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> Traceback (most recent call last):
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\readline.py", line 395, in multiline_input
    return reader.readline()
           ~~~~~~~~~~~~~~~^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\reader.py", line 758, in readline
    self.handle1()
    ~~~~~~~~~~~~^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\reader.py", line 741, in handle1
    self.do_cmd(cmd)
    ~~~~~~~~~~~^^^^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\reader.py", line 671, in do_cmd
    self.refresh()
    ~~~~~~~~~~~~^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\reader.py", line 648, in refresh
    self.screen = self.calc_screen()
                  ~~~~~~~~~~~~~~~~^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\completing_reader.py", line 261, in calc_screen
    screen = super().calc_screen()
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\reader.py", line 315, in calc_screen
    colors = list(gen_colors(self.get_unicode()))
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\utils.py", line 115, in gen_colors
    for color in gen_colors_from_token_stream(gen, line_lengths):
                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\utils.py", line 175, in gen_colors_from_token_stream
    for prev_token, token, next_token in token_window:
                                         ^^^^^^^^^^^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\_pyrepl\utils.py", line 384, in prev_next_window
    for x in iterator:
             ^^^^^^^^
  File "C:\Users\jared\AppData\Local\Python\pythoncore-3.14-64\Lib\tokenize.py", line 588, in _generate_tokens_from_c_tokenizer
    for info in it:
                ^^
UnicodeEncodeError: 'utf-8' codec can't encode characters in position 69-70: surrogates not allowed
>>>
