#!/usr/bin/env python3

from richui import Richui, Config
from rich.padding import Padding
from rich.syntax import Syntax
from rich import print

def pause(ui, message="[reset][italic white](press enter to run the code)[/]"):
    ui.input(message, cursor=' ')

def show_and_run(ui, code_snippet: str, description: str, run_func=None):
    syntax = Syntax(code_snippet, "python", theme="dracula", line_numbers=True)
    print()
    print(Padding(syntax, (0,2)))
    print()
    print(f"[bold white]{description}[/]\n")
    pause(ui)
    if run_func:
        run_func()

def main() -> None:
    config_code = '''\
custom_config = Config(
    cursor="➠",
    bracket="(",
    checkmark="●", 
    title_style="bold white on #f33581",
    title_justify="center",
    value_style="#f72fcb",
    cursor_style="#40fab9",
    prompt_style="bold #4afd86",
    checkmark_style='#40fab9',
    option_style="#ffffff",
    selection_style="#fa9732",
    selected_style="#25f38d",
    footer_style="#707070",
    guide_style="#65fc8e",
    completion_style="white on #8c23f2",
    completion_second_style="italic #8c23f2 on #3f3f3f",
    text_width=50,
    padding=(0, 2)
)'''
    show_and_run(
        ui=Richui(Config()),
        code_snippet=config_code,
        description="This example uses a custom configuration for Rich UI. The above code snippet defines the custom styling options for the UI components."
    )

    custom_config = Config(
        cursor="➠",
        bracket="(",
        checkmark="●", 
        title_style="bold white on #f33581",
        title_justify="center",
        value_style="#f72fcb",
        cursor_style="#40fab9",
        prompt_style="bold #4afd86",
        checkmark_style='#40fab9',
        option_style="#ffffff",
        selection_style="#fa9732",
        selected_style="#25f38d",
        footer_style="#707070",
        guide_style="#65fc8e",
        completion_style="white on #8c23f2",
        completion_second_style="italic #8c23f2 on #3f3f3f",
        text_width=50,
        padding=(0, 2)
    )
    ui = Richui(custom_config)

    tree_code = '''\
tree_data = {
    "Programming": {
        "Language": {
            "Python": [
                "Hacking",
                "Scraping"
            ],
            "Bash": "Scripting"
        },
        "CodeEditor": {
            "Nano": "Nano is a simple command-line text editor.",
            "Acode": "Acode is a lightweight code editor for Android."
        }
    },
    "Language": {
        "ID": "Indonesia"
    }
}
ui.tree(tree_data, title="Data", text_wrap=True)
'''
    show_and_run(
        ui,
        tree_code,
        "The code above displays a tree view of nested data using Rich UI.",
        run_func=lambda: ui.tree({
            "Programming": {
                "Language": {
                    "Python": [
                        "Hacking",
                        "Scraping"
                    ],
                    "Bash": "Scripting"
                },
                "CodeEditor": {
                    "Nano": "Nano is a simple command-line text editor.",
                    "Acode": "Acode is a lightweight code editor for Android."
                }
            },
            "Language": {
                "ID": "Indonesia"
            }
        }, title="Data", text_wrap=True)
    )

    table_code = '''\
table_data = {
    "Name": "Rich UI",
    "Version": "1.0.0",
    "Description": "A simple and customizable command-line UI module built on top of the Rich library",
    "License": "MIT",
    "Source": "https://github.com/iqbalmh18/richui"
}
ui.table(table_data, title=" Rich UI ", text_wrap=True)
'''
    show_and_run(
        ui,
        table_code,
        "The above code snippet creates a table that displays key information about the Rich UI project.",
        run_func=lambda: ui.table({
            "Name": "Rich UI",
            "Version": "1.0.0",
            "Description": "A simple and customizable command-line UI module built on top of the Rich library",
            "License": "MIT",
            "Source": "https://github.com/iqbalmh18/richui"
        }, title=" Rich UI ", text_wrap=True)
    )

    input_text_code = '''\
name = ui.input("Enter your name:", prompt_style="#d75ff8", footer="<press enter to continue>")
print(f"Nice to meet you, {name}!")
'''
    show_and_run(
        ui,
        input_text_code,
        "This snippet shows a text input. The user is prompted to enter their name.",
        run_func=lambda: print(f"Nice to meet you, {ui.input('Enter your name:', prompt_style='#d75ff8', footer='<press enter to continue>')}!")
    )

    input_password_code = '''\
password = ui.input("Enter your password:", prompt_style="#269def", footer="<secure input: enter to continue>", secure=True)
print("Your password:", password)
'''
    show_and_run(
        ui,
        input_password_code,
        "This snippet demonstrates a secure input where the input text is masked.",
        run_func=lambda: print("Your password:", ui.input("Enter your password:", prompt_style="#269def", footer="<secure input: enter to continue>", secure=True))
    )

    input_completion_list_code = '''\
fruits_list = ["Apple", "Apricot", "Banana", "Blackberry", "Blueberry", "Cherry", "Date"]
fruit_input_list = ui.input(
    "Enter a fruit:",
    prompt_style="#60e282",
    footer="<use tab to show completion>",
    completion=fruits_list
)
print("Fruit chosen:", fruit_input_list)
'''
    show_and_run(
        ui,
        input_completion_list_code,
        "This snippet allows the user to choose a fruit with tab completion based on a predefined list.",
        run_func=lambda: print("Fruit chosen:", ui.input("Enter a fruit:", prompt_style="#60e282", footer="<use tab to show completion>", completion=["Apple", "Apricot", "Banana", "Blackberry", "Blueberry", "Cherry", "Date"]))
    )

    input_completion_dict_code = '''\
countries = {
    "United States": "New York",
    "Indonesian": "Jakarta",
    "Germany": "Berlin",
    "France": "Paris",
    "Japan": "Tokyo"
}
country_input = ui.input(
    "Enter a country:",
    prompt_style="#f83d3d",
    footer="<use tab to show completion>",
    completion=countries,
    completion_style="white on #f84a53",
    completion_second_style="italic #f84a53 on #3f3f3f"
)
print("Country chosen:", country_input)
'''
    show_and_run(
        ui,
        input_completion_dict_code,
        "This snippet demonstrates an input with completion using a dictionary where keys are used for matching.",
        run_func=lambda: print("Country chosen:", ui.input(
            "Enter a country:",
            prompt_style="#f83d3d",
            footer="<use tab to show completion>",
            completion={
                "United States": "New York",
                "Indonesian": "Jakarta",
                "Germany": "Berlin",
                "France": "Paris",
                "Japan": "Tokyo"
            },
            completion_style="white on #f84a53",
            completion_second_style="italic #f84a53 on #3f3f3f"
        ))
    )

    single_select_code = '''\
language = ["Bash", "Ruby", "Python", "Javascript"]
selected_action = ui.select(language, prompt="Select an programming language:", prompt_style="bold", return_index=False)
print("Selected programming language:", selected_action)
'''
    show_and_run(
        ui,
        single_select_code,
        "This snippet shows a single select menu where the user selects one programming language.",
        run_func=lambda: print("Selected programming language:", ui.select(["Bash", "Ruby", "Python", "Javascript"], prompt="Select an programming language:", prompt_style="bold", return_index=False))
    )

    multi_select_code = '''\
color_options = ["[red]Red[/]", "[green]Green[/]", "[blue]Blue[/]", "[yellow]Yellow[/]", "[purple]Purple[/]"]
selected_colors = ui.select(
    color_options,
    prompt="Select your favorite colors:",
    prompt_style="bold #39f782",
    footer="<use spase and arrow to toggle>",
    multi_select=True,
)
print("Selected colors:", selected_colors)
'''
    show_and_run(
        ui,
        multi_select_code,
        "This snippet presents a multi-select menu for choosing favorite colors.",
        run_func=lambda: print("Selected colors:", ui.select(
            ["[red]Red[/]", "[green]Green[/]", "[blue]Blue[/]", "[yellow]Yellow[/]", "[purple]Purple[/]"],
            prompt="Select your favorite colors:",
            prompt_style="bold #39f782",
            footer="<use spase and arrow to toggle>",
            multi_select=True,
        ))
    )

    confirm_code = '''\
confirm = ui.confirm("Do you think [bold]Rich UI[/] is cool?", footer="<press enter to confirm>")
print('Confirmed:', confirm)
'''
    show_and_run(
        ui,
        confirm_code,
        "This snippet displays a confirmation prompt to the user.",
        run_func=lambda: print("Confirmed:", ui.confirm("Do you think [bold]Rich UI[/] is cool?", footer="<press enter to confirm>"))
    )

if __name__ == "__main__":
    main()