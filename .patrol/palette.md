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
