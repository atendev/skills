---
name: apple
description: "Apply Apple Human Interface Guidelines whenever designing, building, reviewing, or styling an app, iOS, iPadOS, macOS, watchOS, tvOS, visionOS interface, or mobile screen. Enforces every Apple numeric specification: 44x44 pt tap targets, SF Pro and Dynamic Type scales across all 12 sizes, 8 pt layout grids, safe area insets, screen margins, continuous corner radii, bar heights, system colors, materials, and 4.5:1 or 7:1 contrast ratios."
user-invocable: true
---

# Apple human interface guidelines

Apply this skill automatically whenever designing, building, critiquing, or styling any mobile screen, native app, web-based mobile prototype, iOS, iPadOS, macOS, watchOS, tvOS, or visionOS interface, or when invoked via `/apple`.

Every numeric value below comes from Apple's Human Interface Guidelines. Do not guess or substitute arbitrary pixel values when laying out screens, sizing controls, choosing typography, or picking colors.

## Core design principles

- **Clarity.** Text is legible at every size, icons are precise and lucid, adornments are subtle and appropriate, and a sharpened focus on functionality motivates the design.
- **Deference.** Fluid motion and a crisp, clean interface help people understand and interact with content while never competing with it. Chrome stays minimal and translucent so content fills the screen.
- **Depth.** Distinct visual layers and realistic motion convey hierarchy, impart vitality, and facilitate understanding. Touch and discoverability heighten delight without causing someone to lose context.
- **Platform integrity.** Use system navigation bars, tab bars, sheets, lists, switches, segmented controls, and SF Symbols. Avoid web-style hamburger menus, custom back gestures that break left-edge swipe, hover-only mobile affordances, or unstyled HTML controls.

## Touch, click, and gaze targets

Every interactive element must meet the minimum hit target for its platform, even when the visible glyph or button frame is smaller. Expand the hit region with padding or `contentShape` when the visual control is compact.

| Platform | Input method | Minimum hit target | Minimum spacing between targets | Recommended spacing | Notes |
| --- | --- | --- | --- | --- | --- |
| iOS | Touch | `44 x 44 pt` | `8 pt` edge-to-edge | `12 pt` to `16 pt` | Apply `16 pt` minimum between destructive and primary buttons |
| iPadOS | Touch and pointer | `44 x 44 pt` | `8 pt` edge-to-edge | `12 pt` | Pointer hover region snaps to control bounds with `4 pt` padding |
| macOS | Pointer and trackpad | `28 x 28 pt` standard, `20 x 20 pt` dense minimum | `6 pt` edge-to-edge | `8 pt` to `12 pt` | Standard toolbar buttons use `28 pt` or `32 pt` height |
| watchOS | Touch | `44 x 44 pt` | `6 pt` vertical | `8 pt` vertical | Prefer full-width buttons; side-by-side buttons require `8 pt` gap |
| visionOS | Eye gaze and indirect pinch | `60 x 60 pt` hit region, `44 x 44 pt` minimum visual frame | `12 pt` center-to-edge, `8 pt` edge-to-edge | `16 pt` | Include `4 pt` minimum hover highlight padding around visual bounds |
| tvOS | Focus engine remote | `60 pt` minimum height | `20 pt` between cards | `40 pt` to `48 pt` between shelves | Account for `1.08x` to `1.12x` focus expansion scale so focused items never collide |

## Typography and Dynamic Type scale

Apple platforms use San Francisco: `SF Pro` on iOS, iPadOS, macOS, tvOS, and visionOS; `SF Compact` on watchOS; `SF Mono` for code and tabular numbers; `New York` for editorial serif moments.

- **Optical size threshold.** Use `SF Pro Text` for sizes below `20 pt` and `SF Pro Display` for sizes `20 pt` and above. Modern variable `SF Pro` interpolates optical size `opsz` automatically at the `20 pt` boundary.
- **Minimum legible sizes.** Never go below `11 pt` on iOS and iPadOS, `10 pt` on macOS, `12 pt` on watchOS and visionOS, or `23 pt` on tvOS.
- **Tabular numerals.** Apply `font-variant-numeric: tabular-nums` or `.monospacedDigit` on timers, prices, counters, and aligned data columns.

### iOS, iPadOS, and visionOS default Dynamic Type scale at Large setting

The system default Dynamic Type size is `Large`. Tracking values are given in `1/1000 em`, points, and CSS `em` equivalents.

| Text style | Default weight | Emphasized weight | Size | Line height / leading | Tracking in 1/1000 em | Tracking in pt | CSS letter-spacing | Typical usage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Large Title` | Regular `400` | Bold `700` | `34 pt` | `41 pt` | `+11` | `+0.37 pt` | `+0.011em` | Top-level scrolling navigation titles |
| `Title 1` | Regular `400` | Bold `700` | `28 pt` | `34 pt` | `+13` | `+0.36 pt` | `+0.013em` | Hero headers, empty state titles, modal headers |
| `Title 2` | Regular `400` | Bold `700` | `22 pt` | `28 pt` | `+16` | `+0.35 pt` | `+0.016em` | Major section headers, card titles |
| `Title 3` | Regular `400` | Semibold `600` | `20 pt` | `25 pt` | `+19` | `+0.38 pt` | `+0.019em` | Subsection headers, prominent list headers |
| `Headline` | Semibold `600` | Bold `700` | `17 pt` | `22 pt` | `-24` | `-0.41 pt` | `-0.024em` | Inline navigation titles, alert titles, emphasized row titles |
| `Body` | Regular `400` | Semibold `600` | `17 pt` | `22 pt` | `-24` | `-0.41 pt` | `-0.024em` | Primary reading copy, standard list row labels, form inputs |
| `Callout` | Regular `400` | Semibold `600` | `16 pt` | `21 pt` | `-20` | `-0.32 pt` | `-0.020em` | Secondary descriptions, callout banners, medium buttons |
| `Subheadline` | Regular `400` | Semibold `600` | `15 pt` | `20 pt` | `-16` | `-0.24 pt` | `-0.016em` | List row subtitles, card metadata, secondary labels |
| `Footnote` | Regular `400` | Semibold `600` | `13 pt` | `18 pt` | `-6` | `-0.08 pt` | `-0.006em` | Grouped table headers and footers, alert body copy, timestamps |
| `Caption 1` | Regular `400` | Medium `500` | `12 pt` | `16 pt` | `0` | `0.00 pt` | `0em` | Image captions, helper labels, badge text |
| `Caption 2` | Regular `400` | Semibold `600` | `11 pt` | `13 pt` | `+6` | `+0.07 pt` | `+0.006em` | Tab bar labels, legal microcopy, compact badges |

### Standard Dynamic Type progression from xSmall to xxxLarge

Values are formatted as `size / leading` in points.

| Text style | `xSmall` | `Small` | `Medium` | `Large` default | `xLarge` | `xxLarge` | `xxxLarge` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Large Title` | `31 / 38 pt` | `32 / 39 pt` | `33 / 40 pt` | `34 / 41 pt` | `36 / 43 pt` | `38 / 46 pt` | `40 / 48 pt` |
| `Title 1` | `25 / 31 pt` | `26 / 32 pt` | `27 / 33 pt` | `28 / 34 pt` | `30 / 37 pt` | `32 / 39 pt` | `34 / 41 pt` |
| `Title 2` | `19 / 24 pt` | `20 / 25 pt` | `21 / 26 pt` | `22 / 28 pt` | `24 / 30 pt` | `26 / 32 pt` | `28 / 34 pt` |
| `Title 3` | `17 / 22 pt` | `18 / 23 pt` | `19 / 24 pt` | `20 / 25 pt` | `22 / 28 pt` | `24 / 30 pt` | `26 / 32 pt` |
| `Headline` | `14 / 19 pt` | `15 / 20 pt` | `16 / 21 pt` | `17 / 22 pt` | `19 / 24 pt` | `21 / 26 pt` | `23 / 29 pt` |
| `Body` | `14 / 19 pt` | `15 / 20 pt` | `16 / 21 pt` | `17 / 22 pt` | `19 / 24 pt` | `21 / 26 pt` | `23 / 29 pt` |
| `Callout` | `13 / 18 pt` | `14 / 19 pt` | `15 / 20 pt` | `16 / 21 pt` | `18 / 23 pt` | `20 / 25 pt` | `22 / 28 pt` |
| `Subheadline` | `12 / 16 pt` | `13 / 18 pt` | `14 / 19 pt` | `15 / 20 pt` | `17 / 22 pt` | `19 / 24 pt` | `21 / 28 pt` |
| `Footnote` | `12 / 16 pt` | `12 / 16 pt` | `12 / 16 pt` | `13 / 18 pt` | `15 / 20 pt` | `17 / 22 pt` | `19 / 24 pt` |
| `Caption 1` | `11 / 13 pt` | `11 / 13 pt` | `11 / 13 pt` | `12 / 16 pt` | `14 / 19 pt` | `16 / 21 pt` | `18 / 23 pt` |
| `Caption 2` | `11 / 13 pt` | `11 / 13 pt` | `11 / 13 pt` | `11 / 13 pt` | `13 / 18 pt` | `15 / 20 pt` | `17 / 22 pt` |

### Accessibility Dynamic Type progression from AX1 to AX5

At Accessibility sizes `AX1` through `AX5`, horizontal multi-column rows must reflow into vertical stacks, side-by-side labels and values stack vertically, and line limits expand so text never truncates.

| Text style | `AX1` | `AX2` | `AX3` | `AX4` | `AX5` |
| --- | --- | --- | --- | --- | --- |
| `Large Title` | `44 / 52 pt` | `48 / 57 pt` | `52 / 61 pt` | `56 / 66 pt` | `60 / 70 pt` |
| `Title 1` | `38 / 46 pt` | `43 / 51 pt` | `48 / 57 pt` | `53 / 62 pt` | `58 / 68 pt` |
| `Title 2` | `34 / 41 pt` | `39 / 47 pt` | `44 / 52 pt` | `50 / 59 pt` | `56 / 66 pt` |
| `Title 3` | `31 / 38 pt` | `37 / 44 pt` | `43 / 51 pt` | `49 / 58 pt` | `55 / 65 pt` |
| `Headline` | `28 / 34 pt` | `33 / 40 pt` | `40 / 48 pt` | `47 / 56 pt` | `53 / 62 pt` |
| `Body` | `28 / 34 pt` | `33 / 40 pt` | `40 / 48 pt` | `47 / 56 pt` | `53 / 62 pt` |
| `Callout` | `26 / 32 pt` | `32 / 39 pt` | `38 / 46 pt` | `44 / 52 pt` | `51 / 60 pt` |
| `Subheadline` | `25 / 31 pt` | `30 / 37 pt` | `36 / 43 pt` | `42 / 50 pt` | `49 / 58 pt` |
| `Footnote` | `23 / 29 pt` | `27 / 33 pt` | `33 / 40 pt` | `38 / 46 pt` | `44 / 52 pt` |
| `Caption 1` | `22 / 28 pt` | `26 / 32 pt` | `32 / 39 pt` | `37 / 44 pt` | `43 / 51 pt` |
| `Caption 2` | `20 / 25 pt` | `24 / 30 pt` | `29 / 35 pt` | `34 / 41 pt` | `40 / 48 pt` |

### macOS system type scale

| Text style | Default weight | Emphasized weight | Size | Line height / leading | Tracking in pt |
| --- | --- | --- | --- | --- | --- |
| `Large Title` | Regular `400` | Bold `700` | `26 pt` | `32 pt` | `+0.22 pt` |
| `Title 1` | Regular `400` | Bold `700` | `22 pt` | `26 pt` | `-0.26 pt` |
| `Title 2` | Regular `400` | Bold `700` | `17 pt` | `22 pt` | `-0.43 pt` |
| `Title 3` | Regular `400` | Semibold `600` | `15 pt` | `20 pt` | `-0.23 pt` |
| `Headline` | Bold `700` | Bold `700` | `13 pt` | `16 pt` | `-0.08 pt` |
| `Body` | Regular `400` | Semibold `600` | `13 pt` | `16 pt` | `-0.08 pt` |
| `Callout` | Regular `400` | Semibold `600` | `12 pt` | `15 pt` | `0.00 pt` |
| `Subheadline` | Regular `400` | Semibold `600` | `11 pt` | `14 pt` | `+0.06 pt` |
| `Footnote` | Regular `400` | Semibold `600` | `10 pt` | `13 pt` | `+0.12 pt` |
| `Caption 1` | Regular `400` | Medium `500` | `10 pt` | `13 pt` | `+0.12 pt` |
| `Caption 2` | Medium `500` | Semibold `600` | `10 pt` | `13 pt` | `+0.12 pt` |

### watchOS and tvOS key type sizes

| Platform | Style | Size | Line height | Notes |
| --- | --- | --- | --- | --- |
| watchOS | `Large Title` | `32 pt` | `36 pt` | `SF Compact Display`, Regular or Semibold |
| watchOS | `Title 1` | `26 pt` | `30 pt` | `SF Compact Display` |
| watchOS | `Title 2` | `22 pt` | `26 pt` | `SF Compact Display` |
| watchOS | `Title 3` | `19 pt` | `22 pt` | `SF Compact Rounded` or `SF Compact Text` |
| watchOS | `Headline` | `16 pt` | `20 pt` | `SF Compact Text` Semibold |
| watchOS | `Body` | `16 pt` | `20 pt` | `SF Compact Text` Regular |
| watchOS | `Footnote` | `14 pt` | `17 pt` | `SF Compact Text` |
| watchOS | `Caption 1` | `13 pt` | `16 pt` | `SF Compact Text` |
| watchOS | `Caption 2` | `12 pt` | `14 pt` | Floor size on Apple Watch |
| tvOS | `Title 1` | `76 pt` | `96 pt` | `10 ft` viewing distance |
| tvOS | `Title 2` | `57 pt` | `66 pt` | Section headers |
| tvOS | `Title 3` | `48 pt` | `56 pt` | Shelf headers |
| tvOS | `Headline` | `38 pt` | `46 pt` | Emphasized metadata |
| tvOS | `Body` | `29 pt` | `36 pt` | Primary descriptions |
| tvOS | `Callout` | `31 pt` | `38 pt` | Secondary actions |
| tvOS | `Caption 1` | `25 pt` | `32 pt` | Metadata labels |
| tvOS | `Caption 2` | `23 pt` | `30 pt` | Floor size on Apple TV |

## Layout grid, margins, safe areas, and viewports

### Spatial grid

- **Base grid unit.** Use an `8 pt` spatial grid of `8, 16, 24, 32, 40, 48, 64 pt` for layout margins, section spacing, card padding, and component heights.
- **Half-step unit.** Use `4 pt` for tight vertical pairing between a title and subtitle, or between an icon and its inline label.
- **Micro-step unit.** Use `2 pt` only for optical alignment, segmented control track insets, or toggle switch thumb insets.
- **Hairline dividers.** Use `0.33 pt` on `@3x` displays, which equals `1 physical px`, and `0.5 pt` on `@2x` displays, which also equals `1 physical px`.

### Screen margins and readable content guides

| Context | Outer screen margin | Internal card or cell horizontal padding | Total text inset from screen edge | Vertical spacing between sections |
| --- | --- | --- | --- | --- |
| iPhone standard `375 pt` to `402 pt` width, plain list | `16 pt` | `0 pt` additional | `16 pt` | `24 pt` to `32 pt` |
| iPhone Plus and Pro Max `430 pt` to `440 pt` width, plain list | `20 pt` | `0 pt` additional | `20 pt` | `24 pt` to `32 pt` |
| iPhone inset grouped list, `375 pt` to `402 pt` width | `16 pt`, or `20 pt` on Plus and Max | `16 pt`, or `20 pt` on Plus and Max | `32 pt`, or `40 pt` on Plus and Max | `20 pt` to `24 pt` between groups, `35 pt` with header |
| iPadOS Compact width, up to `678 pt` split view | `16 pt` to `20 pt` | `16 pt` | `32 pt` to `36 pt` | `24 pt` |
| iPadOS Regular width | `24 pt` to `32 pt` | `20 pt` | `44 pt` to `52 pt` | `28 pt` to `36 pt` |
| macOS window content area | `20 pt` | `16 pt` | `36 pt` | `16 pt` to `24 pt` |
| visionOS window content area | `24 pt` to `32 pt` | `16 pt` to `20 pt` | `40 pt` to `52 pt` | `20 pt` to `24 pt` |
| watchOS screen edges | `8 pt` to `12 pt`, `4.5%` of screen width | `8 pt` to `10 pt` inside platters | `16 pt` to `22 pt` | `8 pt` between platters |
| tvOS overscan safe zone | `90 pt` left/right, `60 pt` top/bottom | `24 pt` inside cards | `114 pt` horizontal | `48 pt` to `64 pt` between shelves |

- **Readable content width `readableContentGuide`.** Cap long-form prose and wide form rows at `672 pt` maximum width, which yields `60 to 75` characters per line at `17 pt` Body, with `50 to 65` characters optimal on mobile. On iPad Pro at `1032 pt` width and on macOS, center or align readable content within the `672 pt` guide rather than stretching text edge-to-edge.

### Safe area insets

Never place interactive controls, text, or unclipped content inside the status bar, Dynamic Island, sensor housing notch, home indicator region, or rounded screen corners. Background colors, collection scroll views, and blurred materials extend edge-to-edge behind safe areas.

| Device family | Portrait top safe area | Portrait bottom safe area | Landscape left and right safe area | Landscape top safe area | Landscape bottom safe area |
| --- | --- | --- | --- | --- | --- |
| iPhone 16 Pro, 16 Pro Max, 15 Pro, 15 Pro Max, 14 Pro, 14 Pro Max | `59 pt`, `62 pt` on 16 Pro and 16 Pro Max | `34 pt` | `59 pt`, `62 pt` on 16 Pro and 16 Pro Max | `0 pt` | `21 pt` |
| iPhone 16, 16 Plus, 15, 15 Plus | `59 pt` | `34 pt` | `59 pt` | `0 pt` | `21 pt` |
| iPhone 14, 14 Plus, 13, 13 Pro, 12, 12 Pro, 16e | `47 pt`, `48 pt` on 12 and 13 | `34 pt` | `47 pt` | `0 pt` | `21 pt` |
| iPhone 13 mini, 12 mini | `50 pt` | `34 pt` | `50 pt` | `0 pt` | `21 pt` |
| iPhone X, XS, 11 Pro, 11 | `44 pt`, `48 pt` on 11 | `34 pt` | `44 pt` | `0 pt` | `21 pt` |
| iPhone SE 3rd gen, 8, 7 | `20 pt` | `0 pt` | `0 pt` | `0 pt` | `0 pt` |
| iPad Pro, iPad Air, iPad mini with Face ID or top button | `24 pt` | `20 pt`, `25 pt` with Stage Manager | `0 pt` | `24 pt` | `20 pt` |

### Device viewports, resolutions, scale factors, and size classes

| Device | Logical viewport in pt | Physical resolution in px | Scale factor | PPI | Portrait size class | Landscape size class | Device bezel corner radius |
| --- | --- | --- | --- | --- | --- | --- | --- |
| iPhone SE 3rd gen `4.7"` | `375 x 667 pt` | `750 x 1334 px` | `@2x` | `326` | Compact W, Regular H | Compact W, Compact H | `0 pt` rectangular |
| iPhone 13 mini `5.4"` | `375 x 812 pt` | `1080 x 2340 px` | `@3x` | `476` | Compact W, Regular H | Compact W, Compact H | `44 pt` |
| iPhone 14, 13, 12, 16e `6.1"` | `390 x 844 pt` | `1170 x 2532 px` | `@3x` | `460` | Compact W, Regular H | Compact W, Compact H | `47.33 pt` |
| iPhone 16, 15, 15 Pro `6.1"` | `393 x 852 pt` | `1179 x 2556 px` | `@3x` | `460` | Compact W, Regular H | Compact W, Compact H | `55 pt` |
| iPhone 16 Pro `6.3"` | `402 x 874 pt` | `1206 x 2622 px` | `@3x` | `460` | Compact W, Regular H | Compact W, Compact H | `55 pt` |
| iPhone 16 Plus, 15 Plus, 15 Pro Max `6.7"` | `430 x 932 pt` | `1290 x 2796 px` | `@3x` | `460` | Compact W, Regular H | Regular W, Compact H | `55 pt` |
| iPhone 16 Pro Max `6.9"` | `440 x 956 pt` | `1320 x 2868 px` | `@3x` | `460` | Compact W, Regular H | Regular W, Compact H | `55 pt` |
| iPad mini `8.3"` | `744 x 1133 pt` | `1488 x 2266 px` | `@2x` | `326` | Regular W, Regular H | Regular W, Regular H | `21.5 pt` |
| iPad `10.9"` and iPad Air `11"` | `820 x 1180 pt` | `1640 x 2360 px` | `@2x` | `264` | Regular W, Regular H | Regular W, Regular H | `18 pt` |
| iPad Pro `11"` M4 | `834 x 1210 pt` | `1668 x 2420 px` | `@2x` | `264` | Regular W, Regular H | Regular W, Regular H | `18 pt` |
| iPad Air `13"` and iPad Pro `12.9"` | `1024 x 1366 pt` | `2048 x 2732 px` | `@2x` | `264` | Regular W, Regular H | Regular W, Regular H | `18 pt` |
| iPad Pro `13"` M4 | `1032 x 1376 pt` | `2064 x 2752 px` | `@2x` | `264` | Regular W, Regular H | Regular W, Regular H | `18 pt` |
| Apple Watch Series 10 `42mm` | `187 x 223 pt` | `374 x 446 px` | `@2x` | `326` | Compact | N/A | `36 pt` |
| Apple Watch Series 10 `46mm` | `208 x 248 pt` | `416 x 496 px` | `@2x` | `326` | Compact | N/A | `40 pt` |
| Apple Watch Ultra 2 `49mm` | `205 x 251 pt` | `410 x 502 px` | `@2x` | `338` | Compact | N/A | `38 pt` |
| Apple Vision Pro default window | `1280 x 720 pt` | Dynamic foveated | `@2x` virtual | N/A | Regular W, Regular H | Regular W, Regular H | `36 pt` to `44 pt` |

## Bars, navigation, and component specifications

### System bars

| Component | Compact portrait height | Compact landscape height | iPadOS or Regular height | Total height with safe area on Dynamic Island iPhone | Key inner metrics |
| --- | --- | --- | --- | --- | --- |
| Status bar | `54 pt` to `59 pt` | `0 pt` hidden by default | `24 pt` | `59 pt` | `15 pt` Semibold time on left, cellular, Wi-Fi, and battery icons on right; Dynamic Island cutout is `126 x 37 pt` centered `11 pt` from top |
| Navigation bar inline | `44 pt` | `32 pt` | `50 pt` | `103 pt`, `59 pt` plus `44 pt` | `17 pt` Headline centered title; `17 pt` Regular back button and trailing action buttons, `Semibold` for `Done`, `16 pt` outer margin |
| Navigation bar with Large Title | `96 pt`, `44 pt` bar plus `52 pt` title row | `32 pt` collapses to inline | `102 pt`, `50 pt` plus `52 pt` | `155 pt`, `59 pt` plus `96 pt` | `34 pt` Bold Large Title aligned to `16 pt` leading margin, `8 pt` bottom padding |
| Navigation bar with search field | `+52 pt` additional row | `+44 pt` | `+52 pt` | `155 pt` inline or `207 pt` with Large Title | `36 pt` search pill height, `16 pt` horizontal margin, `8 pt` top and bottom padding, `10 pt` corner radius |
| Tab bar | `49 pt` | `32 pt` | `50 pt` floating pill or top bar | `83 pt`, `49 pt` plus `34 pt` home indicator | `2 to 5` items on iPhone; `25 x 25 pt` icon above `10 pt` Medium label in portrait; `18 x 18 pt` icon beside `13 pt` Regular label in landscape |
| Bottom toolbar | `44 pt` | `32 pt` | `50 pt` | `78 pt`, `44 pt` plus `34 pt` home indicator | Maximum `5` icon buttons or `3` text buttons; `22 x 22 pt` icon size |
| Home indicator pill | `34 pt` safe area container | `21 pt` safe area container | `20 pt` safe area container | Included in bottom inset | Visual pill is `134 x 5 pt`, or `140 x 5 pt` on Plus and Max, with `2.5 pt` radius, positioned `8 pt` above bottom screen edge |
| iPadOS sidebar | N/A | N/A | Full height | Full height | `260 pt` to `320 pt` width, `320 pt` standard primary split column, `44 pt` row height, `10 pt` active row corner radius |
| macOS window toolbar | N/A | N/A | `52 pt` standard, `38 pt` unified compact, `28 pt` title bar only | N/A | Traffic light window controls use `12 x 12 pt` circles, `8 pt` gap, `20 pt` leading inset |

### Lists, tables, and cells

| Metric | Specification | Notes |
| --- | --- | --- |
| Single-line row height | `44 pt` minimum | `17 pt` Body label on left, optional `17 pt` `secondaryLabel` value on right, `11 pt` to `12 pt` vertical padding |
| Two-line subtitle row height | `60 pt`, `58 pt` to `64 pt` range | `17 pt` Body primary label plus `2 pt` gap plus `15 pt` Subheadline or `13 pt` Footnote `secondaryLabel` subtitle, `10 pt` to `12 pt` vertical padding |
| Three-line row height | `76 pt` to `88 pt` | `17 pt` Headline or Body plus `15 pt` Subheadline plus `13 pt` Footnote across `2 lines`, `12 pt` vertical padding |
| Leading settings icon tile | `29 x 29 pt` | `7 pt` continuous corner radius, `18 x 18 pt` white glyph centered inside, `15 pt` to `16 pt` gap to row title |
| Leading avatar or thumbnail | `40 x 40 pt`, `48 x 48 pt` for prominent rows | `20 pt` circle for people, `8 pt` continuous squircle for media thumbnails, `12 pt` gap to text |
| Disclosure chevron `chevron.right` | `7 x 12 pt`, `13 pt` Semibold SF Symbol | Colored `tertiaryLabel`, `#3C3C434D` in Light and `#EBEBF54D` in Dark, `8 pt` to `12 pt` gap from trailing detail label |
| Checkmark accessory `checkmark` | `14 x 14 pt`, `17 pt` Semibold SF Symbol | Colored with app `tint`, `systemBlue` `#007AFF` default |
| Separator inset | `16 pt`, `20 pt` on Plus and Max | Aligns with leading edge of row text, `59 pt` to `60 pt` inset when row has a `29 pt` leading icon tile |
| Grouped section header | `13 pt` Footnote uppercase or `15 pt` Subheadline Semibold | `secondaryLabel` color, `16 pt` horizontal inset from card edge, `32 pt` from screen edge, `6 pt` to `8 pt` bottom padding above card |
| Grouped section footer | `13 pt` Footnote Regular | `secondaryLabel` color, `18 pt` line height, `6 pt` to `8 pt` top padding below card |
| Inset grouped card corner radius | `10 pt`, `12 pt` on iPadOS and visionOS | Continuous corner curve |

### Controls and inputs

| Control | Dimensions | Typography and internal geometry |
| --- | --- | --- |
| Button `small` | `28 pt` visual height, `44 x 44 pt` hit region | `13 pt` Footnote Regular or Semibold, `10 pt` horizontal padding, `4 pt` vertical padding, `14 pt` capsule or `6 pt` rounded rect |
| Button `medium` | `34 pt` visual height, `44 x 44 pt` hit region | `15 pt` Subheadline Regular or Semibold, `12 pt` to `14 pt` horizontal padding, `7 pt` vertical padding, `17 pt` capsule or `8 pt` rounded rect |
| Button `large` | `50 pt` height, `44 pt` to `54 pt` range | `17 pt` Body Semibold, `16 pt` to `20 pt` horizontal padding, `14 pt` vertical padding, `12 pt` to `14 pt` continuous corner radius or `25 pt` capsule |
| Toggle switch `UISwitch` | `51 x 31 pt` | `15.5 pt` pill radius; `27 x 27 pt` white thumb with `2 pt` track inset and `0 3px 8px rgba(0,0,0,0.15)` shadow; active track `systemGreen` `#34C759` |
| Segmented control | `28 pt` standard, `32 pt` prominent | `8.9 pt` outer track radius, `6.9 pt` active thumb radius, `2 pt` track padding, `13 pt` Footnote, `Medium` unpicked and `Semibold` active |
| Slider `UISlider` | `44 pt` interactive height, `4 pt` track thickness | `28 x 28 pt` circular white thumb with `14 pt` radius, `2 pt` track corner radius, `systemBlue` filled side, `systemFill` unfilled side |
| Stepper `UIStepper` | `94 x 32 pt` | Two `47 x 32 pt` segments separated by `1 px` divider `13 pt` tall, `8 pt` corner radius |
| Text field `UITextField` | `44 pt` standalone row height, `36 pt` compact inline | `17 pt` Body text, `placeholderText` in `tertiaryLabel`, `12 pt` to `16 pt` horizontal padding, `10 pt` corner radius, `19 x 19 pt` clear button `xmark.circle.fill` |
| Search field `UISearchTextField` | `36 pt` height | `17 pt` Body text, `10 pt` corner radius, `18 pt` capsule on iOS 18+ bottom bars and visionOS, `8 pt` leading magnifying glass inset |
| Page control `UIPageControl` | `24 pt` visual height, `44 pt` tap height | `8 x 8 pt` dots, `8 pt` dot-to-dot gap, active dot `100%` `label`, inactive dots `30%` `tertiaryLabel` |
| Activity indicator `UIActivityIndicatorView` | `20 x 20 pt` medium, `37 x 37 pt` large | `8` spoke ticks |

### Sheets, alerts, action sheets, and menus

| Component | Width and height | Corner radius and padding | Internal typography and layout |
| --- | --- | --- | --- |
| Modal sheet, `medium` and `large` detents | Full width on iPhone; `540 x 620 pt` form sheet on iPad, `624 x 650 pt` page sheet | `10 pt` to `16 pt` top corners, `38 pt` to `55 pt` bottom corners matching screen bezel | Grabber `36 x 5 pt` with `2.5 pt` radius centered `5 pt` from top edge; `44 pt` to `56 pt` header bar; parent view scales to `0.92x` with `10 pt` top offset when stacked |
| Alert `UIAlertController.Style.alert` | `270 pt` fixed width | `14 pt` continuous corner radius; `20 pt` top and `16 pt` horizontal text padding | `17 pt` Headline centered title; `13 pt` Footnote centered message `4 pt` below title; `44 pt` button height separated by `0.33 pt` or `0.5 pt` dividers; `17 pt` Regular for Cancel, `17 pt` Semibold for preferred action, `systemRed` for destructive |
| Action sheet | `8 pt` horizontal screen margin, `359 pt` to `424 pt` width on iPhone; popover on iPad | `14 pt` continuous corner radius | Optional header with `13 pt` Footnote Semibold title and `13 pt` Regular message, `14 pt` vertical padding; `56 pt` to `57 pt` action button height with `20 pt` Regular text; `8 pt` gap above separate `56 pt` Cancel button with `20 pt` Semibold text |
| Context menu and pull-down menu `UIMenu` | `250 pt` standard width, `180 pt` to `280 pt` range | `13 pt` continuous corner radius | `44 pt` row height, `16 pt` horizontal padding, `17 pt` Body label on left, `20 x 20 pt` SF Symbol on right, `8 pt` section separator between menu groups |
| Popover on iPadOS and macOS | `320 pt` to `400 pt` typical width | `13 pt` continuous corner radius, `13 x 7 pt` arrow | `16 pt` internal padding, `0 12px 32px rgba(0,0,0,0.16)` drop shadow |

## Corner radii and concentric geometry

Apple interfaces use continuous curvature, `CALayerCornerCurve.continuous` or SwiftUI `.continuous`, which blends straight edges into curves smoothly without the abrupt tangent jump of standard CSS circles.

- **Concentric radius rule.** When a rounded element sits inside a rounded container with uniform padding $d$, calculate the inner radius by subtracting $d$ from the outer radius, floored at zero: $R_{\text{inner}} = R_{\text{outer}} - d$. For example, a card with $R_{\text{outer}} = 20\text{ pt}$ and $8\text{ pt}$ padding contains an inner image or button with $R_{\text{inner}} = 12\text{ pt}$.

| Element tier | Corner radius | Notes |
| --- | --- | --- |
| Micro badges, status pills, keyboard keys | `4 pt` to `6 pt` | `5 pt` on iOS virtual keyboard keys, `32 x 42 pt` key size |
| Small buttons, segmented control active thumb, settings icon tiles | `6 pt` to `8 pt` | `7 pt` for `29 x 29 pt` settings icons |
| Inset grouped list cards, text fields, search bars, medium buttons | `10 pt` to `12 pt` | `10 pt` standard iOS grouped card, `12 pt` on iPadOS |
| Large primary buttons, alerts, context menus, notifications | `13 pt` to `16 pt` | `14 pt` for alerts, action sheets, and notification banners |
| Home screen widgets `systemSmall`, `systemMedium`, `systemLarge` | `20 pt` to `24 pt` | `22 pt` standard iOS widget corner radius with `16 pt` inner content padding |
| Bottom sheets, floating islands, full-bleed cards near bezel | `24 pt` to `55 pt` | Concentric with device screen radius: `55 pt` minus `8 pt` margin equals `47 pt` for floating bottom cards on iPhone 16 Pro |
| App icon | `22.37%` of icon width | `13.4 pt` on `60 x 60 pt` icon, `229 px` on `1024 x 1024 px` icon |

## Contrast, color, and accessibility

### Contrast ratio requirements

Test every foreground-background pair in all four system modes: Light, Dark, High-Contrast Light, and High-Contrast Dark.

| Element category | Size threshold | Standard mode minimum contrast | Increased Contrast mode minimum | WCAG level |
| --- | --- | --- | --- | --- |
| Normal text: `Caption 2`, `Caption 1`, `Footnote`, `Subheadline`, `Callout` | `< 17 pt` Regular or `< 14 pt` Bold | `4.5 : 1` | `7.0 : 1` | AA standard, AAA increased contrast |
| Large text: `Body`, `Headline`, `Title 3`, `Title 2`, `Title 1`, `Large Title` | `>= 17 pt` Regular or `>= 14 pt` Bold, `>= 18.66 px` bold or `>= 24 px` regular in CSS | `3.0 : 1` | `4.5 : 1` | AA Large standard, AAA Large increased contrast |
| Active icons, SF Symbols, control boundaries, focus rings, chart series | Any size | `3.0 : 1` | `4.5 : 1` | WCAG 1.4.11 Non-text contrast |
| Disabled controls and decorative dividers | Any size | Exempt from `4.5:1`, typically `1.8 : 1` to `2.5 : 1` using `tertiaryLabel` or `quaternaryLabel` | Increase opacity by `+15%` to `+25%` in Increased Contrast mode | Keep disabled state recognizable without relying on color alone |

### Apple system accent colors

Never hard-code a single static hex value for interactive elements. Use semantic system colors or CSS custom properties that switch between Light, Dark, High-Contrast Light, and High-Contrast Dark.

| Semantic token | Light mode hex and RGB | Dark mode hex and RGB | High-contrast Light hex | High-contrast Dark hex |
| --- | --- | --- | --- | --- |
| `systemBlue` | `#007AFF` `rgb(0, 122, 255)` | `#0A84FF` `rgb(10, 132, 255)` | `#0040DD` `rgb(0, 64, 221)` | `#409CFF` `rgb(64, 156, 255)` |
| `systemGreen` | `#34C759` `rgb(52, 199, 89)` | `#30D158` `rgb(48, 209, 88)` | `#248A3D` `rgb(36, 138, 61)` | `#30DB5B` `rgb(48, 219, 91)` |
| `systemIndigo` | `#5856D6` `rgb(88, 86, 214)` | `#5E5CE6` `rgb(94, 92, 230)` | `#3634A3` `rgb(54, 52, 163)` | `#7D7AFF` `rgb(125, 122, 255)` |
| `systemOrange` | `#FF9500` `rgb(255, 149, 0)` | `#FF9F0A` `rgb(255, 159, 10)` | `#C93400` `rgb(201, 52, 0)` | `#FFB340` `rgb(255, 179, 64)` |
| `systemPink` | `#FF2D55` `rgb(255, 45, 85)` | `#FF375F` `rgb(255, 55, 95)` | `#D30F45` `rgb(211, 15, 69)` | `#FF6482` `rgb(255, 100, 130)` |
| `systemPurple` | `#AF52DE` `rgb(175, 82, 222)` | `#BF5AF2` `rgb(191, 90, 242)` | `#8944AB` `rgb(137, 68, 171)` | `#DA8FFF` `rgb(218, 143, 255)` |
| `systemRed` | `#FF3B30` `rgb(255, 59, 48)` | `#FF453A` `rgb(255, 69, 58)` | `#D70015` `rgb(215, 0, 21)` | `#FF6961` `rgb(255, 105, 97)` |
| `systemTeal` | `#30B0C7` `rgb(48, 176, 199)` | `#40C8E0` `rgb(64, 200, 224)` | `#008299` `rgb(0, 130, 153)` | `#5DE6FF` `rgb(93, 230, 255)` |
| `systemCyan` | `#32ADE6` `rgb(50, 173, 230)` | `#64D2FF` `rgb(100, 210, 255)` | `#0071A4` `rgb(0, 113, 164)` | `#70D7FF` `rgb(112, 215, 255)` |
| `systemMint` | `#00C7BE` `rgb(0, 199, 190)` | `#63E6E2` `rgb(99, 230, 226)` | `#0C817B` `rgb(12, 129, 123)` | `#66D4CF` `rgb(102, 212, 207)` |
| `systemYellow` | `#FFCC00` `rgb(255, 204, 0)` | `#FFD60A` `rgb(255, 214, 10)` | `#B25000` `rgb(178, 80, 0)` | `#FFD426` `rgb(255, 212, 38)` |
| `systemBrown` | `#A2845E` `rgb(162, 132, 94)` | `#AC8E68` `rgb(172, 142, 104)` | `#7F6545` `rgb(127, 101, 69)` | `#B59469` `rgb(181, 148, 105)` |

### Apple system gray ramp

| Gray token | Light mode hex and RGB | Dark mode hex and RGB | High-contrast Light hex | High-contrast Dark hex |
| --- | --- | --- | --- | --- |
| `systemGray` | `#8E8E93` `rgb(142, 142, 147)` | `#8E8E93` `rgb(142, 142, 147)` | `#6C6C70` `rgb(108, 108, 112)` | `#AEAEB2` `rgb(174, 174, 178)` |
| `systemGray2` | `#AEAEB2` `rgb(174, 174, 178)` | `#636366` `rgb(99, 99, 102)` | `#8E8E93` `rgb(142, 142, 147)` | `#7C7C80` `rgb(124, 124, 128)` |
| `systemGray3` | `#C7C7CC` `rgb(199, 199, 204)` | `#48484A` `rgb(72, 72, 74)` | `#AEAEB2` `rgb(174, 174, 178)` | `#545456` `rgb(84, 84, 86)` |
| `systemGray4` | `#D1D1D6` `rgb(209, 209, 214)` | `#3A3A3C` `rgb(58, 58, 60)` | `#BCBCC0` `rgb(188, 188, 192)` | `#444446` `rgb(68, 68, 70)` |
| `systemGray5` | `#E5E5EA` `rgb(229, 229, 234)` | `#2C2C2E` `rgb(44, 44, 46)` | `#D8D8DC` `rgb(216, 216, 220)` | `#363638` `rgb(54, 54, 56)` |
| `systemGray6` | `#F2F2F7` `rgb(242, 242, 247)` | `#1C1C1E` `rgb(28, 28, 30)` | `#EBEBF0` `rgb(235, 235, 240)` | `#242426` `rgb(36, 36, 38)` |

### Semantic labels, backgrounds, fills, and separators

In Dark Mode, Apple distinguishes **Base** surfaces, which are full-screen root views, from **Elevated** surfaces, which are sheets, popovers, split-view sidebars, and floating cards, by raising background luminance rather than adding dark drop shadows.

| Semantic token | Light mode value | Dark mode Base value | Dark mode Elevated value | Purpose |
| --- | --- | --- | --- | --- |
| `label` | `#000000` `100%` | `#FFFFFF` `100%` | `#FFFFFF` `100%` | Primary titles, body copy, row titles |
| `secondaryLabel` | `rgba(60, 60, 67, 0.60)` `#3C3C4399` | `rgba(235, 235, 245, 0.60)` `#EBEBF599` | `rgba(235, 235, 245, 0.60)` `#EBEBF599` | Subtitles, section headers, secondary values |
| `tertiaryLabel` | `rgba(60, 60, 67, 0.30)` `#3C3C434D` | `rgba(235, 235, 245, 0.30)` `#EBEBF54D` | `rgba(235, 235, 245, 0.30)` `#EBEBF54D` | Placeholder text, disabled text, disclosure chevrons |
| `quaternaryLabel` | `rgba(60, 60, 67, 0.18)` `#3C3C432E` | `rgba(235, 235, 245, 0.16)` `#EBEBF529` | `rgba(235, 235, 245, 0.16)` `#EBEBF529` | Watermarks, subtle inactive marks |
| `systemBackground` | `#FFFFFF` | `#000000` | `#1C1C1E` | Primary canvas for plain lists and flat screens |
| `secondarySystemBackground` | `#F2F2F7` | `#1C1C1E` | `#2C2C2E` | Secondary cards or grouped areas on a primary canvas |
| `tertiarySystemBackground` | `#FFFFFF` | `#2C2C2E` | `#3A3A3C` | Nested elements inside secondary backgrounds |
| `systemGroupedBackground` | `#F2F2F7` | `#000000` | `#1C1C1E` | Root canvas behind inset grouped lists and settings screens |
| `secondarySystemGroupedBackground` | `#FFFFFF` | `#1C1C1E` | `#2C2C2E` | Inset grouped card surface sitting on `systemGroupedBackground` |
| `tertiarySystemGroupedBackground` | `#F2F2F7` | `#2C2C2E` | `#3A3A3C` | Controls or wells nested inside an inset grouped card |
| `systemFill` | `rgba(120, 120, 128, 0.20)` | `rgba(120, 120, 128, 0.36)` | `rgba(120, 120, 128, 0.36)` | Thin tracks, slider backgrounds, medium button fills |
| `secondarySystemFill` | `rgba(120, 120, 128, 0.16)` | `rgba(120, 120, 128, 0.32)` | `rgba(120, 120, 128, 0.32)` | Search bar backgrounds, segmented control tracks |
| `tertiarySystemFill` | `rgba(118, 118, 128, 0.12)` | `rgba(118, 118, 128, 0.24)` | `rgba(118, 118, 128, 0.24)` | Subtle pill backgrounds, table cell hover states |
| `quaternarySystemFill` | `rgba(116, 116, 128, 0.08)` | `rgba(116, 116, 128, 0.18)` | `rgba(116, 116, 128, 0.18)` | Large subtle container fills |
| `separator` | `rgba(60, 60, 67, 0.29)` | `rgba(84, 84, 88, 0.60)` | `rgba(84, 84, 88, 0.60)` | Translucent `0.33 pt` or `0.5 pt` list row dividers |
| `opaqueSeparator` | `#C6C6C8` | `#38383A` | `#38383A` | Non-translucent hairline dividers |

## Materials, blur, and elevation

Never use arbitrary opaque gray bars or uncalibrated glassmorphism. Use Apple's system material hierarchy so scrolled content lends subtle color vibrancy through bars, sheets, and overlays.

| Material token | Blur radius | Saturation boost | Light mode tint overlay | Dark mode tint overlay | Border hairline |
| --- | --- | --- | --- | --- | --- |
| `ultraThinMaterial` | `20 px` | `180%` | `rgba(255, 255, 255, 0.45)` | `rgba(30, 30, 30, 0.45)` | `0.5px solid rgba(255, 255, 255, 0.25)` |
| `thinMaterial` | `24 px` | `180%` | `rgba(255, 255, 255, 0.60)` | `rgba(30, 30, 30, 0.60)` | `0.5px solid rgba(255, 255, 255, 0.20)` |
| `regularMaterial` | `30 px` | `180%` | `rgba(255, 255, 255, 0.78)` | `rgba(30, 30, 30, 0.75)` | `0.5px solid rgba(0, 0, 0, 0.10)` light, `rgba(255, 255, 255, 0.14)` dark |
| `thickMaterial` | `40 px` | `180%` | `rgba(255, 255, 255, 0.88)` | `rgba(30, 30, 30, 0.88)` | `0.5px solid rgba(0, 0, 0, 0.12)` light, `rgba(255, 255, 255, 0.16)` dark |
| `chromeMaterial` for bars | `20 px` to `30 px` | `180%` | `rgba(249, 249, 249, 0.80)` | `rgba(22, 22, 22, 0.78)` | `0.33pt solid rgba(60, 60, 67, 0.29)` light, `rgba(84, 84, 88, 0.65)` dark |
| `visionOS glass` | `40 px` | `190%` | `rgba(255, 255, 255, 0.22)` | `rgba(40, 40, 45, 0.38)` | `1px` specular rim gradient `rgba(255,255,255,0.45)` top-left to `rgba(255,255,255,0.08)` bottom-right |

## Motion, haptics, and iconography

### Spring animation parameters

Apple motion uses spring physics driven by velocity and gesture continuation, never linear easing.

| Interaction | Response or duration | Damping ratio | Equivalent cubic-bezier | Behavior |
| --- | --- | --- | --- | --- |
| Button press or touch down | `0.15 s` to `0.20 s` | `0.90` | `cubic-bezier(0.25, 1, 0.5, 1)` | Scale to `0.97` or reduce opacity to `0.75` immediately on touch down |
| Toggle, tab switch, segmented control | `0.25 s` | `0.85` | `cubic-bezier(0.2, 0.9, 0.3, 1)` | Crisp slide with minimal overshoot |
| Navigation push or pop, sheet presentation | `0.35 s`, `350 ms` to `400 ms` | `0.88` to `1.00` | `cubic-bezier(0.32, 0.72, 0, 1)` | Critically damped; incoming screen slides from `100%` right while outgoing screen shifts `-30%` left with `0.10` dimming |
| Interactive card expand or springy drag release | `0.40 s` to `0.50 s` | `0.75` to `0.82` | `cubic-bezier(0.16, 1, 0.3, 1)` | Preserves user release velocity |
| Reduce Motion active, `prefers-reduced-motion: reduce` | `0.20 s` | `1.00` | `ease-in-out` | Replace spatial slides, zooms, and parallax with a `200 ms` opacity crossfade |

### SF Symbols and app icon sizing

| Category | Metric or variant | Specification |
| --- | --- | --- |
| SF Symbol weight matching | `Ultralight` to `Black` | Match adjacent font weight: `Regular` for Body, `Semibold` for Headline and bar buttons |
| SF Symbol `Small` scale | `1.00x` cap height | `~13 pt` bounding box at `17 pt` Body, used inline within sentences or compact badges |
| SF Symbol `Medium` scale | `1.18x` cap height | `~17 x 17 pt` to `20 x 20 pt` at `17 pt` Body, default for list rows, buttons, and menus |
| SF Symbol `Large` scale | `1.38x` cap height | `~22 x 22 pt` to `25 x 25 pt` at `17 pt` Body, used in navigation bars, tab bars, and toolbars |
| App Store master icon | `1024 x 1024 px` | `@1x`, sRGB or Display P3, opaque with no alpha channel |
| iPhone Home Screen icon | `60 x 60 pt`, `180 x 180 px` at `@3x` | `64 x 64 pt`, `192 x 192 px` at `@3x`, on iPhone 16 Pro Max |
| iPad Home Screen icon | `76 x 76 pt`, `152 x 152 px` at `@2x` | `83.5 x 83.5 pt`, `167 x 167 px` at `@2x`, on iPad Pro |
| Spotlight search icon | `40 x 40 pt` | `120 x 120 px` at `@3x`, `80 x 80 px` at `@2x` |
| Settings row icon | `29 x 29 pt` | `87 x 87 px` at `@3x`, `58 x 58 px` at `@2x`, `7 pt` corner radius |
| Notification banner icon | `20 x 20 pt` | `60 x 60 px` at `@3x`, `40 x 40 px` at `@2x` |

## Implementation checklist for every app or mobile screen

When generating SwiftUI, UIKit, React Native, Flutter, or HTML and CSS mobile screens, verify all ten rules before finishing:

1. **Viewport and safe areas.** Frame mobile prototypes in a real Apple viewport such as `393 x 852 pt` for iPhone 16 or `402 x 874 pt` for iPhone 16 Pro, with a `59 pt` top safe area and `34 pt` bottom home indicator inset.
2. **Tap targets.** Confirm every tappable control has at least a `44 x 44 pt` hit box, `60 x 60 pt` on visionOS, `28 x 28 pt` on macOS, and `8 pt` minimum separation.
3. **Typography.** Use the exact Apple Dynamic Type ramp: `34 pt` Large Title, `28 pt` Title 1, `22 pt` Title 2, `20 pt` Title 3, `17 pt` Headline and Body with `-0.41 pt` tracking, `15 pt` Subheadline, `13 pt` Footnote, `12 pt` Caption 1, and `11 pt` Caption 2 floor.
4. **Margins and grid.** Enforce `16 pt` outer horizontal screen margins, `20 pt` on Plus and Max, `16 pt` internal card padding for a `32 pt` total text inset in inset-grouped lists, `44 pt` minimum row height, `60 pt` for subtitle rows, and `8 pt` grid multiples.
5. **System navigation.** Use a `44 pt` inline navigation bar, `96 pt` with Large Title, and a `49 pt` tab bar, `83 pt` with safe area, holding `2 to 5` top-level destinations. Never invent a hamburger drawer or bottom action bar disguised as a tab bar.
6. **Semantic colors.** Use Apple's semantic color tokens: `label`, `secondaryLabel` `#3C3C4399` light and `#EBEBF599` dark, `tertiaryLabel` `#3C3C434D` light and `#EBEBF54D` dark, `systemGroupedBackground` `#F2F2F7` light and `#000000` dark, `secondarySystemGroupedBackground` `#FFFFFF` light and `#1C1C1E` dark, and support both Light and Dark Mode using elevated luminance `#1C1C1E` to `#2C2C2E` in Dark Mode.
7. **Contrast ratios.** Verify `4.5:1` minimum contrast on text under `17 pt`, `7.0:1` for Increased Contrast, and `3.0:1` minimum on large text `>= 17 pt` and active icons.
8. **Corner concentricity.** Use continuous squircle corners: `10 pt` to `12 pt` on grouped cards and inputs, `14 pt` on alerts and large buttons, `7 pt` on `29 x 29 pt` icon tiles, and subtract padding $d$ from outer radius $R_{\text{outer}}$ for nested elements.
9. **Materials.** Use `backdrop-filter: saturate(180%) blur(20px)` on bars and sheets so content scrolls underneath with subtle vibrancy.
10. **Platform fidelity.** Use `0.33 pt` or `0.5 pt` inset separators, `51 x 31 pt` switches, `28 pt` or `32 pt` segmented controls, `270 pt` alerts, and weight-matched SF Symbols.
