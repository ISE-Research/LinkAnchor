mod go;
mod python;
#[cfg(test)]
mod test;

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
const CAPTURE_KEY: &str = "capture";

#[derive(Debug, Clone)]
pub struct Lang {
    queries: HashMap<QueryMode, Vec<String>>,
    language_fn: tree_sitter::Language,
    file_extension: &'static str,
}
impl Lang {
    // Creates new instance for Go Language
    pub fn go() -> Self {
        Self {
            queries: go::queries(),
            language_fn: tree_sitter_go::LANGUAGE.into(),
            file_extension: "go",
        }
    }

    // Creates new instance for python Language
    pub fn python() -> Self {
        Self {
            queries: python::queries(),
            language_fn: tree_sitter_python::LANGUAGE.into(),
            file_extension: "py",
        }
    }
}

impl Lang {
    // finds the definition and deocumentation of the target in the given file_path
    pub fn find_in(&self, target: &Target, file_path: &Path) -> Result<Vec<(String, String)>> {
        let mut parser = Parser::new();
        parser
            .set_language(&self.language_fn)
            .expect("Error loading language grammar");

        // format the queries with values from the target
        let queries = self.queries[&target.query_mode()]
            .iter()
            .filter_map(|q_fstr| target.update_query(q_fstr).ok())
            .collect::<Vec<_>>();

        let source = fs::read_to_string(file_path)?;
        let tree = parser.parse(&source, None).ok_or(CodeError::TSParseError)?;

        let mut results = Vec::new();
        for q in queries {
            let query = Query::new(&self.language_fn, &q).expect("Error creating query");
            let mut query_cursor = QueryCursor::new();
            let mut matches = query_cursor.matches(&query, tree.root_node(), source.as_bytes());
            while let Some(m) = matches.next() {
                for capture in m.captures {
                    // the match we are looking for is tagged with the CAPTURE_KEY
                    if query.capture_names()[capture.index as usize] == CAPTURE_KEY {
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

    // checks if the file format is supported by the language
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
    // creates a new Target for describing a method function in class
    pub fn new_method<S: Into<String>>(type_name: S, function_name: S) -> Self {
        Self {
            function_name: Some(function_name.into()),
            type_name: Some(type_name.into()),
        }
    }

    // creates a new Target for describing a function
    pub fn new_function<S: Into<String>>(function_name: S) -> Self {
        Self {
            function_name: Some(function_name.into()),
            type_name: None,
        }
    }

    // creates a new Target for describing a class
    pub fn new_class<S: Into<String>>(type_name: S) -> Self {
        Self {
            function_name: None,
            type_name: Some(type_name.into()),
        }
    }

    // returns the key-value pairs generated from the target.
    // this is used to format the queries
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
    // formats the query with the values from the target
    fn update_query(&self, query: &str) -> Result<String> {
        strfmt(query, &self.vars()).map_err(CodeError::from)
    }

    // checks if the `type_name` is present
    fn is_typed(&self) -> bool {
        self.type_name.is_some()
    }

    // returns the query mode based on the presence of `type_name` and `function_name`
    // type.function() => Methods
    // type => Types
    // function() => Functions
    fn query_mode(&self) -> QueryMode {
        match self.is_typed() {
            true => match self.function_name.is_some() {
                true => QueryMode::Methods,
                false => QueryMode::Types,
            },
            false => match self.function_name.is_some() {
                true => QueryMode::Functions,
                false => unreachable!(),
            },
        }
    }

    // converts a string of format `type.function()`, `function()`, or `type` to a Target
    pub fn parse(full_path: &str) -> Result<Self> {
        let is_function = full_path.ends_with("()");
        let full_path = full_path.trim();
        let full_path = full_path.trim_end_matches("()");

        let parts: Vec<&str> = full_path.split(".").collect();
        let (type_name, function_name) = match parts.len() {
            0 => return Err(CodeError::TargetCanNotBeEmpty),
            1 => {
                if is_function {
                    (None, Some(parts[0].to_string()))
                } else {
                    (Some(parts[0].to_string()), None)
                }
            }
            n => (
                Some(parts[n - 2].to_string()),
                Some(parts[n - 1].to_string()),
            ), // last two parts are function and type
        };
        Ok(Self {
            function_name,
            type_name,
        })
    }
}

impl Display for Target {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.query_mode() {
            QueryMode::Functions => write!(f, "{}()", self.function_name.as_deref().unwrap_or("")),
            QueryMode::Methods => write!(
                f,
                "{}.{}()",
                self.type_name.as_deref().unwrap_or(""),
                self.function_name.as_deref().unwrap_or("")
            ),
            QueryMode::Types => write!(f, "{}", self.type_name.as_deref().unwrap_or("")),
        }
    }
}

// searches for the previous sibling of the node which has the comment type
fn comment_of(node: tree_sitter::Node) -> Option<tree_sitter::Node> {
    if let Some(prev) = node.prev_sibling() {
        if prev.kind() == "comment" {
            return Some(prev);
        }
    }
    None
}
