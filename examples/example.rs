use std::collections::HashMap;
use std::fmt;
use std::io;

const MAX_PATTERN_LEN: usize = 4096;

/// Errors that can occur during pattern matching.
#[derive(Debug, Clone)]
pub enum MatchError {
    InvalidPattern(String),
    InputTooLarge { size: usize, limit: usize },
    IoError(String),
}

impl fmt::Display for MatchError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MatchError::InvalidPattern(msg) => write!(f, "invalid pattern: {}", msg),
            MatchError::InputTooLarge { size, limit } => {
                write!(f, "input size {} exceeds limit {}", size, limit)
            }
            MatchError::IoError(msg) => write!(f, "I/O error: {}", msg),
        }
    }
}

impl From<io::Error> for MatchError {
    fn from(err: io::Error) -> Self {
        MatchError::IoError(err.to_string())
    }
}

/// A compiled search pattern with optional case sensitivity.
#[derive(Debug)]
pub struct Pattern {
    raw: String,
    case_sensitive: bool,
    literal_count: usize,
}

impl Pattern {
    pub fn new(raw: &str, case_sensitive: bool) -> Result<Self, MatchError> {
        if raw.is_empty() {
            return Err(MatchError::InvalidPattern("empty pattern".into()));
        }
        if raw.len() > MAX_PATTERN_LEN {
            return Err(MatchError::InputTooLarge {
                size: raw.len(),
                limit: MAX_PATTERN_LEN,
            });
        }

        let literal_count = raw.chars().filter(|c| c.is_alphanumeric()).count();

        Ok(Pattern {
            raw: raw.to_string(),
            case_sensitive,
            literal_count,
        })
    }

    /// Returns all byte offsets where the pattern matches in the given text.
    pub fn find_matches<'a>(&self, text: &'a str) -> Vec<(usize, &'a str)> {
        let mut results = Vec::new();
        let (haystack, needle);

        if self.case_sensitive {
            haystack = text.to_string();
            needle = self.raw.clone();
        } else {
            haystack = text.to_lowercase();
            needle = self.raw.to_lowercase();
        }

        for (idx, _) in haystack.match_indices(&needle) {
            let end = idx + self.raw.len();
            results.push((idx, &text[idx..end]));
        }

        results
    }
}
