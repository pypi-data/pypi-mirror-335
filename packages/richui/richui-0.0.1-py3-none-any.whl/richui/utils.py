import os
import re
import sys
import tty
import rich
import termios
import textwrap
import selectors

from rich import print
from rich.live import Live
from rich.tree import Tree
from rich.text import Text
from rich.table import Table
from rich.padding import Padding
from rich.console import Group, Console

from typing import Any, Dict, List, Tuple, Union, Optional

from .config import Config

class Inputer:

    def get_key(self, timeout: Optional[float] = None) -> str:
        std = sys.stdin.fileno()
        old = termios.tcgetattr(std)
        sel = selectors.DefaultSelector()
        try:
            tty.setraw(std)
            sel.register(sys.stdin, selectors.EVENT_READ)
            if timeout is not None:
                events = sel.select(timeout)
                if not events:
                    return ''
            key: str = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)
            return key
        finally:
            sel.unregister(sys.stdin)
            termios.tcsetattr(std, termios.TCSADRAIN, old)

    def get_text(self, text: str) -> str:
        return re.sub(r'\[[^\]]*\]', '', text).strip()
    
    def get_enter(self, multi_line: bool, user_input: List[str], line_input: List[str]) -> bool:
        if multi_line:
            if not line_input:
                return True
            user_input.extend(line_input + ['\n'])
            line_input.clear()
        else:
            user_input.extend(line_input)
            line_input.clear()
            return True
        return False

class Renderer:

    def __init__(self, config: Optional[Config] = None, console: Optional[Console] = None) -> None:
        self.config: Config = config or Config()
        self.console: Console = console or Console()
    
    def __line__(self, line: int) -> None:
        sys.stdout.write(f'\x1b[{line}F')
        for _ in range(line):
            sys.stdout.write('\x1b[2K')
        sys.stdout.write('\n')
        sys.stdout.write('\x1b[0G')
        sys.stdout.flush()
    
    def __wrap__(self, text: str, width: int) -> str:
        text = re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()
        return textwrap.fill(text, width)
    
    def __tree__(
        self,
        text: Union[Dict[Any, Any], Dict[str, Any]],
        text_wrap: Optional[bool] = False,
        text_width: Optional[int] = None,
        title: Optional[str] = None,
        title_style: Optional[str] = None,
        key_style: Optional[str] = None,
        value_style: Optional[str] = None,
        guide_style: Optional[str] = None,
        padding: Optional[Tuple[int, int]] = None,
        **kwargs: Any,
    ) -> Tree:
        if title_style:
            title = f'[{title_style}]{title}[/]'
        tree: Tree = Tree(
            title or '\033[A',
            guide_style=guide_style or self.config.guide_style,
            **kwargs
        )
        def add_branch(tree: Tree, text: Dict[Any, Any], key_style: Optional[str] = None, value_style: Optional[str] = None, text_wrap: bool = False, text_width: Optional[int] = None) -> None:
            for key, value in text.items():
                if isinstance(value, dict):
                    if key_style:
                        key = f'[{key_style or self.config.key_style}]{key}[/]'
                    branch: Tree = tree.add(key)
                    add_branch(branch, value, key_style, value_style, text_wrap, text_width)
                else:
                    key = f'[{key_style or self.config.key_style}]{key}[/]'
                    branch = tree.add(key)
                    if isinstance(value, list):
                        for v in value:
                            if text_wrap:
                                v = self.__wrap__(str(v), text_width or self.config.text_width)
                            v = f'[{value_style or self.config.value_style}]{str(v)}[/]'
                            branch.add(v)
                    else:
                        value = f'[{value_style or self.config.value_style}]{str(value)}[/]'
                        branch.add(value)
        add_branch(tree, text)
        if padding or self.config.padding:
            tree = Padding(tree, padding or self.config.padding)
        return tree
    
    def __table__(
        self,
        text: Union[str, Dict[str, Any], Dict[str, int]],
        text_wrap: Optional[bool] = False,
        text_style: Optional[str] = None,
        text_width: Optional[int] = None,
        text_ljust: Optional[int] = None,
        title: Optional[str] = None,
        title_style: Optional[str] = None,
        title_justify: Optional[str] = None,
        box: Optional[str] = None,
        expand: Optional[bool] = False,
        padding: Optional[Tuple[int, int]] = None,
        show_header: Optional[bool] = False,
        **kwargs: Any,
    ) -> Table:
        
        table: Table = Table(
            box=box,
            expand=expand,
            padding=0,
            show_header=show_header,
            title=title,
            title_style=title_style or self.config.title_style,
            title_justify=title_justify if title_justify in ('left', 'right', 'center') else self.config.title_justify,
            **kwargs
        )
        if title:
            table.add_row()
        if isinstance(text, str):
            if text_wrap:
                table.add_row(self.__wrap__(text, text_width or self.config.text_width))
            else:
                table.add_row(text)
        else:
            for key, value in text.items():
                if text_wrap:
                    table.add_row(key.ljust(text_ljust or self.config.text_ljust), self.__wrap__(str(value) or '', text_width or self.config.text_width))
                else:
                    table.add_row(key.ljust(text_ljust or self.config.text_ljust), str(value) or '')
        if padding or self.config.padding:
            table = Padding(table, padding or self.config.padding)
        return table
    
    def __comptab__(
        self,
        completion_index: int,
        completion_input: Union[List[Any], List[Tuple[Any, Any]]],
        completion_padding: Tuple[int, int],
        completion_style: Optional[str] = None,
        completion_second_style: Optional[str] = None,
        completion_select_style: Optional[str] = None,
    ) -> Table:
        table: Table = Table(
            box=None,
            padding=0,
            show_header=False,
        )
        from_dict: bool = bool(completion_input and isinstance(completion_input[0], tuple))
        if from_dict:
            table.add_column(justify='left')
            table.add_column(justify='left')
        else:
            table.add_column(justify='left')
        for index, items in enumerate(completion_input):
            if from_dict:
                key = items[0]
                value = items[1]
                table.add_row(
                    Text.from_markup(f' {key} ', style=completion_style or self.config.completion_style),
                    Text.from_markup(f' {value} ', style=completion_second_style or self.config.completion_second_style),
                    style = (completion_select_style or self.config.completion_select_style) if index == completion_index else None
                )
            else:
                table.add_row(
                    Text.from_markup(f' {items} ', style=self.config.completion_style),
                    style=self.config.completion_select_style if index == completion_index else None
                )
        table = Padding(table, completion_padding)
        return table
    
    def __display__(
        self,
        prompt: Union[str],
        prompt_style: Optional[str] = None,
        cursor: Optional[str] = None,
        cursor_style: Optional[str] = None,
        footer: Optional[str] = None,
        footer_style: Optional[str] = None,
        secure: Optional[bool] = False,
        user_input: Optional[List[str]] = None,
        line_input: Optional[List[str]] = None,
        completion_index: Optional[int] = 0,
        completion_input: Optional[Union[List[Any], List[Tuple[Any, Any]]]] = None,
        completion_start: Optional[bool] = False,
        completion_padding: Optional[Tuple[int, int]] = (0, 0),
        completion_style: Optional[str] = None,
        completion_second_style: Optional[str] = None,
        completion_select_style: Optional[str] = None,
        **kwargs: Any,
    ) -> Group:
        if user_input is None:
            user_input = []
        if line_input is None:
            line_input = []
        full_input: List[str] = user_input + line_input
        text_input: str = '*' * len(full_input) if secure else ''.join(full_input)
        main_input: Text = Text()
        if prompt:
            main_input.append(Text.from_markup(f"[{prompt_style or self.config.prompt_style}]{prompt}[/] ") )
        main_input.append(text_input)
        if cursor:
            main_input.append(Text.from_markup(f"[{cursor_style or self.config.cursor_style}]{cursor}[/]"))
        if footer:
            main_input.append(Text.from_markup(f" [{footer_style or self.config.footer_style}]{footer}[/]"))
        display: List[Any] = [main_input]
        if completion_start and completion_input:
            table: Table = self.__comptab__(completion_index, completion_input, completion_padding, completion_style, completion_second_style, completion_select_style)
            display.append(table)
        return Group(*display)
    
    def __select__(
        self,
        option: List[str],
        option_show: Optional[bool] = False,
        option_style: Optional[str] = None,
        prompt: Optional[str] = None,
        prompt_style: Optional[str] = None,
        footer: Optional[str] = None,
        footer_style: Optional[str] = None,
        cursor: Optional[str] = None,
        cursor_index: Optional[int] = None,
        cursor_style: Optional[str] = None,
        checkmark: Optional[str] = None,
        checkmark_style: Optional[str] = None,
        bracket: Optional[str] = None,
        bracket_style: Optional[str] = None,
        multi_select: Optional[bool] = False,
        selected: Optional[List[bool]] = None,
        **kwargs: Any,
    ) -> Tuple[int, List[bool]]:
        if selected is None:
            selected = [False] * len(option)
    
        index: int = cursor_index if cursor_index is not None else 0
        total: int = len(option)
    
        def selector(index: int) -> int:
            line: int = 0
            if prompt:
                if option_show:
                    print(Text.from_markup(f'{prompt} {option[index]}', style=prompt_style or self.config.prompt_style))
                else:
                    print(Text.from_markup(prompt, style=prompt_style or self.config.prompt_style))
                line += 1 + prompt.count('\n')
            for i, o in enumerate(option):
                t: Text = Text()
                if i == index:
                    t.append((cursor + ' ') if cursor else (self.config.cursor + ' '), style=cursor_style or self.config.cursor_style)
                else:
                    t.append('  ')
                if multi_select:
                    b_o: str = bracket or self.config.bracket
                    b_c: str = { '(': ')', '[': ']', '{': '}' }.get(b_o, '')
                    t.append(b_o, style=bracket_style or self.config.bracket_style)
                    value: str = (checkmark or self.config.checkmark) if (i < len(selected) and selected[i]) else ' '
                    t.append(value, style=checkmark_style or self.config.checkmark_style)
                    t.append(b_c, style=bracket_style or self.config.bracket_style)
                    t.append(' ')
                if i == index:
                    o_s: str = (self.config.selected_style if (i < len(selected) and selected[i]) else self.config.selection_style)
                else:
                    o_s: str = (self.config.selected_style if (i < len(selected) and selected[i]) else (option_style or self.config.option_style))
                t.append(Text.from_markup(o, style=o_s))
                print(t)
                line += 1 + o.count('\n')
            if footer:
                print()
                print(Text.from_markup(footer, style=footer_style or self.config.footer_style))
                line += 2
            return line
    
        with self.console.capture() as capture:
            line: int = selector(index)
        print(capture.get(), end='')
        self.console.show_cursor(False)
        try:
            while True:
                key: str = Inputer().get_key()
                if key in ('\x1b[A', 'OA', '[A'):
                    index = max(0, index - 1)
                elif key in ('\x1b[B', 'OB', '[B', '\t'):
                    index = min(total - 1, index + 1)
                elif key in ('\x1b[D', '\x1b[C', ' ') and multi_select:
                    selected[index] = not selected[index]
                elif key == '\r':
                    break
                elif key == '\x03':
                    sys.stdout.write(f'\x1b[{line}A')
                    sys.stdout.write('\x1b[J')
                    sys.stdout.flush()
                    return None
                sys.stdout.write(f'\x1b[{line}A')
                sys.stdout.write('\x1b[J')
                with self.console.capture() as capture:
                    line = selector(index)
                print(capture.get(), end='')
        finally:
            self.console.show_cursor(True)
        sys.stdout.write(f'\x1b[{line}A')
        sys.stdout.write('\x1b[J')
        sys.stdout.flush()
        return (index, selected)