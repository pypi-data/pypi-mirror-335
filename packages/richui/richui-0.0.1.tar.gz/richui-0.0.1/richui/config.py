from typing import Any, Tuple, Dict

class Config:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs: Dict[str, Any] = kwargs
        self.cursor: str = kwargs.get('cursor', '➜')
        self.bracket: str = kwargs.get('bracket', '(')
        self.padding: Tuple[int, int] = kwargs.get('padding', (0, 0))
        self.newline: bool = kwargs.get('newline', False)
        self.checkmark: str = kwargs.get('checkmark', '✔')
        self.key_style: str = kwargs.get('key_style', 'white')
        self.value_style: str = kwargs.get('value_style', 'yellow')
        self.text_style: str = kwargs.get('text_style', 'white')
        self.text_width: int = kwargs.get('text_width', 50)
        self.text_ljust: int = kwargs.get('text_ljust', 20)
        self.title_style: str = kwargs.get('title_style', 'bold italic green')
        self.guide_style: str = kwargs.get('guide_style', '#666666')
        self.title_justify: str = kwargs.get('title_justify', 'left')
        self.cursor_style: str = kwargs.get('cursor_style', 'green')
        self.prompt_style: str = kwargs.get('prompt_style', 'white')
        self.option_style: str = kwargs.get('option_style', 'white')
        self.footer_style: str = kwargs.get('footer_style', 'italic #666666')
        self.bracket_style: str = kwargs.get('bracket_style', 'white')
        self.selected_style: str = kwargs.get('selected_style', 'green')
        self.selection_style: str = kwargs.get('selection_style', 'yellow')
        self.checkmark_style: str = kwargs.get('checkmark_style', 'green')
        self.completion_style: str = kwargs.get('completion_style', 'green on #666666')
        self.completion_second_style: str = kwargs.get('completion_second_style', 'white on #666666')
        self.completion_select_style: str = kwargs.get('completion_select_style', 'bold reverse')