use std::collections::HashMap;
use std::fs;
use std::path::Path;
use strfmt::strfmt;
use tree_sitter::StreamingIterator;
use tree_sitter::{Parser, Query, QueryCursor};
use walkdir::WalkDir;

use crate::query;

#[derive(Debug, Clone)]
struct Lang {
    separator: &'static str,
    queries: HashMap<String, Vec<String>>,
    language_fn: tree_sitter::Language,
    file_extension: &'static str,
}
impl Lang {
    fn go() -> Self {
        Self {
            separator: ".",
            queries: query::go(),
            language_fn: tree_sitter_go::LANGUAGE.into(),
            file_extension: "go",
        }
    }
}
