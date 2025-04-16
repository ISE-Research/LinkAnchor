mod go;
mod python;

use std::collections::HashMap;
use std::fmt::Display;
use std::fs;
use std::path::Path;
use strfmt::strfmt;
use tree_sitter::StreamingIterator;
use tree_sitter::{Parser, Query, QueryCursor};

use crate::CodeError;
use crate::Result;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum QueryMode {
    Functions,
    Methods,
    Types,
}

const FUNCTION_KEY: &str = "function";
const RECEIVER_KEY: &str = "receiver";

#[derive(Debug, Clone)]
pub struct Lang {
    queries: HashMap<QueryMode, Vec<String>>,
    language_fn: tree_sitter::Language,
    file_extension: &'static str,
}
impl Lang {
    pub fn go() -> Self {
        Self {
            queries: go::queries(),
            language_fn: tree_sitter_go::LANGUAGE.into(),
            file_extension: "go",
        }
    }
}

impl Lang {
    pub fn find_in(&self, target: &Target, root_dir: &Path) -> Result<Vec<(String, String)>> {
        let mut parser = Parser::new();

        parser
            .set_language(&self.language_fn)
            .expect("Error loading language grammar");
        let queries = self.queries[&target.query_mode()?]
            .iter()
            .filter_map(|q_fstr| target.update_query(q_fstr).ok())
            .collect::<Vec<_>>();

        let source = fs::read_to_string(root_dir)?;
        let tree = parser.parse(&source, None).ok_or(CodeError::TSParseError)?;
        let mut results = Vec::new();
        for q in queries {
            let query = Query::new(&self.language_fn, &q).expect("Error creating query");
            let mut query_cursor = QueryCursor::new();
            let mut matches = query_cursor.matches(&query, tree.root_node(), source.as_bytes());
            while let Some(m) = matches.next() {
                for capture in m.captures {
                    if query.capture_names()[capture.index as usize] == "capture" {
                        let node = capture.node;
                        let definition = node
                            .utf8_text(source.as_bytes())
                            .unwrap_or_default()
                            .to_owned()
                            .to_string();
                        let documentation = comment_of(node)
                            .map(|n| n.utf8_text(source.as_bytes()).unwrap_or_default())
                            .unwrap_or_default();

                        results.push((definition, documentation.into()))
                    }
                }
            }
        }
        Ok(results)
    }

    pub fn accepts(&self, path: &Path) -> bool {
        path.extension().and_then(|s| s.to_str()) == Some(self.file_extension)
    }
}

#[derive(Debug, Clone)]
pub struct Target {
    function_name: Option<String>,
    type_name: Option<String>,
}

impl Target {
    pub fn new_method<S: Into<String>>(type_name: S, function_name: S) -> Self {
        Self {
            function_name: Some(function_name.into()),
            type_name: Some(type_name.into()),
        }
    }
    pub fn new_function<S: Into<String>>(function_name: S) -> Self {
        Self {
            function_name: Some(function_name.into()),
            type_name: None,
        }
    }
    pub fn new_class<S: Into<String>>(type_name: S) -> Self {
        Self {
            function_name: None,
            type_name: Some(type_name.into()),
        }
    }
    fn vars(&self) -> HashMap<String, String> {
        let mut vars = HashMap::new();
        if let Some(ref name) = self.function_name {
            vars.insert(String::from(FUNCTION_KEY), name.clone());
        }
        if let Some(ref name) = self.type_name {
            vars.insert(String::from(RECEIVER_KEY), name.clone());
        }
        vars
    }
    fn update_query(&self, query: &str) -> Result<String> {
        strfmt(query, &self.vars()).map_err(CodeError::from)
    }

    fn is_typed(&self) -> bool {
        self.type_name.is_some()
    }

    fn query_mode(&self) -> Result<QueryMode> {
        match self.is_typed() {
            true => match self.function_name.is_some() {
                true => Ok(QueryMode::Methods),
                false => Ok(QueryMode::Types),
            },
            false => match self.function_name.is_some() {
                true => Ok(QueryMode::Functions),
                false => Err(CodeError::TargetCanNotBeEmpty),
            },
        }
    }

    pub fn parse(full_path: &str) -> Self {
        let full_path = full_path.trim();
        let full_path = full_path.trim_end_matches("()");

        let mut parts: Vec<&str> = full_path.split(".").collect();
        let function_name = parts.pop().map(|s| s.to_string());
        // Depending on number of parts left, we may have package/module and/or type
        let (_package, type_name) = match parts.len() {
            0 => (None, None),
            1 => (None, Some(parts[0].to_string())), // single type or function in root
            _ => (Some(parts[0].to_string()), Some(parts[1].to_string())),
        };
        Self {
            function_name,
            type_name,
        }
    }
}

impl Display for Target {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}{}{}",
            self.type_name.as_deref().unwrap_or(""),
            if self.is_typed() { "." } else { "" },
            self.function_name.as_deref().unwrap_or(""),
        )
    }
}

fn comment_of(node: tree_sitter::Node) -> Option<tree_sitter::Node> {
    if let Some(prev) = node.prev_sibling() {
        if prev.kind() == "comment" {
            return Some(prev);
        }
    }
    None
}
