# Design QA

## Source visual truth

- Reference: `/var/folders/f6/cq6x74ks52z818wcczbq0ssm0000gn/T/codex-clipboard-5aff2038-2b1b-4c58-9fa0-9d26f9f41c86.png`
- Additional references: `/var/folders/f6/cq6x74ks52z818wcczbq0ssm0000gn/T/codex-clipboard-c0b02fb8-85ee-430f-9694-fc8434e3b90c.png`, `/var/folders/f6/cq6x74ks52z818wcczbq0ssm0000gn/T/codex-clipboard-fa084576-18d0-4dba-a27e-a15efa3989f8.png`
- Direction: mobile green visual system, large rounded hero, white layered cards, bottom navigation, touch-friendly actions, floating metric cards, segmented visualization, and intelligent operational prompts.

## Implementation

- Routes: `http://127.0.0.1:5002/` and `http://127.0.0.1:5002/dashboard`
- Intended viewport: 390 × 844 CSS px, device scale factor 1.
- Current browser capture: desktop viewport 1280 × 720 CSS px; a matching mobile viewport capture could not be produced in the available browser surface.

## Comparison

- Full-view comparison: blocked because the rendered implementation and source cannot be normalized to the same mobile viewport in the available browser surface.
- Focused comparison: CSS and template inspection confirm the mobile-specific green hero, layered white cards, bottom touch navigation, 44px controls, and responsive table overflow are implemented.

## Findings

- [P2] Mobile visual capture remains unavailable; visual fidelity cannot be formally signed off from the browser surface.

## Implementation Checklist

- [x] Apply green mobile hero and white layered card language.
- [x] Convert the sidebar to a bottom navigation under 600px.
- [x] Increase mobile touch targets and preserve readable operation actions.
- [x] Keep tables and process rails usable with horizontal scrolling.
- [x] Add a visual production cockpit with order segmentation, line utilization bars, inventory metrics, alerts, and activity feed.
- [x] Run Python compilation, route rendering, and mobile CSS marker checks.

final result: blocked
