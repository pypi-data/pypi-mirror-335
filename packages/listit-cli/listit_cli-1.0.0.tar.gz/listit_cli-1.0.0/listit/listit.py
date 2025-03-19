#!/usr/bin/env python3

import sys
import os
import pyfiglet
import inquirer
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init(autoreset=True)

# Globals
TASK_FILE = os.path.expanduser("~/.listit_tasks.txt")
console = Console()

def print_banner():
    """Display the ASCII banner with app details."""
    ascii_banner = pyfiglet.figlet_format("L.I.S.T")
    console.print(f"[bold cyan]{ascii_banner}[/bold cyan]")
    console.print("📌 Log Important Simple Tasks")
    console.print("🔹 Version: 1.0.0")
    console.print("📖 Type 'listit help' for usage instructions\n" + Style.RESET_ALL)

def show_help():
    """Show available commands."""
    console.print("\n[bold cyan]Available Commands:[/bold cyan]")
    console.print("[green]listit all[/green]      - View all tasks")
    console.print("[green]listit add 'task'[/green] - Add a new task")
    console.print("[green]listit done N[/green]   - Mark task N as done")
    console.print("[green]listit remove N[/green] - Remove task")
    console.print("[green]listit open N[/green] - To open the txt file")
    console.print("[green]listit help[/green]     - Show help\n")

def open_task_file():
    """Open the task file in the default editor."""
    if not os.path.exists(TASK_FILE):
        console.print("[red]No task file found! Add a task first using 'listit add \"task description\"'[/red]")
        return
    
    try:
        if sys.platform == "win32":
            os.startfile(TASK_FILE)
        elif sys.platform == "darwin":
            subprocess.run(["open", TASK_FILE])
        else:
            subprocess.run(["xdg-open", TASK_FILE])
        console.print("[bold green]✔ Task file opened in your default text editor.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error opening file:[/bold red] {e}")

def listit_tasks():
    """Display all tasks in a table."""
    if not os.path.exists(TASK_FILE):
        console.print("[red]No tasks found! Add a task using 'listit add \"task description\"'[/red]")
        return

    with open(TASK_FILE, "r") as f:
        tasks = f.readlines()

    if not tasks:
        console.print("[yellow]No tasks available.[/yellow]")
        return

    table = Table(title="📋 Your Tasks")
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="magenta")
    table.add_column("Task", style="white")

    for idx, task in enumerate(tasks, start=1):
        status, task_desc = task.strip().split("|", 1)
        table.add_row(str(idx), "[green]✔[/green]" if status == "[*]" else "[red]✘[/red]", task_desc)

    console.print(table)

def add_task(task):
    """Add a new task."""
    with open(TASK_FILE, "a") as f:
        f.write(f"[ ]|{task}\n")
    console.print(f"[bold green]✔ Task added:[/bold green] {task}")

def mark_task_done(task_id):
    """Mark a task as completed with an interactive confirmation."""
    if not os.path.exists(TASK_FILE):
        console.print("[red]No tasks available.[/red]")
        return

    with open(TASK_FILE, "r") as f:
        tasks = f.readlines()

    if task_id < 1 or task_id > len(tasks):
        console.print("[red]Invalid task ID![/red]")
        return

    task_text = tasks[task_id - 1].strip().split("|", 1)[1]

    questions = [
        inquirer.Confirm("confirm", message=f"Mark '{task_text}' as completed?")
    ]
    answer = inquirer.prompt(questions)

    if answer["confirm"]:
        tasks[task_id - 1] = tasks[task_id - 1].replace("[ ]", "[*]", 1)
        with open(TASK_FILE, "w") as f:
            f.writelines(tasks)
        console.print(f"[bold green]✔ Task {task_id} marked as completed![/bold green]")

def remove_task(task_id):
    """Remove a task with interactive confirmation."""
    if not os.path.exists(TASK_FILE):
        console.print("[red]No tasks available.[/red]")
        return

    with open(TASK_FILE, "r") as f:
        tasks = f.readlines()

    if task_id < 1 or task_id > len(tasks):
        console.print("[red]Invalid task ID![/red]")
        return

    removed_task = tasks[task_id - 1].strip().split("|", 1)[1]

    questions = [
        inquirer.Confirm("confirm", message=f"Are you sure you want to delete '{removed_task}'?")
    ]
    answer = inquirer.prompt(questions)

    if answer["confirm"]:
        tasks.pop(task_id - 1)
        with open(TASK_FILE, "w") as f:
            f.writelines(tasks)
        console.print(f"[bold yellow]🗑 Task removed:[/bold yellow] {removed_task}")

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print_banner()
        return
    
    command = sys.argv[1]

    if command == "all":
        listit_tasks()
    elif command == "add":
        if len(sys.argv) < 3:
            console.print("[bold red]Usage: listit add 'task description'[/bold red]")
        else:
            add_task(" ".join(sys.argv[2:]))
    elif command == "done":
        try:
            mark_task_done(int(sys.argv[2]))
        except (IndexError, ValueError):
            console.print("[bold red]Usage: listit done N (where N is the task number)[/bold red]")
    elif command == "remove":
        try:
            remove_task(int(sys.argv[2]))
        except (IndexError, ValueError):
            console.print("[bold red]Usage: listit remove N (where N is the task number)[/bold red]")
    elif command == "open":
        open_task_file()
    elif command == "help":
        show_help()
    else:
        console.print("[bold red]Unknown command! Type 'listit help' for instructions.[/bold red]")

if __name__ == "__main__":
    main()