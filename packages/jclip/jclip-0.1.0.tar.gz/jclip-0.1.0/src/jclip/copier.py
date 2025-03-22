import typer
import pyperclip
from typing_extensions import Annotated
from rich.console import Console
from time import sleep
from art import *
console = Console()

def JClip(
    clipout: Annotated[str, typer.Option("-clipout", "-ct", help="Output paste-file, e.g. 'clipboard.txt' [IMPORTANT: ONLY .TXT SUPORRT]")] = "",
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Enable verbose Mode")] = False
):
    ascii_logo = text2art("JClip", font="univers")
    print(ascii_logo)
    print("\n May the Clipboard Be With You! \n")
    file_formats = ".txt"
    if clipout == "":
        clipout = "jclip_output.txt"
    if file_formats not in clipout:
        clipout = clipout + ".txt"
    if file_formats in clipout:
        if verbose == False:
            with console.status("[bold green]Working on tasks...") as status:
                console.log("Correct file format in clipout", style="green")
                sleep(1)
                outfile = open(clipout, "a")
                fileclip = pyperclip.paste()
                outfile.write("\n \n \n [NEW PASTE LINE] \n \n" + fileclip)
                outfile.close()
                sleep(1)
                console.log("Pasted Clipboard in [" + "[white bold]" + clipout + "[green]]", style="bold green")
        if verbose == True:
             with console.status("[bold green]Working on tasks...") as status:
                console.log("Correct file format in clipout", style="green")
                sleep(1)
                outfile = open(clipout, "a")
                console.log("Opened Clipboard 📋", style="green")
                sleep(1)
                fileclip = pyperclip.paste()
                outfile.write("\n \n [NEW PASTE LINE] \n \n" + fileclip)
                console.log("[ TEXT PASTED ] >> \n \n \n ", fileclip, "\n \n")
                sleep(1)
                outfile.close()
                console.log("Closed File [" + "[white bold]" + clipout + "[green]]", style="green")
                sleep(1)
                console.log("Pasted Clipboard in [" + "[white bold]" + clipout + "[green]]", style="bold green")