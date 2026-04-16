# Design System Specification: The Academic Sentinel

## 1. Overview & Creative North Star
**Creative North Star: The Digital Curator**
This design system rejects the "SaaS dashboard" aesthetic in favor of a high-end, editorial experience. It is designed to feel like a bespoke academic journal—authoritative, quiet, and deeply analytical. We achieve this by moving away from rigid grids and 1px borders, opting instead for **Intentional Asymmetry** and **Tonal Layering**. The layout should feel "curated," where whitespace is treated as a premium functional element that allows complex pedagogical data to breathe.

## 2. Colors & Surface Architecture
The palette is rooted in a deep, intellectual foundation. We use color not just for branding, but to define the physical geography of the interface.

### The Palette (Material Design Mapping)
*   **Primary Hierarchy:** `primary` (#041627) for high-level authority; `primary_container` (#1a2b3c) for structural depth.
*   **Accentuation:** `secondary` (#735c00) and `secondary_fixed_dim` (#e9c349) represent "Scholar Gold"—used exclusively for highlights, critical insights, and milestones.
*   **Foundation:** `background` (#f8f9fa) and `surface_container_lowest` (#ffffff).

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to section content. Boundaries must be defined through:
1.  **Background Shifts:** Placing a `surface_container_low` card against a `surface` background.
2.  **Tonal Transitions:** Using subtle shifts in the surface-container tiers to denote nesting.

### Glass & Gradient Signature
To move beyond "flat" design, apply **Glassmorphism** to floating elements (e.g., navigation rails or hovering filters). 
*   **Technique:** Use `surface` at 80% opacity with a 12px-20px backdrop blur.
*   **CTAs:** Use a subtle linear gradient (from `primary` to `primary_container`) at a 135-degree angle to give buttons a weighted, tactile feel that flat colors lack.

## 3. Typography: Editorial Authority
The type system creates a dialogue between tradition (the serif) and modern utility (the sans-serif).

*   **The Authority (Noto Serif):** Used for all `display` and `headline` roles. This font carries the weight of institutional knowledge. Increase letter-spacing slightly for `display-lg` to create an "opened-up" luxury feel.
*   **The Utility (Inter & Public Sans):** Used for `body` and `labels`. Inter provides a neutral, high-readability canvas for teacher-facing data. 
*   **Hierarchy Note:** Always pair a `headline-md` (Serif) with a `title-sm` (Sans-Serif) to create a clear "Publication Header" look.

## 4. Elevation & Depth: Tonal Layering
We do not use elevation to make things "pop"; we use it to establish intellectual hierarchy.

*   **The Layering Principle:** Stacking is done via color. A `surface_container_highest` element represents a "Deep Insight" or "Focus Area," while `surface_container_lowest` represents the "Standard Document."
*   **Ambient Shadows:** If a card must float, use a "Sentinel Shadow": `Color: on_surface (at 4% opacity)`, `Blur: 32px`, `Y-Offset: 8px`. It should feel like a soft glow of light, not a drop shadow.
*   **The Ghost Border:** For high-density data tables where separation is critical, use a "Ghost Border": `outline_variant` at 15% opacity. Never use 100% opacity.

## 5. Components & Primitive Styling

### Modern Cards & Containers
*   **Forbid Dividers:** Do not use horizontal lines to separate card content. Use vertical whitespace (from the `xl` or `lg` scale) to create "invisible gutters."
*   **The Node Motif:** Incorporate subtle "graph and node" accents in the corners of cards using `outline_variant` at 10% opacity—resembling architectural blueprints.

### Action Elements (Buttons & Chips)
*   **Primary Button:** `primary` background, `on_primary` text, `roundness-md`. Add a subtle `primary_container` inner shadow (top-down) for a pressed-ink effect.
*   **Status Badges (Badges/Chips):**
    *   *Likely Missed:* `error_container` background with `on_error_container` text.
    *   *Covered Abroad:* `secondary_container` background with `on_secondary_container` text.
    *   *Styling:* Use `roundness-full` and `label-sm` (Public Sans) in all-caps with +5% tracking for a professional "stamp" feel.

### Data Visualization & Tables
*   **The "Open Table" Look:** No outer borders. The table head (`surface_container_high`) should have a slight `roundness-sm` on the top corners only. 
*   **Row Interaction:** On hover, change the row background to `surface_container_low` rather than adding a border.

### Academic Inputs
*   **Text Fields:** Use the "Underline and Fill" style rather than an enclosed box. Fill with `surface_container`, and use a `primary` 2px bottom border only on focus. This mimics a researcher’s ledger.

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical margins. A wider left margin (editorial style) creates space for "Node" background motifs.
*   **Do** use the Scholar Gold (`secondary`) sparingly. It is a "laser pointer" for the eye—use it only for the most critical gap in the data.
*   **Do** utilize `surface_bright` for interactive tooltips to make them feel like light-boxes appearing over the scholarly text.

### Don’t:
*   **Don’t** use pure black (#000000). Use `primary` or `on_surface` to maintain the sophisticated navy/off-white balance.
*   **Don’t** use standard "Material Design" shadows. They are too aggressive for this academic context. Stick to tonal shifts.
*   **Don’t** crowd the screen. If a teacher is analyzing a "Gap," the UI should provide a "Deep Work" environment—limit the number of competing cards on a single screen.