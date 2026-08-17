/** Extract a readable message from an unknown thrown value, falling back to a default. */
export function errorMessage(err: unknown, fallback: string): string {
    return err instanceof Error ? err.message : fallback;
}
