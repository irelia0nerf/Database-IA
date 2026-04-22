# FoundLab Design System — Veritas v1.0

**Last updated:** 2026-04-21  
**Primary Direction:** Institutional sovereign infrastructure — every pixel earns its existence through information, provenance, or hierarchy  
**Forbidden:** Decorative gradients, unsourced metrics, cyberpunk glow, startup-casual type, toy dashboards, hover spectacle, animations that precede data

-----

## 1. Visual Theme & Atmosphere

### Core Visual Doctrine

FoundLab operates where cryptographic proof replaces institutional trust. The UI must look like it has been subpoenaed — every element defensible, sourced, and reproducible. The visual language is **sovereign infrastructure**, not SaaS product.

The system must communicate: *this is not software that helps you manage risk. This is the physical substrate that proves risk was managed.*

### Intended Cognitive Effect

Users — CIOs, CISOs, auditors, compliance leads — must feel the same cognitive state as reading a signed legal instrument. Not excitement. Not delight. **Certainty.**

### Density Level

High information density on operational screens. Intentional sparsity on institutional/landing screens. Never decorative sparsity (whitespace as aesthetic). Sparsity must serve focus, not elegance.

### Emotional / Operational Tone

- Command-level authority
- Forensic precision
- Zero affect (no rounded bubbly elements signaling approachability)
- Negative space is audit margin, not breathing room

### What the UI Must Never Feel Like

- A SaaS dashboard with colorful widget cards
- A startup’s compliance checkbox tool
- A cybersecurity product with glowing threat orbs
- A bank’s internal legacy tool (correct authority, wrong era)
- Any product that uses gradients to compensate for weak information hierarchy

### Visual Implications of Tone Statements

|Tone Statement |Visual Rule                                                       |
|---------------|------------------------------------------------------------------|
|“Sovereign”    |Monochromatic base with single signal color; no multi-hue palettes|
|“Forensic”     |Borders define containers, not shadows or cards without borders   |
|“Institutional”|Serif elements for headers in landing/board mode; mono for data   |
|“Proof-first”  |Every number has a source label or hash below it                  |
|“Zero affect”  |No rounded corners above 4px on data elements; 2px max on badges  |
|“Authoritative”|Typography weight does hierarchy, not color hue                   |

-----

## 2. Color Palette & Semantic Roles

### Base Mode: Dark Institutional (primary)

|Token                   |Hex      |Semantic Role                                   |Allowed                                        |Forbidden                                   |
|------------------------|---------|------------------------------------------------|-----------------------------------------------|--------------------------------------------|
|`--color-bg-base`       |`#0A0B0E`|Page root background                            |All screens                                    |Never override with texture or gradient     |
|`--color-bg-surface`    |`#111318`|Primary surface (panels, cards)                 |Containers, drawers                            |Do not use as page bg                       |
|`--color-bg-elevated`   |`#181C24`|Secondary surface above bg-surface              |Modals, focused panels                         |Do not stack more than 2 levels             |
|`--color-bg-inset`      |`#0D0F13`|Recessed areas                                  |Input fields, code blocks, table rows          |Do not use as panel bg                      |
|`--color-border-default`|`#252A35`|Primary divider / structural border             |All containers, table rows, form fields        |Never used as accent or focus ring          |
|`--color-border-subtle` |`#1C2028`|Sub-dividers, section separators                |Within surfaces                                |Never on outer container                    |
|`--color-border-active` |`#3A4455`|Hover/focus structural state                    |Interactive elements on hover                  |Not for static elements                     |
|`--color-text-primary`  |`#E8EAF0`|Primary legible text                            |Body, labels, values                           |Never on dark-on-dark                       |
|`--color-text-secondary`|`#8C93A4`|Supporting text, metadata                       |Timestamps, sources, captions                  |Never for primary values                    |
|`--color-text-tertiary` |`#525968`|Disabled, placeholder, inactive                 |Deactivated labels                             |Never for anything interactive              |
|`--color-signal`        |`#C2D1FF`|Primary signal — verification, confirmed, signed|Hash confirmations, seal status, verified state|Never used as button color; never decorative|
|`--color-signal-dim`    |`#3D4F7C`|Signal background tint                          |Badge backgrounds for verified                 |Never full saturation in body               |
|`--color-warning`       |`#D4A843`|Flag state, review pending                      |FLAG_REVIEW status indicators                  |Never for decorative highlight              |
|`--color-warning-dim`   |`#3D3010`|Warning surface tint                            |Warning badge bg                               |Not used as general warm tone               |
|`--color-critical`      |`#C74B3A`|BURN / FREEZE / hard error                      |BurnEngine verdicts, hard failures             |Never for warnings; never decorative        |
|`--color-critical-dim`  |`#2D1410`|Critical surface tint                           |Error panel bg                                 |                                            |
|`--color-success`       |`#4CAF7D`|APPROVE, operational OK                         |Only APPROVE verdicts and system health pass   |Never used to mean “positive sentiment”     |
|`--color-success-dim`   |`#0F2B1C`|Success surface tint                            |APPROVE badge bg                               |                                            |
|`--color-mono`          |`#9BA8C0`|Monospace data color                            |Hashes, signatures, addresses, timestamps      |Never prose; never headers                  |
|`--color-accent-void`   |`#000000`|Hard black for overlays                         |Modals backdrop                                |                                            |

### Light Mode: Board / Institutional (secondary — landing and board-facing exports only)

|Token                         |Hex      |Semantic Role          |
|------------------------------|---------|-----------------------|
|`--color-bg-base-light`       |`#F4F5F7`|Page background        |
|`--color-bg-surface-light`    |`#FFFFFF`|Card / panel surface   |
|`--color-bg-elevated-light`   |`#EDEEF2`|Inset / table rows     |
|`--color-border-default-light`|`#D0D3DC`|Container borders      |
|`--color-text-primary-light`  |`#0F1117`|Primary text           |
|`--color-text-secondary-light`|`#5A6072`|Supporting text        |
|`--color-signal-light`        |`#2A3F8F`|Verified / signed state|
|`--color-critical-light`      |`#B03325`|Failures, burn verdicts|

**Rule**: Light mode is for institutional documents, board presentations, and PDF exports. The operational product runs dark. Never mix modes in the same screen.

-----

## 3. Typography

### Font Families

```css
--font-display:  'Libre Baskerville', 'Georgia', serif;
--font-ui:       'IBM Plex Sans', 'Helvetica Neue', sans-serif;
--font-mono:     'IBM Plex Mono', 'Courier New', monospace;
```

**Rationale:**

- `Libre Baskerville` — institutional authority without antiquarian affect; used only for landing/board-facing mode headers
- `IBM Plex Sans` — designed for engineering and information products; carries IBM Systems/mainframe DNA; never casual
- `IBM Plex Mono` — all cryptographic data, hashes, signatures, timestamps, code; non-negotiable

### Type Scale

|Role              |Font                                        |Size   |Weight|Line Height|Letter Spacing         |
|------------------|--------------------------------------------|-------|------|-----------|-----------------------|
|Hero (landing)    |`--font-display`                            |56–72px|400   |1.1        |-0.02em                |
|Page Title        |`--font-display` (board) / `--font-ui` (ops)|32px   |600   |1.2        |-0.01em                |
|Section Title     |`--font-ui`                                 |18px   |600   |1.3        |0                      |
|Body              |`--font-ui`                                 |14px   |400   |1.6        |0                      |
|Table Text        |`--font-ui`                                 |13px   |400   |1.4        |0                      |
|Label / UI Label  |`--font-ui`                                 |11px   |500   |1.2        |0.06em (uppercase only)|
|Caption / Metadata|`--font-ui`                                 |11px   |400   |1.4        |0                      |
|Hash / Signature  |`--font-mono`                               |11px   |400   |1.5        |0.02em                 |
|Verdict Score     |`--font-mono`                               |48px   |700   |1.0        |-0.02em                |
|Terminal / Console|`--font-mono`                               |12px   |400   |1.6        |0                      |
|Timestamp         |`--font-mono`                               |11px   |400   |1.4        |0                      |

### Usage Rules

- Serif (`Libre Baskerville`) is permitted **only** in: hero headlines, landing mode section headers, board-facing document exports
- Serif is forbidden in: operational dashboards, command center, audit trail, decision detail, any data surface
- Monospace is mandatory for: all hash values, all signatures, all transaction IDs, all timestamps, all raw data fields, terminal/console outputs
- Uppercase labels must be `font-ui`, 11px, weight 500, `letter-spacing: 0.06em`, `color: --color-text-secondary`
- Body text must never exceed 16px; density is a feature, not a constraint

-----

## 4. Spacing, Layout & Elevation

### Base Unit

```
--space-unit: 4px
```

Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96

### Container Widths

```css
--container-max:    1280px;
--container-wide:   1440px;   /* command center only */
--container-narrow: 720px;    /* document / audit detail */
--container-xs:     480px;    /* modal, focused form */
```

### Section Spacing

|Screen Type    |Between Sections|Within Section|
|---------------|----------------|--------------|
|Landing        |96–128px        |48px          |
|Command Center |32px            |16px          |
|Decision Detail|48px            |24px          |
|Audit Trail    |24px            |12px          |

### Component Padding

|Component       |Padding  |
|----------------|---------|
|Panel / Card    |24px     |
|Table Cell      |12px 16px|
|Button (default)|8px 20px |
|Input Field     |10px 14px|
|Badge           |2px 8px  |
|Modal           |32px     |
|Sidebar         |16px     |

### Radius Scale

```css
--radius-none:   0px;
--radius-xs:     2px;    /* badges, status indicators */
--radius-sm:     4px;    /* buttons, inputs */
--radius-md:     6px;    /* panels, cards — maximum for data surfaces */
--radius-lg:     8px;    /* modals only */
```

**Rule**: No `border-radius` above `8px` anywhere in the system. Rounded corners signal approachability; FoundLab signals authority.

### Shadow / Elevation

```css
--shadow-none:    none;
--shadow-surface: 0 1px 3px rgba(0,0,0,0.4);     /* panel lift */
--shadow-raised:  0 4px 16px rgba(0,0,0,0.6);    /* modals */
--shadow-focus:   0 0 0 2px var(--color-signal);  /* keyboard focus ring only */
```

Shadow is structural, not decorative. No glow, no color shadows, no box-shadow as aesthetic choice.

### Grid Behavior

```css
/* Command Center */
--grid-command: 240px 1fr;    /* sidebar + main */

/* Decision Detail */
--grid-detail: 1fr 320px;     /* content + evidence panel */

/* Audit Trail */
--grid-audit: 80px 1fr;       /* index/time column + entry */
```

### Density Rules by Screen Type

|Screen         |Density|Rationale                                        |
|---------------|-------|-------------------------------------------------|
|Landing        |Low    |Institutional gravitas; content breathes         |
|Command Center |High   |Operators process volume; every px serves data   |
|Decision Detail|Medium |Precision read; one decision in full context     |
|Audit Trail    |High   |Sequential chain; vertical compression is correct|
|Board Exports  |Low    |Print-derived hierarchy; margin is authority     |

-----

## 5. Surface Model

### Base Background

`--color-bg-base` (`#0A0B0E`) is the canvas. It must never receive gradient, noise texture, or pattern overlay. It is void — the absence of unverified information.

### Surface Hierarchy

```
bg-base        → page root
├── bg-surface      → primary panels (main content areas)
│   ├── bg-elevated     → secondary surfaces (modals, focused state)
│   │   └── bg-inset        → recessed (inputs, code, inset tables)
```

No surface skips a level. `bg-elevated` never sits directly on `bg-base`.

### Panel Rules

- All panels must have: `border: 1px solid var(--color-border-default)`
- No panel uses shadow as primary delimiter — border is the delimiter
- Shadow is additive, only for modals and drawers (spatial lift above border-based content)
- No panel uses background-color alone without border — ambiguity is a security posture failure

### Overlays

Overlays use `rgba(0,0,0,0.72)` backdrop. No blur on overlay backdrop — blur obscures information that may still be operationally relevant to auditors.

### Glassmorphism

Forbidden. It has no information value and signals consumer product aesthetics incompatible with the FoundLab brand.

### Blur

Forbidden in all contexts except:

- Tooltip/popover: `backdrop-filter: blur(8px)` permitted on popover background only if it improves legibility of the popover itself
- All other blur usage: rejected

### Border Presence Rules

|Context                  |Border Required             |
|-------------------------|----------------------------|
|Any panel containing data|Yes — always                |
|Navigation sidebar       |Right border only           |
|Table                    |Outer border + row dividers |
|Input field              |Full border, not bottom-only|
|Modal                    |Yes                         |
|Badge                    |Yes, 1px                    |
|Button (primary)         |No border — uses bg fill    |
|Button (secondary/ghost) |Yes — border is the button  |

### Borders Forbidden On

- Page root (no border around viewport)
- Section headers as decoration (no `border-bottom` as section styling; use spacing only)
- Typography (no underline-as-decoration outside interactive links)

-----

## 6. Motion & Interaction

### Default Motion Style

Restrained. Functional. Non-distracting.

```css
--duration-fast:   120ms;
--duration-default: 200ms;
--duration-slow:   300ms;
--easing-default:  cubic-bezier(0.16, 1, 0.3, 1);    /* fast out, smooth settle */
--easing-enter:    cubic-bezier(0.0, 0.0, 0.2, 1);
--easing-exit:     cubic-bezier(0.4, 0.0, 1, 1);
```

### Hover Behavior

- Text color: shift from `--color-text-secondary` → `--color-text-primary`; 120ms
- Border color: shift from `--color-border-default` → `--color-border-active`; 120ms
- Background: `+4% lightness` on surface — no opacity tricks, no color hue change
- No scale transforms on hover
- No glow or box-shadow addition on hover (exception: focus ring only on keyboard nav)

### Focus Behavior

```css
:focus-visible {
  outline: 2px solid var(--color-signal);
  outline-offset: 2px;
  border-radius: var(--radius-xs);
}
```

Focus ring is `--color-signal` — the only context where signal color is used without a verification event.

### Active / Pressed States

- Darken background by 8% for 80ms; release to hover state
- No bounce, no spring physics on press
- Button press must feel mechanical, not elastic

### Loading States

- Skeleton screens: use `--color-bg-elevated` with `--color-bg-surface` alternating; 1.5s pulse animation, opacity 0.5–1.0
- No spinners except for isolated async operations (hash verification, KMS calls); spinner is 18px, `--color-signal`, rotation only
- Progress bars for known-duration operations; `--color-signal` fill on `--color-border-default` track

### Transition Intensity

- Panel entrance: `opacity 0→1`, `translateY(4px→0)`, 200ms — surgical, not theatrical
- Modal entrance: `opacity 0→1`, `scale(0.98→1)`, 200ms
- Drawer: `translateX(100%→0)`, 240ms
- Table row highlight: `background-color` transition only, 120ms
- All page transitions: none (full page loads are not animated)

### Prohibited Animations

- Parallax scrolling
- Looping background animations
- Particle systems
- Continuous pulsing elements (except skeleton loader, which terminates)
- Entrance stagger animations on data tables (data must be immediately readable)
- Scroll-triggered reveals (operational data is not a story; it is a ledger)

-----

## 7. Component Library

### Navbar

**Role:** Primary wayfinding and product identity anchor  
**Visual:** Full-width, `--color-bg-surface`, `border-bottom: 1px solid var(--color-border-default)`, height 56px  
**Typography:** Logo in `--font-ui` 600 14px uppercase with letter-spacing; nav items `--font-ui` 400 13px  
**States:** Active nav item: `--color-text-primary` + `border-bottom: 2px solid var(--color-signal)` on item itself, not full bar  
**Forbidden:** Hamburger menu on desktop, logo animation, dropdown mega-menus, sticky behavior with shadow-on-scroll

-----

### Sidebar

**Role:** Operational navigation — command center mode only  
**Visual:** 240px fixed, `--color-bg-surface`, `border-right: 1px solid var(--color-border-default)`  
**Nav items:** 36px height, 16px horizontal padding, `--font-ui` 13px  
**Active state:** `background: --color-bg-elevated`, `border-left: 2px solid --color-signal`, text `--color-text-primary`  
**Section labels:** 10px, uppercase, 500 weight, `--color-text-tertiary`, `letter-spacing: 0.08em`  
**Forbidden:** Icon-only collapsed sidebar (content loss unacceptable in forensic context), hover tooltips as primary nav labels

-----

### Hero (Landing)

**Role:** Institutional positioning — primary first read  
**Visual:** Full-width section, `--color-bg-base`, no background treatment; text-only with maximum one structural line element  
**Typography:** `--font-display` 56–72px 400, `--color-text-primary`; subheading `--font-ui` 18px 400, `--color-text-secondary`  
**CTA:** Single primary button; no secondary CTA competing with it in the hero zone  
**Forbidden:** Hero image, video background, animated text, gradient background in hero section, abstract blob graphics, floating cards

-----

### Buttons

**Primary**

```css
background: var(--color-signal-dim);
border: 1px solid var(--color-signal);
color: var(--color-signal);
font: 500 13px var(--font-ui);
padding: 8px 20px;
border-radius: var(--radius-sm);
```

Hover: `background` +10% lightness, border static  
Active: `background` −10% lightness

**Secondary / Ghost**

```css
background: transparent;
border: 1px solid var(--color-border-active);
color: var(--color-text-primary);
```

**Destructive**

```css
border: 1px solid var(--color-critical);
color: var(--color-critical);
background: var(--color-critical-dim);
```

**Forbidden button variants:** Gradient fill, rounded pill shape (`border-radius > 4px`), icon-only without tooltip, buttons wider than content container

-----

### Cards / Panels

```css
background: var(--color-bg-surface);
border: 1px solid var(--color-border-default);
border-radius: var(--radius-md);
padding: 24px;
```

**Header within card:** `font-ui` 13px 600, uppercase, `--color-text-secondary`, `letter-spacing: 0.06em`, `padding-bottom: 16px`, `border-bottom: 1px solid var(--color-border-subtle)`  
**Metric value:** `--font-mono` 32px 700, `--color-text-primary`  
**Source/provenance line:** Required below every metric — `--font-mono` 10px, `--color-text-tertiary`  
**Forbidden:** Cards without provenance on any data value, cards with colored accent borders as decoration, card hover elevation lift, shadow-only card (border is mandatory)

-----

### Badges / Status Indicators

```css
/* Base */
font: 500 10px/1.2 var(--font-ui);
letter-spacing: 0.06em;
text-transform: uppercase;
border-radius: var(--radius-xs);  /* 2px */
padding: 2px 8px;
border: 1px solid;
```

|Verdict       |Background            |Border                 |Text                    |
|--------------|----------------------|-----------------------|------------------------|
|APPROVE       |`--color-success-dim` |`--color-success`      |`--color-success`       |
|FLAG_REVIEW   |`--color-warning-dim` |`--color-warning`      |`--color-warning`       |
|FREEZE_ASSETS |`--color-warning-dim` |`--color-warning`      |`--color-warning`       |
|BURN_IMMEDIATE|`--color-critical-dim`|`--color-critical`     |`--color-critical`      |
|VERIFIED      |`--color-signal-dim`  |`--color-signal`       |`--color-signal`        |
|PENDING       |`--color-bg-elevated` |`--color-border-active`|`--color-text-secondary`|

**Forbidden:** Rounded pill badges, color-only badges without border, badges as decoration

-----

### Tables

**Role:** Primary data read surface in operational mode  
**Structure:**

```
thead: bg-inset, border-bottom: 2px solid --color-border-default
  th: font-ui 11px 500 uppercase, letter-spacing 0.06em, color text-secondary, padding 12px 16px
tbody:
  tr: border-bottom 1px solid --color-border-subtle
  tr:hover: background --color-bg-elevated, transition 120ms
  td: font-ui 13px 400, color text-primary, padding 12px 16px
  td.hash: font-mono 11px, color --color-mono
  td.timestamp: font-mono 11px, color text-secondary
  td.verdict: contains badge only, centered
```

**Forbidden:** Zebra striping with hue change, table without outer border, truncation without expand affordance on hash fields, row expansion with animation

-----

### Forms

**Input:**

```css
background: var(--color-bg-inset);
border: 1px solid var(--color-border-default);
border-radius: var(--radius-sm);
color: var(--color-text-primary);
font: 400 13px var(--font-ui);
padding: 10px 14px;
```

Focus: `border-color: var(--color-signal)` + `box-shadow: var(--shadow-focus)`  
Error: `border-color: var(--color-critical)` + error message below in `--color-critical`, `--font-ui` 11px

**Labels:** Above input, `--font-ui` 11px 500 uppercase, `--color-text-secondary`, `letter-spacing: 0.06em`, `margin-bottom: 6px`

**Forbidden:** Floating/animated labels, placeholder-as-label, inline form fields without label, auto-fill style overrides that change background color

-----

### Tabs

**Role:** Screen-level navigation within a detail view  
**Visual:** Horizontal bar, `border-bottom: 1px solid --color-border-default` under full width  
**Tab item:** `--font-ui` 13px 500; inactive `--color-text-secondary`; active `--color-text-primary` + `border-bottom: 2px solid --color-signal`  
**Forbidden:** Pill-style tabs, card-style tabs with raised active state, tab panels that animate between each other

-----

### Alerts

```
border-left: 3px solid [semantic color];
background: [dim variant];
border: 1px solid [semantic color at 40% opacity];
padding: 12px 16px;
```

|Type    |Left Border       |Message Style                           |
|--------|------------------|----------------------------------------|
|Info    |`--color-signal`  |`--font-ui` 13px, `--color-text-primary`|
|Warning |`--color-warning` |`--font-ui` 13px, `--color-warning`     |
|Critical|`--color-critical`|`--font-ui` 13px 500, `--color-critical`|
|Success |`--color-success` |`--font-ui` 13px, `--color-success`     |

**Forbidden:** Toast notifications for critical system states (critical alerts are persistent inline, not dismissed), alert icons without semantic meaning

-----

### Evidence Blocks

**Role:** Display cryptographic evidence — hashes, signatures, veritas seals

```css
background: var(--color-bg-inset);
border: 1px solid var(--color-border-default);
border-radius: var(--radius-sm);
padding: 16px;
```

**Internal structure:**

```
[LABEL — font-ui 10px uppercase 500, color text-tertiary]
[VALUE — font-mono 12px, color --color-mono, selectable]
[COPY BUTTON — ghost, 11px, right-aligned]
```

Hash chains must render with connecting structure:

```
prev_hash → lock_hash → this_hash
```

Use `--color-border-subtle` connector lines, `--font-mono` 10px for hashes, `--color-signal` for verified state marker.

**Forbidden:** Truncated hashes without expand, copy without feedback state, visual fanfare on hash match (a checkmark is sufficient — badge VERIFIED)

-----

### Audit Timeline

**Role:** Chronological chain of custody — VeritasBlackChain entries  
**Structure:** Vertical timeline, left-aligned index column (timestamp in `--font-mono`), right-side entry  
**Entry:**

- Actor: `--font-ui` 13px 600
- Action: `--font-ui` 13px 400
- Artifact: `--font-mono` 11px, `--color-mono`
- Timestamp: `--font-mono` 10px, `--color-text-tertiary`
- Connector: 1px solid `--color-border-subtle`, vertical

**Chain break indicator:** Red connector line `--color-critical` + inline alert “CHAIN INTEGRITY VIOLATION — prev_hash mismatch” — never silenced, never dismissible

**Forbidden:** Collapsed timeline by default, animations on entry appearance, icons as primary timeline markers (text is the marker)

-----

### Terminal / Console

```css
background: #060709;
border: 1px solid var(--color-border-default);
border-radius: var(--radius-sm);
padding: 16px;
font: 400 12px/1.6 var(--font-mono);
color: var(--color-text-primary);
overflow-x: auto;
```

Semantic coloring within terminal:

- System lines: `--color-text-tertiary`
- Verified/OK: `--color-success)`
- Error: `--color-critical)`
- Hash/address: `--color-mono`
- Command input: `--color-text-primary` with `>` prefix in `--color-text-secondary`

**Forbidden:** Simulated typing animation, fake terminal cursor blinking as decoration, colorized output that contradicts semantic roles above

-----

### Modals

```css
background: var(--color-bg-elevated);
border: 1px solid var(--color-border-active);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-raised);
padding: 32px;
max-width: 640px;
```

**Backdrop:** `rgba(0,0,0,0.72)`, no blur  
**Header:** `--font-ui` 16px 600, `border-bottom: 1px solid --color-border-default`, `padding-bottom: 16px`  
**Footer:** `border-top: 1px solid --color-border-default`, `padding-top: 16px`, actions right-aligned  
**Forbidden:** Modal without explicit close mechanism, confirmation modals without destructive-styled confirm button, stacked modals

-----

### Drawers

**Role:** Contextual detail panel without leaving current screen  
**Placement:** Right edge, 480px width  
**Background:** `--color-bg-surface`, `border-left: 1px solid --color-border-default`  
**Forbidden:** Left-side drawers, animated drawer content reveal, drawer with shadow-only separation

-----

## 8. Screen Regimes

### Regime A — Institutional / Landing / Board-Facing

**Purpose:** First impression for CIOs, auditors, board members; also used for PDF/export artifacts

- **Density:** Low — 96px+ section spacing, generous margins
- **Surface:** `--color-bg-base` (dark) or `--color-bg-base-light` (light for print/export)
- **Typography:** `--font-display` for primary headers; `--font-ui` for body
- **Component patterns:** Hero, narrative section blocks, evidence summary cards, single CTA
- **Prohibited carryovers:** Table density from command center, monospace-heavy data blocks, badge clusters, sidebar navigation

-----

### Regime B — Operational / Command Center

**Purpose:** Day-to-day operation for platform teams; high-throughput data monitoring

- **Density:** High — 16–24px section spacing; maximize data-per-viewport
- **Surface:** Dark only; `--color-bg-base` → `--color-bg-surface` panels
- **Typography:** `--font-ui` exclusively for UI elements; `--font-mono` for all data values
- **Component patterns:** Sidebar nav, data tables, badge-heavy status rows, evidence blocks, real-time verdict feed
- **Prohibited carryovers:** Hero display typography, serif headers, landing-mode sparsity, decorative section spacing

-----

### Regime C — Forensic / Audit / Decision Detail

**Purpose:** Deep investigation of a single decision, transaction, or audit event

- **Density:** Medium — breadth of evidence, not volume of records; each element must be individually parseable
- **Surface:** Dark; two-column layout — evidence panel pinned right
- **Typography:** Mixed — `--font-ui` for prose labels; `--font-mono` mandatory for all evidence values
- **Component patterns:** Audit timeline, evidence blocks, hash chain visualization, expandable reasoning accordion, verdict badge
- **Prohibited carryovers:** Aggregate metrics (no totals in forensic view — only this record), navigation tabs that hide evidence, any collapsed sections by default

-----

## 9. Do’s and Don’ts

### Do

- Add `[source]` or `[hash]` provenance beneath every metric displayed
- Use `--font-mono` for all cryptographic values without exception
- Render BURN_IMMEDIATE and chain integrity violations in persistent, non-dismissible elements
- Define 1px structural borders on every container; shadows are supplementary only
- Use `--color-signal` exclusively for cryptographic verification and keyboard focus
- Label all uppercase UI text with `letter-spacing: 0.06em` and weight 500
- Degrade gracefully on data absence — show empty state with audit-appropriate message, not a loading skeleton that never resolves
- Keep click targets minimum 36px height regardless of content size
- On hash fields: always show full value on click/expand; never truncate permanently

### Don’t

- Display any metric without traceable source label
- Use gradients for backgrounds, buttons, or any structural element
- Animate data arrival in tables or timelines — data is not theater
- Use `border-radius` above 8px anywhere in the system
- Use color as the sole differentiator for semantic states (all states have both color and text/icon confirmation)
- Mix Regime A and Regime B component patterns in the same view
- Use shadow as the primary separator between containers
- Introduce any font outside the three defined families
- Use the word “beautiful”, “sleek”, or “modern” in UI copy
- Render a BURN verdict in any color other than `--color-critical`
- Allow placeholder text to serve as form field labels
- Suppress or dismiss chain integrity violation alerts

-----

## 10. Usage Rules for AI Tools

### Stitch

- Load this `DESIGN.md` as the design system source before any generation
- Reference color tokens by name (`--color-bg-surface`) not by hex in prompts
- Specify screen regime explicitly in every generation request: “Generate in Regime B — Command Center”
- If Stitch introduces rounded pill elements, gradients, or card hover shadows: reject and regenerate with instruction “apply radius and surface rules from Section 4 and 5”

### Gemini / AI Studio

- Paste Sections 2 and 3 (Color Palette + Typography) into system prompt for any UI generation
- Specify: “This is an institutional forensic product. Do not introduce consumer SaaS patterns.”
- Any output containing `border-radius > 8px`, gradient backgrounds, or glowing elements fails the brief — regenerate

### Claude / Claude Code

- Treat this file as the single source of truth for all frontend generation tasks in this codebase
- When generating component code: reference token names from Section 2 as CSS custom properties; do not hardcode hex values
- If generating a new component type not listed in Section 7: apply the nearest analogous component rules and flag the gap for design review
- Regeneration instruction: “Regenerate using only surface, border, and typography rules from FoundLab DESIGN.md Veritas v1.0. No invented styles.”

### Cursor

- Pin this file as a project rule: “All frontend code must use CSS custom properties defined in DESIGN.md Veritas v1.0”
- Inline linting note: any `background: linear-gradient` in component CSS is a design system violation — flag and block

### Figma-Assisted Workflows

- Token names in this document map 1:1 to Figma variable names in the FoundLab Veritas library
- Color styles: import from Section 2; do not create local styles
- Text styles: import from Section 3 scale; do not introduce additional text styles
- Components generated from this spec are the source; Figma is the derivation, not vice versa

-----

## 11. Output Quality Bar

Every screen generated from this `DESIGN.md` must pass the following tests before shipping:

### Consistency Test

Every color value on screen maps to a named token in Section 2. No hex values appear in component code.

### Legibility Test

All text at minimum contrast ratio 4.5:1 against its background. Monospace data elements at 11px minimum. No truncated hash values as final state.

### Product Relevance Test

A screenshot of this screen, shown without FoundLab branding, is identifiable as “institutional infrastructure” and not as “SaaS dashboard”, “cyberpunk security tool”, or “startup product”.

### Brand Specificity Test

Remove all logos. The screen still does not resemble any competitor product. IBM Plex type stack + dark institutional palette + evidence block components are sufficient to identify FoundLab without brand marks.

### Anti-Generic Test

The following elements are absent: purple gradients, glowing card borders, circular progress indicators used decoratively, hero illustrations with abstract shapes, stock-photography hero backgrounds, dashboard “quick stat” widgets without provenance, any element that would appear in a Dribbble “dark dashboard UI” shot.

### Provenance Test

Every numeric value displayed has either a source label, a hash reference, or an explicit “no data” state. No metric is displayed without a chain-of-custody trace.

-----

*FoundLab · dont trust, verify. · DESIGN.md Veritas v1.0 · 2026-04-21*  
*Classification: INTERNAL — derivative artifacts for partners only*