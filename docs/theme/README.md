# ETLantic Visual Theme

ETLantic uses a restrained nautical-cartography theme for visual identity.
The theme affects imagery, color, shape, and layout. Product terminology remains
technical and direct.

## Brand Concept

The core visual is a plotted route crossing a compass instrument:

- the route represents typed data flow;
- nodes represent contracts and pipeline boundaries;
- the compass represents validation and planning;
- branching routes represent interchangeable execution backends;
- chart contours represent the wider data environment.

The visual metaphor must not change architectural terminology. Documentation
should say `PipelinePlan`, plugin, artifact, output, and execution backend—not
voyage, vessel, cargo, harbor, or similar substitutes.

## Primary Assets

| Asset | Purpose |
|---|---|
| `assets/etlantic-logo.svg` | Canonical scalable logo |
| `assets/etlantic-favicon.svg` | Simplified small-size mark |
| `assets/etlantic-logo.png` | Transparent raster logo |
| `assets/etlantic-banner.png` | README and documentation hero |
| `assets/etlantic-logo-source.png` | Generated source; not for publication |

The SVG mark is canonical for documentation and application chrome. The
transparent PNG is available for platforms that require raster artwork.

## Palette

| Role | Name | Hex |
|---|---|---|
| Primary dark | Abyss | `#071A2B` |
| Secondary dark | Atlantic | `#0D3B5E` |
| Primary signal | Bioluminescent cyan | `#27D3E2` |
| Secondary signal | Sea-glass mint | `#63E6BE` |
| Restrained accent | Navigation brass | `#D6A84B` |
| Error and warning | Signal coral | `#FF6B5E` |
| Light surface | Sailcloth | `#EAF1ED` |
| Muted copy | Fog | `#9CB2BE` |

Use cyan and mint for routes, active states, links, and successful validation.
Use brass sparingly for orientation or emphasis. Coral is reserved for errors,
hazards, and destructive actions.

## Typography

- Interface and prose: Inter
- Code and technical annotations: IBM Plex Mono
- Fallbacks: system sans-serif and monospace stacks

Do not use decorative maritime typefaces.

## Shape Language

- Circular compass boundaries
- Connected nodes and directional paths
- Fine chart contours and technical grids
- Rounded geometry with clear directional arrows
- Sparse brass orientation marks

Avoid anchors, ship wheels, pirate imagery, treasure maps, sailor mascots,
photorealistic ships, and decorative waves.

## Documentation Usage

The Read the Docs site uses the SVG logo, simplified favicon, banner on the
home page, navy navigation chrome, and cyan/mint accents. Long technical
chapters should not use decorative backgrounds.

## Writing Rule

Visual branding may be nautical. Product copy should remain precise and
technical. Do not distribute nautical metaphors through ordinary documentation.

## Future Assets

Add assets only for concrete surfaces:

- social preview card;
- monochrome logo;
- light-background banner;
- plugin-category icons;
- release announcement template.
