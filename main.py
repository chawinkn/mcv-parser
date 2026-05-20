import argparse
import questionary
from mcv import MCVParser
from rich.console import Console

console = Console()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCV Parser - Download course materials easily")
    parser.add_argument("-u", "-s", "--username", "--student-id", help="Your 10-digit Student ID", dest="username")
    parser.add_argument("-p", "--password", help="Your MyCourseVille password")
    parser.add_argument("-d", "--delay", help="Crawl delay in seconds (default: 10.0)", type=float, default=10.0)
    args = parser.parse_args()

    if args.delay < 0:
        console.print("[bold red]❌ Delay must be a non-negative value.[/bold red]")
        exit(1)

    username = args.username
    if not username:
        username = questionary.text("Student ID (10 digits)").ask()

    password = args.password
    if not password:
        password = questionary.password("Password").ask()

    if not username or not password:
        console.print("[bold red]❌ Username and password are required.[/bold red]")
        exit(1)

    mcvp = MCVParser(username, password, delay=args.delay)

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
