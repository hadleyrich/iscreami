/** Format a nullable number as a fixed-decimal string, returning "—" for null/undefined. */
export function fmt(value: number | null | undefined, decimals = 1): string {
    if (value === null || value === undefined) return "—";
    return value.toFixed(decimals);
}

/** Format a nullable kJ/100g energy value as a string with unit, returning "—" for null. */
export function fmtKj(value: number | null | undefined): string {
    if (value === null || value === undefined) return "—";
    return `${Math.round(value)} kJ`;
}
