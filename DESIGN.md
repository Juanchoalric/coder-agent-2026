---
name: Dashboard de Ventas 2026
description: Internal sales dashboard in Apple-style minimalism - calm, precise, all signal, on a neutral ground with one Apple blue accent.
colors:
  accent: "#0071e3"
  accent-text: "#0060df"
  ground: "#f5f5f7"
  surface: "#ffffff"
  ink: "#1d1d1f"
  ink-secondary: "#6e6e73"
  hairline: "rgba(0, 0, 0, 0.06)"
  hairline-strong: "rgba(0, 0, 0, 0.12)"
  tooltip: "#1d1d1f"
  chart-blue: "#0071e3"
  chart-green: "#34c759"
  chart-orange: "#ff9500"
  chart-pink: "#ff2d55"
  chart-purple: "#5e5ce6"
  chart-cyan: "#64d2ff"
  chart-yellow: "#ffd60a"
  chart-violet: "#af52de"
  chart-teal: "#30b0c7"
  chart-gray: "#8e8e93"
  dark-bg: "#000000"
  dark-surface: "#1c1c1e"
  dark-ink: "#f5f5f7"
  dark-ink-secondary: "#a1a1a6"
  dark-ink-tertiary: "#98989f"
  dark-hairline: "rgba(255, 255, 255, 0.12)"
  dark-hairline-strong: "rgba(255, 255, 255, 0.2)"
  dark-accent: "#0a84ff"
  dark-accent-strong: "#409cff"
  dark-accent-soft: "rgba(10, 132, 255, 0.16)"
  dark-header-bg: "rgba(0, 0, 0, 0.72)"
  dark-table-hover: "#2c2c2e"
  dark-chart-grid: "rgba(255, 255, 255, 0.1)"
  dark-chart-tick: "#a1a1a6"
  dark-tooltip-bg: "#f5f5f7"
  dark-tooltip-fg: "#1d1d1f"
  dark-doughnut-border: "#1c1c1e"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(1.75rem, 2.4vw, 2.375rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.03em"
    fontFeature: '"tnum" 1, "cv11" 1'
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    letterSpacing: "-0.03em"
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    letterSpacing: "0.02em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    letterSpacing: "-0.01em"
    fontFeature: '"tnum" 1, "cv11" 1'
  table-header:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.04em"
rounded:
  card: "18px"
  control: "10px"
  page: "8px"
  bar: "7px"
  pill: "999px"
spacing:
  card-pad: "1.25rem 1.375rem"
  section-gap: "1rem"
  kpi-stack: "0.375rem"
  cell-x: "0.875rem"
  cell-y: "0.625rem"
components:
  surface-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  kpi-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "1.25rem 1.375rem"
  period-pill:
    backgroundColor: "rgba(0, 113, 227, 0.14)"
    textColor: "{colors.accent-text}"
    rounded: "{rounded.pill}"
    padding: "0.375rem 0.875rem"
    typography: "{typography.label}"
  table-input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.5rem 0.75rem"
  pagination-button:
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.page}"
    padding: "0.25rem 0.625rem"
  pagination-button-current:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.page}"
    padding: "0.25rem 0.625rem"
  theme-toggle:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.pill}"
    size: "2.25rem"
  table-header-cell:
    textColor: "{colors.ink-secondary}"
    typography: "{typography.table-header}"
---

# Design System: Dashboard de Ventas 2026

## Overview

**Creative North Star: "The Quiet System Page"**

An internal sales instrument that reads like an Apple system page: calm, precise, all signal. It is a data-first utility for analysts and project managers who validate sales numbers before they move up the chain, so the visual system is engineered to disappear around the data. The world is built on a neutral gray ground with white surfaces, one Apple blue accent reserved for interactive and focal moments, hairline-only separation, and a frosted sticky header as its one signature surface.

Density is low and deliberate: a single KPI row, then quiet charts, then the transaction table, each in its own white card with a continuous 18px radius. Nothing competes with the numbers. The system refuses the dense bordered-card dashboard cliché and substitutes soft offset shadows and hairlines for weight. All figures render in tabular numerals with tight tracking so columns and values align as data.

Motion is deliberately restrained - exactly one authored moment. The KPI row reveals on load, staggered by column, and that animation is the only one in the system; it is fully disabled under `prefers-reduced-motion`. This is an Operate-mode, Restrained-strategy world: neutral + one accent, no decorative surface.

**Key Characteristics:**
- One Apple blue accent (#0071e3) on a neutral ground (#f5f5f7)
- Frosted sticky header as the signature surface (blur, not shadow)
- Hairline-only separation; no heavy or dense borders
- Continuous 18px radius on all surfaces
- SF system font stack with tabular numerals and tight tracking
- One authored motion moment (staggered KPI reveal, reduced-motion aware)
- Data held in white surface cards with soft ambient shadows
- Dark mode restyles the same world on an inverted True Black (#000000) ground with a brighter Apple blue (#0a84ff)

## Colors

The palette is a neutral gray scale plus one Apple blue accent, with the full Apple system set reserved for data encoding inside charts.

### Primary

- **Apple Blue** (#0071e3): The single interface accent. Used for the active pagination page, chart bars that carry the series accent, the period pill tint, and all focus rings. It appears sparingly - selection, focus, and the one factual accent.
- **Deep Apple Blue** (#0060df): Accent-colored text on tinted pills. The pill sits on a blue tint (rgba(0, 113, 227, 0.14)), so its text and dot are darkened from #0071e3 to #0060df for contrast (period pill in the header).

### Neutral

- **Cloud Gray** (#f5f5f7): Page ground and table row hover. The light, quiet field everything sits on.
- **Pure Surface** (#ffffff): Card, input, and footer backgrounds. All data lives on white.
- **Ink** (#1d1d1f): Primary text - KPI values, table cells, body copy. Near-black, the loudest color in the system.
- **Secondary Ink** (#6e6e73): Everything that must not shout - labels, sub-values, card titles, chart ticks and legend text, table headers, and meta info.
- **Hairline** (rgba(0, 0, 0, 0.06)): The default separator: card borders, table row rules, header bottom rule, chart gridlines.
- **Strong Hairline** (rgba(0, 0, 0, 0.12)): The emphasized separator: form control borders and the table header underline.
- **Tooltip Ink** (#1d1d1f): Chart tooltip background, with #f5f5f7 text - the tooltip inverts the ground/ink relationship.

### Chart Palette (Apple System Set)

A 10-color set used only for data encoding inside charts: Apple Blue #0071e3, System Green #34c759, System Orange #ff9500, System Pink #ff2d55, System Indigo #5e5ce6, System Cyan #64d2ff, System Yellow #ffd60a, System Purple #af52de, System Teal #30b0c7, System Gray #8e8e93. Single-series charts borrow a single hue from this set (monthly = blue #0071e3, top products = indigo #5e5ce6, country = green #34c759, age = orange #ff9500); multi-series charts cycle the full set.

### Dark Theme

A full dark-mode extension of the same world, reached through the theme toggle in the frosted header. The ground/ink relationship inverts - the ground drops to True Black (#000000) and surfaces to Dark Surface (#1c1c1e) - and the accent shifts to the brighter Dark Apple Blue (#0a84ff) so it stays luminous on near-black. Every light token has a direct dark counterpart; the roles are unchanged.

- **True Black** (#000000): Dark-mode page ground.
- **Dark Surface** (#1c1c1e): Card, input, and footer surfaces in dark mode.
- **Dark Ink** (#f5f5f7): Primary text in dark mode - KPI values, table cells, body copy.
- **Dark Secondary Ink** (#a1a1a6): Labels, card titles, chart ticks, table headers, and meta in dark mode.
- **Dark Tertiary Ink** (#98989f): The quietest supporting text in dark mode.
- **Dark Hairline** (rgba(255, 255, 255, 0.12)): Default separator in dark mode - card borders, row rules, chart gridlines.
- **Dark Strong Hairline** (rgba(255, 255, 255, 0.2)): Emphasized separator in dark mode - form controls and the table header underline.
- **Dark Apple Blue** (#0a84ff): The dark-mode interface accent - active pagination, chart series accent, focus rings.
- **Dark Deep Apple Blue** (#409cff): Accent-colored text on tinted pills in dark mode.
- **Dark Accent Soft** (rgba(10, 132, 255, 0.16)): The period pill tint in dark mode.
- **Dark Header** (rgba(0, 0, 0, 0.72)): The frosted header backdrop in dark mode.
- **Dark Table Hover** (#2c2c2e): Row hover tint in dark mode.
- **Dark Chart Grid** (rgba(255, 255, 255, 0.1)): Chart gridlines in dark mode.
- **Dark Chart Tick** (#a1a1a6): Chart tick and legend text in dark mode.
- **Dark Tooltip** (#f5f5f7 background, #1d1d1f text): The tooltip inverts again - light surface, dark text - so it stays the inverse of its surroundings.
- **Dark Doughnut Border** (#1c1c1e): Doughnut segment separators in dark mode.
- **Dark Shadows**: `0 4px 16px rgba(0, 0, 0, 0.45), 0 1px 2px rgba(0, 0, 0, 0.3)` at rest; `0 10px 28px rgba(0, 0, 0, 0.55), 0 2px 6px rgba(0, 0, 0, 0.35)` on hover - deeper than light mode because a black shadow disappears on a black ground.

The Apple system chart palette is unchanged across themes; only the chart chrome (ticks, gridlines, tooltip, doughnut segment borders) restyles in dark mode.

### Named Rules

**The One-Accent Rule.** Interface chrome carries exactly one accent: Apple Blue (#0071e3). The Apple system palette may appear only inside chart canvases, where color encodes data, never in UI chrome.

**The Contrast Fix Rule.** Accent-colored text never sits directly on the raw accent. On tinted surfaces (the period pill), text drops to Deep Apple Blue (#0060df); on solid accent surfaces (the active pagination page), text is white.

**The Theme Continuity Rule.** Dark mode is a strict restyle of the pinned world: the same continuous 18px radius, the same hairline-only separation, the same single accent (just brighter), and no new motion. Every dark token maps 1:1 to a light token with the same role.

## Typography

**Display Font:** System SF stack (`-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`)
**Body Font:** Same SF stack; the system supplies no display/body pairing, one stack carries the whole interface.
**Numeric Face:** The same stack with `font-feature-settings: "tnum" 1, "cv11" 1` - tabular numerals for aligned data, alternate figures via cv11.

**Character:** One quiet humanist sans stack in near-black on gray, with tight tracking (-0.01em body, -0.03em on values) and tabular numerals everywhere so columns and figures align like ledger rows. Hierarchy is expressed through size, weight, and gray, not through font changes.

### Hierarchy

- **Display / KPI Value** (weight 700, `clamp(1.75rem, 2.4vw, 2.375rem)`, line-height 1.05, -0.03em): The four decisive numbers. Tabular-numeral, near-black, larger and heavier than anything else on screen.
- **Title / Header** (weight 600, 1.25rem, -0.03em, responsive to 1.5rem): The dashboard title in the frosted header.
- **Label** (weight 600, 0.8125rem, +0.02em): KPI labels ("Total ventas (USD)", etc.) in Secondary Ink, plus the period pill text. Card titles use the same size/weight at -0.01em tracking.
- **Body** (default weight, default size, -0.01em, tnum + cv11): Table cells, header subline, and supporting text in Ink.
- **Table Header** (weight 600, 0.75rem, +0.04em, uppercase): The only uppercase text in the system - DataTable column heads in Secondary Ink over a Strong Hairline rule.
- **Sub-text** (0.75rem): KPI sub-values and the footer; secondary context in Secondary Ink. DataTable info and length labels sit at 0.8125rem.

### Named Rules

**The Data Face Rule.** Every figure in the dashboard - KPI values, table cells, chart ticks - renders in tabular numerals (tnum 1). Numbers align as data; nothing wobbles.

**The Quiet Label Rule.** Labels are small (0.8125rem), semibold, and gray (Secondary Ink #6e6e73). They state what the value means and never compete with it. The single uppercase exception is the table header, and it stays at 0.75rem.

## Layout

One centered column, max-width 7xl (1280px), padded `px-4` (1rem) with `sm:px-6` (1.5rem) and `lg:px-8` (2rem). The page scrolls vertically in a fixed order defined by the first viewport: frosted header, KPI row, chart grid, transaction table, footer. Section rhythm is `1.5rem` (mt-6) between sections and `1rem` (gap-4) between cards within a grid.

- **KPI row:** 1 column on mobile, 2 on `sm` (640px), 4 on `lg` (1024px). Each card pads `1.25rem 1.375rem` with an internal vertical rhythm of `0.375rem` between label, value, and sub.
- **Chart grid:** 1 column on mobile, 2 on `lg` (1024px). The age-bucket chart spans both columns. Chart boxes keep a `min-height: 260px` with a `max-height: 240px` canvas so the grid stays even.
- **Table section:** full-width card with `1.25rem` padding and a horizontal scroll wrapper for narrow viewports.
- **Header:** sticky at top (z-index 40), content in the same 7xl container, `1rem` vertical padding, wrapping flex that lets the period pill drop below the title on small screens.
- **Footer:** `1rem` padding, wrapping flex with `1.5rem` column gaps; meta reads as a quiet row of run/matching/period facts in `0.75rem` Secondary Ink.

Density is intentionally low: generous gutters, one card per metric, nothing in a grid tighter than 4 columns.

## Elevation & Depth

A hybrid system: cards are defined by hairline borders plus soft, low-opacity ambient shadows, and the one raised surface is the frosted header, which conveys depth through backdrop blur rather than shadow. The header background is `rgba(245, 245, 247, 0.72)` with `backdrop-filter: saturate(180%) blur(20px)`, so scrolling content softly melts beneath it.

### Shadow Vocabulary

- **Card at rest** (`0 4px 16px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.04)`): All surfaces at rest - KPI cards, chart cards, table card, footer. Ambient, not structural; the hairline border does the structural work.
- **Card lifted** (`0 10px 28px rgba(0, 0, 0, 0.09), 0 2px 6px rgba(0, 0, 0, 0.05)`): KPI cards on hover, paired with `translateY(-2px)`.
- **Focus ring** (`0 0 0 3px rgba(0, 113, 227, 0.18)`): DataTable search and length controls on focus, in addition to their border switching to the accent.
- **Card at rest (dark)** (`0 4px 16px rgba(0, 0, 0, 0.45), 0 1px 2px rgba(0, 0, 0, 0.3)`): All surfaces at rest in dark mode.
- **Card lifted (dark)** (`0 10px 28px rgba(0, 0, 0, 0.55), 0 2px 6px rgba(0, 0, 0, 0.35)`): KPI cards on hover in dark mode.

### Named Rules

**The Flat-By-Default Rule.** Surfaces are flat at rest. Elevation appears only as a response to state - the KPI card hover lift, the focus ring - and the header's blur is its resting state.

**The Single-Motion Rule.** Exactly one authored animation exists: the KPI reveal (0.5s `cubic-bezier(0.22, 1, 0.36, 1)`, fade + 10px rise), staggered at 60/120/180ms per card. It is disabled entirely under `prefers-reduced-motion`. Hover transitions (KPI cards 0.28s `cubic-bezier(0.22, 1, 0.36, 1)`, pagination 0.15s ease) are the only other motion.

## Shapes

Continuous, gentle geometry. All surfaces share one radius - `--radius: 18px` - giving the dashboard a soft, unified silhouette: KPI cards, chart cards, the table card, and the footer. Radius varies only by function at smaller scales:

- Surfaces and cards: 18px
- Period pill and status dot: 999px (fully round)
- Form controls (search input, length select): 10px
- Pagination buttons: 8px
- Chart bars: 7px
- Chart tooltips: 10px
- Keyboard focus outline: 4px
- Doughnut charts: a ring silhouette at 68% cutout with 2px white segment borders

Borders are hairlines only: `rgba(0, 0, 0, 0.06)` by default, `rgba(0, 0, 0, 0.12)` for the emphasized header rule and form controls. The table draws no cell borders - only hairline bottom rules per row.

### Named Rules

**The Continuous Radius Rule.** One radius (18px) is the system's form language for all surfaces. Smaller radii exist only where the geometry is small enough to need them; they never compete with the 18px surface silhouette.

**The Hairline-Only Rule.** Separation is achieved with hairlines, never weight. The strongest rule in the system is `rgba(0, 0, 0, 0.12)` at the table header.

## Components

### Frosted Header
- **Style:** Sticky at top (z-index 40) with `background: rgba(245, 245, 247, 0.72)` and `backdrop-filter: saturate(180%) blur(20px)`; `1px` Hairline bottom rule.
- **Content:** Title (weight 600, tracking -0.03em) with a Secondary Ink subline (sources + generation time), and the period pill on the right.
- **State:** No hover states; it stays calm and translucent over all content.

### Period Pill
- **Shape:** Fully round pill (999px).
- **Style:** Tinted accent background `rgba(0, 113, 227, 0.14)`, Deep Apple Blue (#0060df) text and 0.5rem dot, 0.8125rem semibold, nowrap, `0.5rem` internal gap between dot and label.

### Surface Card
- **Corner Style:** Continuous 18px radius.
- **Background:** Pure Surface (#ffffff).
- **Border:** 1px Hairline (rgba(0, 0, 0, 0.06)).
- **Shadow:** Card at rest (see Elevation).
- **Internal Padding:** `1.25rem 1.375rem` for chart boxes; `1.25rem` for the table section; `1rem` for the footer.
- **Card Title:** Secondary Ink, 0.8125rem semibold, -0.01em tracking, with `0.75rem` margin below.

### KPI Card
- **Corner Style:** 18px radius.
- **Background:** Pure Surface, 1px Hairline border, card-at-rest shadow.
- **Internal Padding:** `1.25rem 1.375rem`.
- **Hierarchy:** label (Secondary Ink, 0.8125rem semibold, +0.02em) → value (Display, tabular, near-black) → sub (0.75rem Secondary Ink), each separated by `0.375rem`.
- **Hover:** Lifts `translateY(-2px)` and swaps to the card-lifted shadow over 0.28s `cubic-bezier(0.22, 1, 0.36, 1)`.
- **Load state:** Reveals with the single stagger animation (0ms / 60ms / 120ms / 180ms), suppressed under `prefers-reduced-motion`.

### Charts
- **Container:** Each chart lives in a surface card, `min-height: 260px`, canvas capped at `max-height: 240px`.
- **Global defaults (Chart.js):** SF font stack, 12px, Secondary Ink text; hairline (rgba(0, 0, 0, 0.06)) gridlines with no axis border; legend as 8px round point-style markers.
- **Tooltip:** Ink (#1d1d1f) background, Cloud Gray (#f5f5f7) text, 10px padding, 10px radius, 4px box padding, with the value formatted as USD.
- **Bars:** 7px radius on bar ends, `maxBarThickness` capped per chart (44px monthly, 40px age, 30px country, 20px horizontal charts). Horizontal bar charts flip the axis for category/product reads.
- **Doughnuts:** 68% cutout, 2px white segment borders, legend on the right.

### DataTable
- **Search & Length controls:** Surface background, 1px Strong Hairline border, 10px radius, `0.5rem 0.75rem` padding. On focus the border switches to Apple Blue with a 3px `rgba(0, 113, 227, 0.18)` focus ring.
- **Header:** Uppercase 0.75rem semibold Secondary Ink over a Strong Hairline underline; cells pad `0.75rem 0.875rem`.
- **Rows:** Ink text, `0.625rem 0.875rem` padding, hairline bottom rules only (no cell borders). Hover tints the whole row Cloud Gray (#f5f5f7).
- **Pagination:** Round (8px) ghost buttons at `0.25rem 0.625rem`, `0.1rem` margins, Secondary Ink; hover tints `rgba(0, 0, 0, 0.05)` and darkens text to Ink over 0.15s ease; the current page fills Apple Blue with white text.
- **Info & Length labels:** 0.8125rem Secondary Ink.

### Footer
- **Style:** Surface card treatment (18px radius, 1px hairline, surface background), `1rem` padding, 0.75rem Secondary Ink text.
- **Meta:** Run ID, match rate, and period facts in a wrapping flex; technical values in Ink semibold `code`; the generator credit sits right-aligned at 70% opacity.

### Focus
- **Global:** Every focusable element (`a`, `button`, `input`, `select`, `[tabindex]`) shows a `3px` solid `rgba(0, 113, 227, 0.35)` outline with a `2px` offset and `4px` radius. DataTable controls additionally use the softer ring above. Focus is always visible; it is never removed.

### Theme Toggle
- **Shape:** Circular 36px (2.25rem) hairline button in the header, right of the period pill.
- **Style:** `1px` Strong Hairline border on a Surface background with a Secondary Ink icon; hover tints to Table Hover and darkens to Ink over 0.25s ease.
- **Icon:** Inline SVG sun/moon at 18px (1.125rem), `stroke-width: 1.8`, round line caps and joins. The moon is hidden by default; `[data-theme="dark"]` swaps the sun for the moon via `display`.
- **State:** `aria-pressed` mirrors the active theme ("true" in dark); `aria-label` and `title` read "Cambiar modo claro/oscuro".
- **Focus:** The global 3px accent outline with 2px offset.

### Theming Behavior
- **Precedence:** Stored choice (`localStorage "theme"`) > system preference (`prefers-color-scheme: dark`) > light. The stored value always wins; contexts where localStorage throws (e.g. `file://`) fall back gracefully.
- **Apply:** `applyTheme()` sets `data-theme` on `<html>`, mirrors it to the toggle's `aria-pressed`, and rebuilds the charts.
- **Charts:** `themeColors()` reads `--accent`, `--chart-tick`, `--chart-grid`, `--tooltip-bg/fg`, and `--doughnut-border` via `getComputedStyle`; `buildCharts()` destroys all Chart.js instances and recreates them so canvas text, gridlines, tooltips, and doughnut segment borders follow the active theme.
- **Transition:** Theme switches animate with a `0.25s ease` color transition on the body, header, toggle, and cards. `prefers-reduced-motion` turns all transitions off and also suppresses the KPI reveal.

## Do's and Don'ts

### Do:
- **Do** keep the ground Cloud Gray (#f5f5f7), surfaces white, and chrome on exactly one Apple blue accent (#0071e3).
- **Do** render every figure in tabular numerals with tight tracking, so columns align as data.
- **Do** give every new surface the continuous 18px radius.
- **Do** separate with hairlines (rgba(0, 0, 0, 0.06); 0.12 for emphasized rules) and soft ambient shadows, never heavy borders.
- **Do** use Deep Apple Blue (#0060df) for accent-colored text that sits on tinted backgrounds.
- **Do** darken tooltip surfaces (Ink #1d1d1f) with light text, and keep chart gridlines at hairline opacity.
- **Do** respect `prefers-reduced-motion`; the KPI reveal must be the only authored animation.
- **Do** treat dark mode as a strict restyle: same radius, hairlines, one accent, and no new motion - only the palette inverts.
- **Do** let the stored theme choice win over the system preference, and keep `aria-pressed` in sync with the applied theme.

### Don't:
- **Don't** add a second accent to the interface chrome - the Apple system palette is for chart data encoding only.
- **Don't** animate anything beyond the KPI reveal and state transitions.
- **Don't** introduce heavy, dense, or multi-pixel borders; the dense bordered-card dashboard is the explicit anti-reference.
- **Don't** set uppercase or wide-tracking text outside the DataTable header.
- **Don't** introduce a second font family; one SF system stack carries the entire interface.
- **Don't** lift surfaces at rest; elevation is reserved for the KPI hover and the header's blur.
- **Don't** hardcode light-mode colors inside chart canvases; read the theme tokens so charts stay legible on True Black (#000000).
- **Don't** introduce dark-specific surfaces, radii, or animations; the dark world is the light world with an inverted palette.
