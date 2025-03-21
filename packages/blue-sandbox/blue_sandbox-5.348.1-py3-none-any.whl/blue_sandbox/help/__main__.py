from blueness import module
from blue_options.help.functions import help_main

from blue_sandbox import NAME
from blue_sandbox.help.functions import help_functions

NAME = module.name(__file__, NAME)


help_main(NAME, help_functions)
