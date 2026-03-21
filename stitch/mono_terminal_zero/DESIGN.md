```markdown
# Design System Specification: High-End Terminal Editorial

## 1. Overview & Creative North Star
### Creative North Star: "The Digital Brutalist"
This design system rejects the "softness" of modern web aesthetics in favor of a high-contrast, high-authority Terminal User Interface (TUI). It is an intentional return to the rigid, fixed-width reliability of the command line, reimagined through a premium editorial lens. 

We are not building a "retro" interface; we are building a precision instrument. The design breaks away from the "template" look by utilizing intentional asymmetry in block widths, overlapping character-based containers, and a typographic scale that treats monospaced text with the dignity of a broadsheet newspaper. Every element must feel "constructed" rather than "rendered."

## 2. Colors & Surface Logic
The palette is rooted in absolute darkness, punctuated by high-frequency neons that serve as functional beacons.

### The Palette (Material Design Mapping)
*   **Surface (Background):** `#131313` (Base), `#0e0e0e` (Lowest).
*   **Primary (Action/Focus):** `#c3f5ff` (Text), `#00e5ff` (Container/Neon Cyan).
*   **Secondary (Success/Data):** `#a8e430` (Text), `#b8f642` (Neon Green).
*   **Tertiary (Alert/Warning):** `#ffe7e2` (Text), `#ff3d00` (Alert Red).

### The "No-Line" Rule
Traditional 1px CSS borders are strictly prohibited. Sectioning must be achieved through:
1.  **Background Color Shifts:** Moving from `surface` (#131313) to `surface_container_lowest` (#0e0e0e).
2.  **Character Borders:** Using Unicode box-drawing characters (e.g., `┌`, `─`, `┐`, `│`).

### Surface Hierarchy & Nesting
Treat the UI as a series of physical "data blocks." Use the `surface_container` tiers to create depth without shadows:
*   **Level 0 (Base):** `surface` (#131313) for the main application backdrop.
*   **Level 1 (Sections):** `surface_container_low` (#1b1b1b) for major sidebars or headers.
*   **Level 2 (Active Modules):** `surface_container_high` (#2a2a2a) for focused input areas.

### Signature Textures
To add "soul" to the terminal, use subtle vertical gradients on primary CTAs—transitioning from `primary` (#c3f5ff) to `primary_container` (#00e5ff). This creates a "backlit" effect reminiscent of high-end CRT instrumentation.

## 3. Typography
Typography is the core of this system. We use a **Strict Monospace** stack (JetBrains Mono preferred) to ensure vertical and horizontal alignment across all modules.

*   **Display/Headline:** Use `display-lg` (3.5rem) for hero data or section headers. These should be set in ALL CAPS to emphasize the Brutalist authority.
*   **Body:** `body-md` (0.875rem) is the workhorse. High line-height (1.5) is essential to maintain readability against the pitch-black background.
*   **Labels:** `label-sm` (0.6875rem) in `secondary_fixed` (#b8f642) should be used for metadata, timestamps, or system status indicators.

The typographic hierarchy communicates the brand’s "Precision" identity: Larger headers act as structural anchors, while smaller labels provide the technical "read-out" feel.

## 4. Elevation & Depth (Structural Integrity)
We do not use shadows. Elevation is conveyed through **Tonal Layering** and **Character Framing**.

### The Layering Principle
Stacking containers creates hierarchy. A `surface_container_highest` block placed inside a `surface_dim` area provides a "raised" effect. The contrast between the deep black and charcoal creates a natural lift.

### The "Character Border" Framework
Where structural definition is needed, use Unicode box-drawing characters. These must use the `outline_variant` (#3b494c) color. 
*   **Ghost Borders:** For non-active containers, set the character border opacity to 20%. 
*   **Active Borders:** For focused elements, use `primary_container` (#00e5ff) at 100% opacity.

### Roundedness Scale
**Value: 0px.** 
The system prohibits rounded corners (Border Radius: 0). Every element must be a sharp, right-angled block to maintain the terminal's structural integrity.

## 5. Components

### Buttons
*   **Primary:** Solid `primary_container` block with `on_primary` text. No rounded corners. Square padding: `0.4rem` top/bottom, `1.1rem` left/right.
*   **Secondary:** Character-framed (`┌──┐`) with `primary` text.
*   **State:** On hover, the background should invert (Text becomes `primary`, Background becomes `transparent`).

### Input Fields
*   **Default:** A block of `surface_container_high` with a trailing cursor block `█`. 
*   **Focus:** Border character changes to `secondary_fixed` (#b8f642).
*   **Error:** Border character and label change to `tertiary_container` (#ffc2b3).

### Lists & Tables
*   **Divider Rule:** No horizontal lines. Use a `0.2rem` (Spacing 1) vertical gap or a subtle background shift to `surface_container_low`.
*   **Selection:** The active row is indicated by a leading character (e.g., `>`) and a full-width background highlight of `surface_container_highest`.

### Status Chips
*   **Style:** Minimalist text blocks enclosed in brackets: `[ RUNNING ]` or `[ ERROR ]`.
*   **Color:** Use `secondary` for success and `tertiary` for alerts.

## 6. Do's and Don'ts

### Do:
*   **Align to Grid:** Ensure all text and boxes align to a strict vertical grid.
*   **Use Whitespace:** Use the `20` (4.5rem) and `24` (5.5rem) spacing tokens for major section margins to prevent "information density fatigue."
*   **Intentional Asymmetry:** Align the sidebar to the right or use off-center headers to create an editorial, high-end feel.

### Don't:
*   **No Anti-aliasing issues:** Avoid font weights below 400; neons on black can "glow" and become unreadable if the weight is too light.
*   **No Shadows/Blurs:** Never use `box-shadow` or `backdrop-blur`. This system is about "Hard Surface" UI.
*   **No Smooth Transitions:** Micro-interactions (hovers/toggles) should be instant (0ms) or use a "stepped" animation to mimic terminal rendering.

## 7. Spacing Scale
The spacing scale is optimized for "Character Cell" alignment.
*   **Compact (3):** `0.6rem` - Internal padding for small blocks.
*   **Standard (5):** `1.1rem` - Standard margin between sibling elements.
*   **Structural (12):** `2.75rem` - Spacing between major layout blocks.```