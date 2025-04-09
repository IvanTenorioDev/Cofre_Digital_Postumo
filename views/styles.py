# Estilos padrão para tkinter

# Cores padrão do sistema
BG_COLOR = "#f0f0f0"  # Cinza claro padrão
TEXT_COLOR = "#000000"  # Preto
BUTTON_COLOR = "#e1e1e1"  # Cinza para botões
BUTTON_ACTIVE = "#d0d0d0"  # Cinza mais escuro para botões ativos
FRAME_COLOR = "#e9e9e9"  # Cinza para frames
HIGHLIGHT_COLOR = "#4a6984"  # Azul para destaques
ERROR_COLOR = "#ff6b6b"  # Vermelho para erros
SUCCESS_COLOR = "#51cf66"  # Verde para sucesso
WARNING_COLOR = "#fcc419"  # Amarelo para avisos

# Tamanhos e espaçamentos
PADDING_SMALL = 5
PADDING_MEDIUM = 10
PADDING_LARGE = 20

# Fonte padrão
FONT_FAMILY = "Helvetica"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_XLARGE = 18
FONT_SIZE_TITLE = 24

# Estilos de fonte
FONT_NORMAL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_TITLE = (FONT_FAMILY, FONT_SIZE_TITLE, "bold")
FONT_SUBTITLE = (FONT_FAMILY, FONT_SIZE_LARGE, "bold")
FONT_SMALL = (FONT_FAMILY, FONT_SIZE_SMALL)

# Estilos de componentes
BUTTON_STYLE = {
    "bg": BUTTON_COLOR,
    "fg": TEXT_COLOR,
    "activebackground": BUTTON_ACTIVE,
    "activeforeground": TEXT_COLOR,
    "relief": "raised",
    "font": FONT_NORMAL,
    "padx": 15,
    "pady": 5
}

BUTTON_PRIMARY_STYLE = {
    "bg": HIGHLIGHT_COLOR,
    "fg": "white",
    "activebackground": "#3b5876",
    "activeforeground": "white",
    "relief": "raised",
    "font": FONT_BOLD,
    "padx": 15,
    "pady": 5
}

BUTTON_DANGER_STYLE = {
    "bg": ERROR_COLOR,
    "fg": "white",
    "activebackground": "#e03131",
    "activeforeground": "white",
    "relief": "raised",
    "font": FONT_BOLD,
    "padx": 15,
    "pady": 5
}

ENTRY_STYLE = {
    "bg": "white",
    "fg": TEXT_COLOR,
    "relief": "sunken",
    "bd": 1,
    "highlightthickness": 1,
    "highlightbackground": "#cccccc",
    "highlightcolor": HIGHLIGHT_COLOR,
    "font": FONT_NORMAL
}

LABEL_STYLE = {
    "bg": BG_COLOR,
    "fg": TEXT_COLOR,
    "font": FONT_NORMAL
}

FRAME_STYLE = {
    "bg": BG_COLOR,
    "bd": 0
}

CARD_STYLE = {
    "bg": FRAME_COLOR,
    "highlightbackground": "#cccccc",
    "highlightthickness": 1,
    "padx": 15,
    "pady": 15
} 