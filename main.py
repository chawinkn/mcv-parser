import argparse
import getpass
from mcv import MCVParser
from rich.console import Console
from rich.prompt import Prompt

console = Console()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCV Parser - Download course materials easily")
    parser.add_argument("-u", "-s", "--username", "--student-id", help="Your 10-digit Student ID", dest="username")
    parser.add_argument("-p", "--password", help="Your MyCourseVille password")
    args = parser.parse_args()

    username = args.username
    if not username:
        username = Prompt.ask("[bold white]👤 Student ID (10 digits)[/bold white]")

    password = args.password
    if not password:
        console.print("[bold white]🔑 Password:[/bold white] ", end="")
        password = getpass.getpass("")

    mcvp = MCVParser(username, password)

    with console.status("[bold yellow]🔐 Logging in...[/bold yellow]") as status:
        login_success = mcvp.login()
        if login_success:
            status.update("[bold green]✅ Login Successful![/bold green]")
        else:
            status.stop()
            console.print("[bold red]❌ Incorrect username or password. Please try again.[/bold red]")
            exit(1)

    console.print("[bold green]✅ Login Successful![/bold green]")
    mcvp.dump_materials()
