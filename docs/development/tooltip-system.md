# Tooltip System Documentation

## Overview

A consistent, app-wide tooltip system has been implemented using DaisyUI v5 components to help new users understand ice cream recipe calculations.

## Components

### `Tooltip`

A wrapper component that displays tooltip text on hover using DaisyUI's `@tooltip` class.

**File:** `src/components/Tooltip.tsx`

**Usage:**

```tsx
import { Tooltip } from "./Tooltip";

<Tooltip content="This explains what this element does" position="top">
  <button>Hover me</button>
</Tooltip>;
```

**Props:**

- `content` (string, required): The tooltip text
- `position` ('top' | 'bottom' | 'left' | 'right', optional): Tooltip position (default: 'top')
- `children` (ReactNode, required): The element that triggers the tooltip

### `InfoIcon`

A help circle icon that displays a tooltip when hovered. Use this for inline help next to labels.

**File:** `src/components/InfoIcon.tsx`

**Usage:**

```tsx
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

<div className="flex items-center gap-1">
  <label>Total Fat</label>
  <InfoIcon label={TOOLTIPS.totalFat} position="bottom" />
</div>;
```

**Props:**

- `label` (string, required): The tooltip text
- `position` ('top' | 'bottom' | 'left' | 'right', optional): Tooltip position (default: 'top')
- `className` (string, optional): Additional CSS classes

## Tooltip Content

All tooltip content is centralized in `src/lib/tooltips.ts` for easy maintenance and updates.

**Structure:**

```tsx
export const TOOLTIPS = {
  // Group by feature/component
  profileName: "Explain what this means...",
  metricName: "Explain what this metric does...",
  // ... etc
};
```

**Adding New Tooltips:**

1. Add the tooltip text to `TOOLTIPS` object with a descriptive key
2. Import and use it in your component:

```tsx
import { TOOLTIPS } from "../lib/tooltips";
import { InfoIcon } from "./InfoIcon";

<InfoIcon label={TOOLTIPS.yourNewKey} position="top" />;
```

## Components Updated with Tooltips

### Already Implemented:

- ✅ **MetricCards.tsx** - Metric definitions (Total Solids, Fat, MSNF, etc.)
- ✅ **CompositionTable.tsx** - Composition breakdown with tooltips on key metrics
- ✅ **FreezingSection.tsx** - PAC, Freezing Point, Serving Temperature
- ✅ **SweetnessSection.tsx** - POD (Potere Dolcificante) sweetness explanation
- ✅ **IngredientPanel.tsx** - Ingredient header explanation
- ✅ **CalculatorView.tsx** - Profile selector, recipe buttons, section headers
- ✅ **IngredientFormModal.tsx** - PAC/POD override fields with explanations
- ✅ **NutritionTable.tsx** - Individual nutrition metrics (Total Fat, Sugars, Protein)
- ✅ **IngredientsView.tsx** - Ingredient database view and purpose
- ✅ **HomePage.tsx** - Navigation cards for Calculator and Ingredients
- ✅ **App.tsx** - Header navigation links

### Areas for Future Tooltips:

1. **RecipePickerModal.tsx** - Recipe selection help
2. **IngredientSearch.tsx** - Search tips for finding ingredients
3. **Additional nutrition metrics** - Saturated fat, fiber, carbohydrates details
4. **Profile explanations** - What different recipe profiles mean
5. **Ingredient categories** - Description of each category type

## Positioning Best Practices

- **top** (default) - Use for section headers, when tooltip won't overlap content
- **bottom** - Use for metric cards, ingredient list items (prevents overlap with top of page)
- **left** - Use for right-aligned elements like buttons
- **right** - Use for left-aligned labels, elements on the left side

## Styling

Tooltips inherit DaisyUI styling and respect light/dark mode via the existing theme system. Key styles:

- **Icon appearance:** `w-4 h-4`, muted color `text-base-content/50`
- **Hover state:** Brightens on hover with `hover:text-base-content/70`
- **Cursor:** Changes to `cursor-help` on hover
- **Animation:** DaisyUI provides smooth fade-in on hover

## Best Practices

1. **Keep text concise** - Tooltips work best with 1-2 sentences max
2. **Use simple language** - Target new users unfamiliar with ice cream science
3. **Avoid duplication** - Don't repeat what's obvious from the UI label
4. **Be context-aware** - Explain _why_ something matters, not just _what_ it is
5. **Update centrally** - Always modify `TOOLTIPS` object, not hardcoded strings

## Example: Adding Tooltips to a New Component

```tsx
import { InfoIcon } from "./InfoIcon";
import { TOOLTIPS } from "../lib/tooltips";

export function MyComponent() {
  return (
    <div className="space-y-2">
      {/* Option 1: Tooltip on wrapper element */}
      <Tooltip content={TOOLTIPS.myFeature} position="top">
        <button>My Button</button>
      </Tooltip>

      {/* Option 2: InfoIcon next to label (recommended for forms) */}
      <div className="flex items-center gap-1">
        <label>My Field</label>
        <InfoIcon label={TOOLTIPS.myField} position="right" />
      </div>

      {/* Option 3: Tooltip on clickable text */}
      <Tooltip content={TOOLTIPS.myDetail}>
        <a href="#" className="link">
          Learn more
        </a>
      </Tooltip>
    </div>
  );
}
```

## Testing Tooltips

1. Hover over info icons and buttons to see tooltips appear
2. Test on both light and dark themes
3. Verify positioning doesn't overlap important content
4. On mobile, tooltips show on tap/focus
5. Verify text is readable and not truncated

## Implementation Checklist

When adding tooltips to a new area:

- [ ] Add tooltip content to `src/lib/tooltips.ts`
- [ ] Import `InfoIcon` and/or `Tooltip` components
- [ ] Import `TOOLTIPS` from `src/lib/tooltips`
- [ ] Choose appropriate positioning (top/bottom/left/right)
- [ ] Test in both light and dark modes
- [ ] Verify no TypeScript errors
- [ ] Check that tooltips don't obscure important UI elements
