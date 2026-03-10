interface RegExpOptions {
    global?: boolean;
    matchCase?: boolean;
    wholeWord?: boolean;
    multiline?: boolean;
    unicode?: boolean;
}

const SPECIAL_CHARS = /[-\/\\^$*+?.()|[\]{}]/g;
const MAX_PATTERN_LENGTH = 10_000;

/**
 * Escapes special regex characters in a string.
 */
function escapeRegExpCharacters(value: string): string {
    return value.replace(SPECIAL_CHARS, "\\$&");
}

/**
 * Creates a RegExp from a search string with configurable options.
 * Throws if the resulting pattern exceeds the maximum allowed length.
 */
export function createRegExp(
    searchString: string,
    isRegex: boolean,
    options: RegExpOptions = {}
): RegExp {
    if (!searchString) {
        throw new Error("Cannot create regex from empty string");
    }
    if (!isRegex) {
        searchString = escapeRegExpCharacters(searchString);
    }
    if (options.wholeWord) {
        if (!/\B/.test(searchString.charAt(0))) {
            searchString = "\\b" + searchString;
        }
        if (!/\B/.test(searchString.charAt(searchString.length - 1))) {
            searchString += "\\b";
        }
    }
    if (searchString.length > MAX_PATTERN_LENGTH) {
        throw new RangeError(
            `Pattern length ${searchString.length} exceeds limit of ${MAX_PATTERN_LENGTH}`
        );
    }

    let modifiers = "";
    if (options.global) modifiers += "g";
    if (!options.matchCase) modifiers += "i";
    if (options.multiline) modifiers += "m";
    if (options.unicode) modifiers += "u";

    return new RegExp(searchString, modifiers);
}

type MatchResult = {
    text: string;
    index: number;
    groups: Record<string, string>;
};

export function findAllMatches(
    pattern: RegExp,
    input: string
): MatchResult[] {
    const results: MatchResult[] = [];
    let match: RegExpExecArray | null;

    const globalPattern = new RegExp(pattern.source, pattern.flags + "g");
    while ((match = globalPattern.exec(input)) !== null) {
        results.push({
            text: match[0],
            index: match.index,
            groups: { ...match.groups },
        });
    }
    return results;
}
