import type { ZodError } from "zod";

/** Map of field names to their first validation error message. */
export type FieldErrors = Record<string, string>;

/** Convert a ZodError into a flat map of field → first error message. */
export function fieldErrors(error: ZodError): FieldErrors {
    const result: FieldErrors = {};
    for (const issue of error.issues) {
        const key = issue.path.join(".");
        if (key && !(key in result)) {
            result[key] = issue.message;
        }
    }
    return result;
}
