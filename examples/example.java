package com.example.text;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Splits strings around matches of a given delimiter, with support
 * for trimming results and omitting empty strings.
 *
 * <p>Example usage:
 * <pre>{@code
 *   List<String> parts = Splitter.on(",")
 *       .trimResults()
 *       .omitEmptyStrings()
 *       .split("foo, bar, , baz");
 *   // returns ["foo", "bar", "baz"]
 * }</pre>
 *
 * @author Example Project Contributors
 * @since 1.0
 */
public final class Splitter {

    private final Pattern delimiter;
    private final boolean trimResults;
    private final boolean omitEmpty;
    private final int limit;

    private Splitter(Pattern delimiter, boolean trim, boolean omitEmpty, int limit) {
        this.delimiter = Objects.requireNonNull(delimiter);
        this.trimResults = trim;
        this.omitEmpty = omitEmpty;
        this.limit = limit;
    }

    /**
     * Returns a splitter that uses the given fixed string as a delimiter.
     *
     * @param separator the literal delimiter string
     * @return a new {@code Splitter} instance
     * @throws IllegalArgumentException if {@code separator} is empty
     */
    public static Splitter on(String separator) {
        if (separator.isEmpty()) {
            throw new IllegalArgumentException("Separator must not be empty");
        }
        return new Splitter(
            Pattern.compile(Pattern.quote(separator)),
            false, false, -1
        );
    }

    @SuppressWarnings("unchecked")
    public static Splitter onPattern(String regex) {
        Pattern pattern = Pattern.compile(regex);
        if (pattern.matcher("").matches()) {
            throw new IllegalArgumentException(
                "Pattern must not match empty string: " + regex
            );
        }
        return new Splitter(pattern, false, false, -1);
    }

    public Splitter trimResults() {
        return new Splitter(delimiter, true, omitEmpty, limit);
    }

    public Splitter omitEmptyStrings() {
        return new Splitter(delimiter, trimResults, true, limit);
    }

    public List<String> split(CharSequence input) {
        String[] raw = delimiter.split(input, limit);
        List<String> result = new ArrayList<>(raw.length);

        for (String part : raw) {
            String value = trimResults ? part.strip() : part;
            if (!omitEmpty || !value.isEmpty()) {
                result.add(value);
            }
        }
        return List.copyOf(result);
    }
}
