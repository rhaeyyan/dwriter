"""Theme definitions for dwriter TUI.

This module contains all available themes for the application,
defined using Textual's Theme object for consistent switching.
"""

from textual.theme import Theme

# Cyberpunk theme - neo-cyan synth_term palette (default)
CYBERPUNK = Theme(
    name="cyberpunk",
    primary="#00E5FF",
    secondary="#00E5FF",
    success="#CCFF00",
    warning="#FFD700",
    error="#FF003C",
    accent="#00E5FF",
    foreground="#ffffff",
    background="#0d0f18",
    surface="#1a1e29",
    panel="#111111",
)

# Dark theme - softer, more muted colors
DARK = Theme(
    name="dark",
    primary="#569cd6",
    secondary="#ce9178",
    success="#6a9955",
    warning="#d7ba7d",
    error="#f44747",
    accent="#569cd6",
    foreground="#d4d4d4",
    background="#1e1e1e",
    surface="#1e1e1e",
    panel="#252526",
)

# Light theme - clean, professional appearance
LIGHT = Theme(
    name="light",
    primary="#0066cc",
    secondary="#6c4c28",
    success="#388e3c",
    warning="#f57c00",
    error="#d32f2f",
    accent="#0066cc",
    foreground="#333333",
    background="#ffffff",
    surface="#ffffff",
    panel="#f5f5f5",
)

# Minimal theme - high contrast, monochrome-focused
MINIMAL = Theme(
    name="minimal",
    primary="#808080",
    secondary="#606060",
    success="#4a4a4a",
    warning="#5a5a5a",
    error="#3a3a3a",
    accent="#808080",
    foreground="#e0e0e0",
    background="#0a0a0a",
    surface="#1a1a1a",
    panel="#202020",
)

# Catppuccin Mocha - popular dark theme
CATPPUCCIN = Theme(
    name="catppuccin",
    primary="#cba6f7",
    secondary="#89b4fa",
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
    accent="#cba6f7",
    foreground="#cdd6f4",
    background="#11111b",
    surface="#1e1e2e",
    panel="#181825",
)

# Gruvbox Dark - warm, earthy tones
GRUVBOX = Theme(
    name="gruvbox",
    primary="#d3869b",
    secondary="#83a598",
    success="#98971a",
    warning="#d79921",
    error="#cc241d",
    accent="#d3869b",
    foreground="#ebdbb2",
    background="#1d2021",
    surface="#282828",
    panel="#1d2021",
)

# Nord - cool, arctic-inspired palette
NORD = Theme(
    name="nord",
    primary="#88c0d0",
    secondary="#81a1c1",
    success="#a3be8c",
    warning="#ebcb8b",
    error="#bf616a",
    accent="#88c0d0",
    foreground="#eceff4",
    background="#2e3440",
    surface="#2e3440",
    panel="#3b4252",
)

# Dracula - popular dark theme with vibrant colors
DRACULA = Theme(
    name="dracula",
    primary="#bd93f9",
    secondary="#6272a4",
    success="#50fa7b",
    warning="#f1fa8c",
    error="#ff5555",
    accent="#bd93f9",
    foreground="#f8f8f2",
    background="#282a36",
    surface="#282a36",
    panel="#44475a",
)

# Jamboree - Complete high-contrast palette
JAMBOREE = Theme(
    name="jamboree",
    primary="#FE81D4",    # Hot Pink
    secondary="#1A05A2",  # Deep Blue (Highlight only)
    success="#ABDADC",    # Light Blue
    warning="#FBC3C1",    # Peach
    error="#FF5555",      # Vibrant Red (Distinct from Pink)
    accent="#FE81D4",     # Hot Pink
    foreground="#ffffff", # White (Primary text for clarity)
    background="#0a0a0f", # Obsidian Blue
    surface="#161625",    # Dark Navy Elevation
    panel="#1c1c3c",      # High-Contrast Navy (For Log entries and Todo board)
)

# Ruby - "Cyberpunk Edition" (Red-Dominant Neon HUD)
RUBY = Theme(
    name="ruby",
    primary="#D53E0F",    # Neon Ruby Red
    secondary="#4a0e0e",  # Deep Merlot
    success="#4a0e0e",    # Deep Merlot (Level 1 Activity)
    warning="#D53E0F",    # Neon Ruby Red (Level 2 Activity)
    error="#A6E3A1",      # Terminal Green (Level 4 Activity)
    accent="#FCBF49",     # Neon Gold (Level 3 Activity)
    foreground="#EED9B9", # Pale Cream (High readability)
    background="#080202", # Obsidian Wine (Deep-dark depth)
    surface="#1a0505",    # Deep Wine (Level 0 Activity)
    panel="#1a0505",      # Deep Wine Panels
)

# Dictionary mapping theme names to Theme objects
THEMES = {
    "cyberpunk": CYBERPUNK,
    "dark": DARK,
    "light": LIGHT,
    "minimal": MINIMAL,
    "catppuccin": CATPPUCCIN,
    "gruvbox": GRUVBOX,
    "nord": NORD,
    "dracula": DRACULA,
    "jamboree": JAMBOREE,
    "ruby": RUBY,
}
# Theme sorting logic: Prioritize Cyberpunk, Jamboree, Ruby; then alphabetical
_PRIORITY_THEMES = ["cyberpunk", "jamboree", "ruby"]
_OTHER_THEMES = sorted([n for n in THEMES.keys() if n not in _PRIORITY_THEMES])

# List of theme names for Select widget options
_THEME_ORDER = _PRIORITY_THEMES + _OTHER_THEMES
THEME_OPTIONS = [(n.capitalize(), n) for n in _THEME_ORDER]
