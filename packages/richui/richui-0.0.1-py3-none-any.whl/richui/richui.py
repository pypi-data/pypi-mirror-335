from .config import Config
from .utils import Inputer, Renderer

from typing import Union, Optional, List, Dict, Any, Tuple

from rich.console import Console
from rich.live import Live
from rich import print

import time

class Richui:

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config: Config = config or Config()
        self.console: Console = Console()
        self.inputer: Inputer = Inputer()
        self.renderer: Renderer = Renderer(self.config, self.console)
    
    def tree(
        self,
        text: Union[str, Dict[Any, Any]],
        text_wrap: Optional[bool] = False,
        text_width: Optional[int] = None,
        title: Optional[str] = None,
        title_style: Optional[str] = None,
        key_style: Optional[str] = None,
        value_style: Optional[str] = None,
        guide_style: Optional[str] = None,
        padding: Optional[Tuple[int, int]] = None,
        newline: Optional[bool] = False,
        **kwargs: Any,
    ) -> None:
        tree = self.renderer.__tree__(
            text, text_wrap, text_width, title, title_style, key_style,
            value_style, guide_style, padding, **kwargs
        )
        if newline:
            print()
            print(tree)
            print()
        else:
            print(tree)
    
    def table(
        self,
        text: Union[str, Dict[Any, Any]],
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
        newline: Optional[bool] = False,
        show_header: Optional[bool] = False,
        **kwargs: Any,
    ) -> None:
        table = self.renderer.__table__(
            text, text_wrap, text_style, text_width, text_ljust,
            title, title_style, title_justify, box, expand, padding,
            show_header, **kwargs
        )
        if newline:
            print()
            print(table)
            print()
        else:
            print(table)
    
    def input(
        self,
        prompt: str,
        prompt_style: Optional[str] = None,
        footer: Optional[str] = None,
        footer_style: Optional[str] = None,
        cursor: Optional[str] = None,
        cursor_style: Optional[str] = None,
        secure: Optional[bool] = False,
        multi_line: Optional[bool] = False,
        completion: Optional[Union[List[Any], Dict[Any, Any]]] = None,
        completion_style: Optional[str] = None,
        completion_second_style: Optional[str] = None,
        completion_select_style: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        user_input: List[str] = []
        line_input: List[str] = []
        completion_index: int = 0
        completion_input: Optional[Union[List[Any], List[Tuple[Any, Any]]]] = None
        completion_start: bool = False
        cursor = cursor or '_' 

        with Live(auto_refresh=False, console=self.console, transient=True) as live:
            try:
                self.console.show_cursor(False)
                while True:
                    completion_padding: Tuple[int, int] = (0, len(prompt)) if prompt and len(prompt) < 30 else (0, 0)
                    display = self.renderer.__display__(
                        prompt,
                        prompt_style,
                        cursor,
                        cursor_style,
                        footer,
                        footer_style,
                        secure,
                        user_input,
                        line_input,
                        completion_index,
                        completion_input,
                        completion_start,
                        completion_padding,
                        completion_style,
                        completion_second_style,
                        completion_select_style
                    )
                    live.update(display)
                    live.refresh()
                    keys: str = self.inputer.get_key()
                    if not keys:
                        continue
                    
                    if completion_start and completion_input:
                        if keys in ('\x1b[A', '\x1bOA', '[A'):
                            completion_index = (completion_index - 1) % len(completion_input)
                            continue
                        elif keys in ('\x1b[B', '\x1bOB', '[B', '\t'):
                            completion_index = (completion_index + 1) % len(completion_input)
                            continue
                        elif keys in ('\r', '\n'):
                            main = completion_input[completion_index]
                            main = main[0] if isinstance(main, tuple) else main
                            line_input = list(main)
                            completion_start = False
                            completion_input = None
                            continue
                        else:
                            completion_start = False
                            completion_input = None
    
                    if keys == '\t' and completion is not None:
                        text_input: str = ''.join(user_input + line_input)
                        if isinstance(completion, dict):
                            find = [(k, v) for k, v in completion.items() if k.startswith(text_input)]
                        else:
                            find = [comp for comp in completion if comp.startswith(text_input)]
                        if len(find) == 1:
                            main = find[0]
                            main = main[0] if isinstance(main, tuple) else main
                            if len(main) > len(text_input):
                                remaining = main[len(text_input):]
                                line_input.extend(remaining)
                            continue
                        elif len(find) > 1:
                            completion_index = 0
                            completion_input = find
                            completion_start = True
                            continue
                        else:
                            completion_input = None
                            continue
    
                    if keys in ('\r', '\n'):
                        if self.inputer.get_enter(multi_line, user_input, line_input):
                            break
                    elif keys == '\x7f':
                        if line_input:
                            line_input.pop()
                    elif keys == '\x03':
                        return ''
                    elif keys.isprintable():
                        line_input.append(keys)
            finally:
                self.console.show_cursor(True)
    
        display = self.renderer.__display__(
            prompt,
            prompt_style,
            '',
            cursor_style,
            footer,
            footer_style,
            secure,
            user_input,
            line_input,
            0,
            None,
            False,
            (0, len(prompt)) if prompt else (0, 0),
        )
        with self.console.capture() as capture:
            self.console.print(display)
        line = capture.get().count('\n')
        self.renderer.__line__(line)
        return ''.join(user_input + line_input).strip()
    
    def select(
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
        return_index: Optional[bool] = False,
        **kwargs: Any,
    ) -> Union[int, List[str], List[int]]:
        selected: List[bool] = [False] * len(option)
        result = self.renderer.__select__(
            option,
            option_show,
            option_style,
            prompt,
            prompt_style,
            footer,
            footer_style,
            cursor,
            cursor_index,
            cursor_style,
            checkmark,
            checkmark_style,
            bracket,
            bracket_style,
            multi_select,
            selected,
            **kwargs,
        )
        index: int
        selected = []
        if result is None:
            return result
        if isinstance(result, tuple):
            index, selected = result
        if multi_select:
            if return_index:
                return [i for i, s in enumerate(selected) if s]
            else:
                return [self.inputer.get_text(option[i]) for i, s in enumerate(selected) if s]
        else:
            return index if return_index else self.inputer.get_text(option[index])
    
    def confirm(
        self,
        prompt: str,
        prompt_style: Optional[str] = None,
        no_text: Optional[str] = 'No',
        yes_text: Optional[str] = 'Yes',
        cursor: Optional[str] = None,
        cursor_index: Optional[int] = None,
        cursor_style: Optional[str] = None,
        footer: Optional[str] = None,
        footer_style: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        option: List[str] = [yes_text, no_text]
        select_: List[bool] = [False] * len(option)
        result = self.renderer.__select__(
            option=option,
            prompt=prompt,
            prompt_style=prompt_style,
            footer=footer,
            footer_style=footer_style,
            cursor=cursor,
            cursor_index=cursor_index,
            cursor_style=cursor_style,
            selected=select_,
        )
        if result is None:
            return result
        index, _ = result if isinstance(result, tuple) else (0, select_)
        return index == 0