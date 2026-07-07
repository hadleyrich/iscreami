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

## 2026-07-07
- RecipeCard icon-only export and delete buttons missing aria-label — added aria-label matching existing codebase pattern — opened PR #87
