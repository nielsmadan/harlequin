package service

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"
)

// ErrInvalidDuration is returned when a duration string cannot be parsed.
var ErrInvalidDuration = errors.New("invalid duration format")

// Uint64Opt represents an optional unsigned 64-bit integer value
// commonly used for resource limits in container configurations.
type Uint64Opt struct {
	value *uint64
}

// Set parses and stores the string as a uint64.
func (o *Uint64Opt) Set(s string) error {
	v, err := strconv.ParseUint(s, 0, 64)
	if err != nil {
		return fmt.Errorf("parsing %q: %w", s, err)
	}
	o.value = &v
	return nil
}

// Value returns the stored value, or 0 if unset.
func (o *Uint64Opt) Value() uint64 {
	if o.value == nil {
		return 0
	}
	return *o.value
}

// String returns the string representation.
func (o *Uint64Opt) String() string {
	if o.value != nil {
		return strconv.FormatUint(*o.value, 10)
	}
	return ""
}

// ParseDuration parses a human-friendly duration string like "3h30m" or "1d12h".
// Extends time.ParseDuration with support for day ("d") units.
func ParseDuration(s string) (time.Duration, error) {
	if s == "" {
		return 0, ErrInvalidDuration
	}

	// Handle day units by converting to hours
	if idx := strings.Index(s, "d"); idx >= 0 {
		days, err := strconv.Atoi(s[:idx])
		if err != nil {
			return 0, fmt.Errorf("%w: %s", ErrInvalidDuration, s)
		}
		remainder := s[idx+1:]
		base := time.Duration(days) * 24 * time.Hour

		if remainder == "" {
			return base, nil
		}
		extra, err := time.ParseDuration(remainder)
		if err != nil {
			return 0, fmt.Errorf("%w: %s", ErrInvalidDuration, s)
		}
		return base + extra, nil
	}

	return time.ParseDuration(s)
}
