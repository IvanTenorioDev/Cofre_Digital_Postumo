# Cores
DARK_BG = "#121212"  # Fundo principal escuro
DARKER_BG = "#0A0A0A"  # Fundo mais escuro para cards
BLUE_PRIMARY = "#3F8CFF"  # Azul mais vibrante atualizado
BLUE_SECONDARY = "#2563EB"  # Azul secundário atualizado
TEXT_PRIMARY = "#FFFFFF"  # Texto principal
TEXT_SECONDARY = "#94A3B8"  # Texto secundário mais suave (atualizado)
DANGER_COLOR = "#EF4444"  # Vermelho para alertas/exclusão (atualizado)
SUCCESS_COLOR = "#22C55E"  # Verde para sucesso (atualizado)
CARD_BG = "#1E1E2E"  # Fundo dos cards mais suave (atualizado)
ACCENT_COLOR = "#A855F7"  # Nova cor de destaque (roxo)
WARNING_COLOR = "#FBBF24"  # Cor de alerta (amarelo)
BORDER_COLOR = "#334155"  # Cor para bordas

# Variáveis de tema escuro
SURFACE_1 = "#1C1C1E"  # Superfície de nível 1
SURFACE_2 = "#2C2C2E"  # Superfície de nível 2
SURFACE_3 = "#3C3C3E"  # Superfície de nível 3
OVERLAY_BG = "rgba(0, 0, 0, 0.5)"  # Fundo para overlays

# Fontes
FONT_TITLE = ("Inter", 28, "bold")  # Atualizado para Inter
FONT_SUBTITLE = ("Inter", 20)
FONT_REGULAR = ("Inter", 14)
FONT_SMALL = ("Inter", 12)
FONT_COUNTER = ("Inter", 48, "bold")  # Fonte para os contadores
FONT_BUTTON = ("Inter", 13)  # Nova fonte específica para botões

# Constantes de espaçamento
PADDING_SMALL = 8
PADDING_MEDIUM = 16
PADDING_LARGE = 24
PADDING_XLARGE = 32

# Constantes de raio de borda
BORDER_RADIUS_SMALL = 4
BORDER_RADIUS_MEDIUM = 8
BORDER_RADIUS_LARGE = 12

# Estilos de Botões Modernizados
BTN_STYLE = {
    "font": FONT_BUTTON,
    "relief": "flat",
    "bd": 0,
    "padx": 20,
    "pady": 10,
    "cursor": "hand2",
    "borderwidth": 0,
    "highlightthickness": 0
}

# Estilos de Botão Principal
BTN_PRIMARY_STYLE = {
    **BTN_STYLE,
    "bg": BLUE_PRIMARY,
    "fg": TEXT_PRIMARY,
    "activebackground": BLUE_SECONDARY,
    "activeforeground": TEXT_PRIMARY
}

# Estilos de Botão Secundário
BTN_SECONDARY_STYLE = {
    **BTN_STYLE,
    "bg": SURFACE_1,
    "fg": TEXT_PRIMARY,
    "activebackground": SURFACE_2,
    "activeforeground": TEXT_PRIMARY,
    "highlightthickness": 1,
    "highlightbackground": BORDER_COLOR
}

# Estilos de Botão de Perigo
BTN_DANGER_STYLE = {
    **BTN_STYLE,
    "bg": DANGER_COLOR,
    "fg": TEXT_PRIMARY,
    "activebackground": "#DC2626",  # Vermelho mais escuro para hover
    "activeforeground": TEXT_PRIMARY
}

# Estilo para Cards com sombra
CARD_STYLE = {
    "bg": CARD_BG,
    "bd": 0,
    "highlightthickness": 1,
    "highlightbackground": BORDER_COLOR,
    "relief": "flat",
    "padx": PADDING_LARGE,
    "pady": PADDING_LARGE
}

# Estilo para entrada de texto
ENTRY_STYLE = {
    "bg": SURFACE_1,
    "fg": TEXT_PRIMARY,
    "insertbackground": TEXT_PRIMARY,
    "relief": "flat",
    "font": FONT_REGULAR,
    "bd": 0,
    "highlightthickness": 1,
    "highlightbackground": BORDER_COLOR,
    "highlightcolor": BLUE_PRIMARY
}

# Estilo para frames com sombra
FRAME_STYLE = {
    "bg": DARK_BG,
    "bd": 0,
    "highlightthickness": 0,
    "relief": "flat"
}

# Estilo para labels
LABEL_STYLE = {
    "bg": DARK_BG,
    "fg": TEXT_PRIMARY,
    "font": FONT_REGULAR,
    "padx": PADDING_SMALL,
    "pady": PADDING_SMALL
}

# Estilo para labels de título
LABEL_TITLE_STYLE = {
    **LABEL_STYLE,
    "font": FONT_TITLE,
}

# Estilo para labels de subtítulo
LABEL_SUBTITLE_STYLE = {
    **LABEL_STYLE,
    "font": FONT_SUBTITLE,
}

# Estilo para labels secundárias
LABEL_SECONDARY_STYLE = {
    **LABEL_STYLE,
    "fg": TEXT_SECONDARY,
    "font": FONT_SMALL
}

# Efeitos de animação
ANIMATION_SPEED_FAST = 150
ANIMATION_SPEED_NORMAL = 250
ANIMATION_SPEED_SLOW = 350 