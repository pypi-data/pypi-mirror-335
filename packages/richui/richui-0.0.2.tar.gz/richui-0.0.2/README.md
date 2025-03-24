# Rich UI

**An interactive command-line UI module built on top of Rich for customizable UI components.**

Rich UI is a Python module that allows you to build interactive command-line interfaces with a modern, colorful, and fully customizable appearance. It leverages the power of [Rich](https://github.com/Textualize/rich) to provide features such as syntax-highlighted code displays, interactive tree and table views, input prompts with completion, and selection menus.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Custom Configuration Example](#custom-configuration-example)
  - [Tree View Example](#tree-view-example)
  - [Table Example](#table-example)
  - [Text Input Example](#text-input-example)
  - [Secure Input (Password) Example](#secure-input-password-example)
  - [Input with Completion (List) Example](#input-with-completion-list-example)
  - [Input with Completion (Dictionary) Example](#input-with-completion-dictionary-example)
  - [Single Select Example](#single-select-example)
  - [Multi-Select Example](#multi-select-example)
  - [Confirm Example](#confirm-example)
- [Running the Example](#running-the-example)

## Features

- **Interactive Components:** Includes tree views, tables, single and multi-select menus, secure input prompts, and confirm dialogs.
- **Custom Configuration:** Easily configure UI elements such as cursor style, prompt style, footer style, and more.
- **Syntax Highlighting:** Display text with syntax highlighting (support: rich markup, ansii colors, hex colors).
- **Completion Support:** Input fields with support for auto-completion from lists or dictionaries.

## Installation

Install **richui** with pip:

```bash
pip install richui
```

Install **richui** from sources:

```bash
git clone https://github.com/iqbalmh18/richui
cd richui
pip3 install .
```

## Quick Start

import **Richui** and **Config** class

```python
from richui import Richui, Config
```
### Custom Configuration Example

This snippet defines a custom configuration for Richui, including styling options for various UI components.

```python
custom_config = Config(
    cursor="➠",
    bracket="(",
    checkmark="●", 
    title_style="bold white on #f33581",
    title_justify="center",
    value_style="#f72fcb",
    cursor_style="#40fab9",
    prompt_style="bold #4afd86",
    checkmark_style="#40fab9",
    option_style="#ffffff",
    selection_style="#fa9732",
    selected_style="#25f38d",
    footer_style="#707070",
    guide_style="#65fc8e",
    completion_style="white on #5efda9",
    completion_second_style="italic #5efda9 on #3f3f3f",
    text_width=50,
    padding=(0, 2)
)
```

Set **custom_config** to Richui

```python
ui = Richui(custom_config)
```

*Description:* This example uses a custom configuration for Rich UI. The above snippet defines styling options for the UI components.

### Tree View Example

This snippet displays a tree view of nested data.

```python
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
    "Country": {
        "ID": "Indonesia"
    }
}
ui.tree(tree_data, title="Data", text_wrap=True)
```

*Description:* The code above displays a tree view of nested data using Rich UI.

### Table Example

This snippet creates a table to display key information about the Rich UI project.

```python
table_data = {
    "Name": "Rich UI",
    "Version": "1.0.0",
    "Description": "A customizable command-line UI module built on top of the Rich library.",
    "License": "MIT",
    "Source": "https://github.com/iqbalmh18/Richui"
}
ui.table(table_data, title=" Rich UI ", text_wrap=True)
```

*Description:* The above snippet creates a table that displays key information about the Rich UI project.

### Text Input Example

This snippet shows a text input prompt where the user is asked to enter their name.

```python
name = ui.input("Enter your name:", prompt_style="#d75ff8", footer="<press enter to continue>")
print(f"Nice to meet you, {name}!")
```

*Description:* This snippet shows a text input prompt for the user's name.

### Secure Input (Password) Example

This snippet demonstrates a secure input prompt where the entered text is masked.

```python
password = ui.input("Enter your password:", prompt_style="#269def", footer="<secure input: enter to continue>", secure=True)
print("Your password:", password)
```

*Description:* The code above demonstrates a secure input prompt.

### Input with Completion (List) Example

This snippet allows the user to choose a fruit with tab-completion based on a predefined list.

```python
fruits_list = ["Apple", "Apricot", "Banana", "Blackberry", "Blueberry", "Cherry", "Date"]
fruit_input_list = ui.input(
    "Enter a fruit:",
    prompt_style="#60e282",
    footer="<use tab to show completion>",
    completion=fruits_list
)
print("Fruit chosen:", fruit_input_list)
```

*Description:* This snippet allows selection from a list with auto-completion.

### Input with Completion (Dictionary) Example

This snippet demonstrates an input prompt with completion using a dictionary, where the keys are used for matching.

```python
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
```

*Description:* This snippet demonstrates an input prompt with completion using a dictionary.

### Single Select Example

This snippet shows a single select menu where the user selects one programming language.

```python
language = ["Bash", "Ruby", "Python", "Javascript"]
selected_action = ui.select(language, prompt="Select a programming language:", prompt_style="bold", return_index=False)
print("Selected programming language:", selected_action)
```

*Description:* The code above presents a single select menu.

### Multi-Select Example

This snippet presents a multi-select menu for choosing favorite colors.

```python
color_options = ["[red]Red[/]", "[green]Green[/]", "[blue]Blue[/]", "[yellow]Yellow[/]", "[purple]Purple[/]"]
selected_colors = ui.select(
    color_options,
    prompt="Select your favorite colors:",
    prompt_style="bold #39f782",
    footer="<use space and arrow keys to toggle>",
    multi_select=True,
)
print("Selected colors:", selected_colors)
```

*Description:* This snippet presents a multi-select menu.

### Confirm Example

This snippet displays a confirmation prompt to the user.

```python
confirm = ui.confirm("Do you think [bold]Rich UI[/] is cool?", footer="<press enter to confirm>")
print("Confirmed:", confirm)
```

*Description:* The code above displays a confirmation prompt to the user.

## Running the Example

The interactive demo is contained in the module and can be run as follows:

```bash
python3 -m richui.example
```

This command will display each code snippet with syntax highlighting and an accompanying description.