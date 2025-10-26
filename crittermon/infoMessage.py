import time
import crittermon.tools as tools

def message(message):
    tools.flush_stdin()
    tools.gv.input_manager.pause()
    console = tools.gv.console

    console.print(f"{message} <<", style="bright_white")
    input()

    tools.flush_stdin()
    time.sleep(0.25)
    tools.gv.input_manager.unpause()


