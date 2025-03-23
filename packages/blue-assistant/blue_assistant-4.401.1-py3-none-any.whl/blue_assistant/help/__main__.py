from blueness import module
from blue_options.help.functions import help_main

from blue_assistant import NAME
from blue_assistant.help.functions import help_functions

NAME = module.name(__file__, NAME)


help_main(NAME, help_functions)



