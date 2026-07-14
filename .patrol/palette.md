# Palette — Design / UX Patrol Log

## 2026-06-10
- FileUploadModal missing backdrop click and Escape key dismissal — added backdrop onClick + document-level Escape handler + proper ARIA dialog attributes

## 2026-06-13
- RecipeCard delete confirmation modal missing Escape key dismissal and ARIA dialog attributes — added document-level Escape handler + role/aria-modal/aria-label — opened PR #15

## 2026-06-14
- CalculatorView save and delete modals missing ARIA dialog attributes and Escape key dismissal — added document-level Escape handlers + role/aria-modal/aria-label, removed dead backdrop onKeyDown — opened PR #21

## 2026-06-15
- FreezingSection expanded chart modal missing ARIA dialog attributes, Escape key dismissal, backdrop click, and close button aria-label — added role/aria-modal/aria-label, document-level Escape handler, backdrop onClick, and descriptive aria-label on close button — opened PR #27

## 2026-06-16
- RecipePickerModal missing ARIA dialog attributes and Escape key dismissal — added role/aria-modal/aria-label on outer container and document-level Escape handler — opened PR #31

## 2026-06-17
- Mobile hamburger menu missing Escape key dismissal — added useEffect with document-level Escape handler — opened PR #35

## 2026-06-18
- Mobile hamburger menu missing focus management — added focus-to-first-link on open, focus-return-to-button on close — opened PR #38

## 2026-07-02
- 404 page missing back-to-home navigation — added "Back to Home" link with ArrowLeft icon on the 404 page, styled as primary button — opened PR #62

## 2026-07-03
- DaisyUI data-tip tooltips invisible to screen readers — added sr-only span to Tooltip component and aria-hidden to InfoIcon HelpCircle icon — opened PR #64

## 2026-07-04
- ProfileFormModal, IngredientFormModal, ProfilesView delete confirm, IngredientsView delete confirm — added Escape key dismissal and ARIA dialog attributes — opened PR #73

## 2026-07-05
- App header missing skip-to-content link (WCAG 2.4.1) — added visually-hidden skip link as first focusable element with #main-content target via tabIndex container; added aria-label to both desktop and mobile nav elements — opened PR #77

## 2026-07-06
- All pages missing document.title (WCAG 2.4.2) — added useEffect to set meaningful page titles on Calculator, Ingredients, Recipes, Profiles, 404, and Home — opened PR #82

## 2026-07-07
- RecipeCard icon-only export and delete buttons missing aria-label — added aria-label matching existing codebase pattern — opened PR #87

## 2026-07-08
- FileUploadModal X close button missing aria-label — all other icon-only buttons had it, but this one was missed — opened PR #93

## 2026-07-13
- IngredientsView and ProfilesView missing `<main>` landmark — both used `<div>` while other pages used `<main>`, breaking landmark navigation for screen readers (WCAG 1.3.1) — opened PR #99

## 2026-07-14
- Added `<meta name="description">` and `<meta name="theme-color">` to index.html for mobile browser chrome matching and link previews — opened PR #101
- Fixed ProfileFormModal heading always showing "Create a new target profile" even when editing — opened PR #101
