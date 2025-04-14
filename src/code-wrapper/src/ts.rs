use std::collections::HashMap;
use std::fmt::Display;
use std::fs;
use std::path::Path;
use strfmt::strfmt;
use tree_sitter::StreamingIterator;
use tree_sitter::{Parser, Query, QueryCursor};

use crate::query;
use crate::CodeError;
use crate::Result;

#[derive(Debug, Clone)]
pub struct Lang {
    separator: &'static str,
    queries: HashMap<String, Vec<String>>,
    language_fn: tree_sitter::Language,
    file_extension: &'static str,
}
impl Lang {
    pub fn go() -> Self {
        Self {
            separator: ".",
            queries: query::go(),
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
        let queries = self.queries[target.query_mode()?]
            .iter()
            .filter_map(|q_fstr| target.update_query(q_fstr).ok())
            .collect::<Vec<_>>();

        let source = fs::read_to_string(root_dir)?;
        let tree = parser.parse(&source, None).ok_or(CodeError::TSParseError)?;
        let mut results = Vec::new();
        for q in queries {
            dbg!(&q);
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
        path.extension()
            .and_then(|s| s.to_str())
            .map_or(false, |ext| ext == self.file_extension)
    }
}

#[derive(Debug, Clone)]
pub struct Target {
    function_name: Option<String>,
    type_name: Option<String>,
}

impl Target {
    pub fn new_method<S: Into<String>>(type_name: S,function_name: S ) -> Self {
        Self {
            function_name: Some(function_name.into()),
            type_name: Some(type_name.into()),
        }
    }
    fn vars(&self) -> HashMap<String, String> {
        let mut vars = HashMap::new();
        if let Some(ref name) = self.function_name {
            vars.insert(String::from("function"), name.clone());
        }
        if let Some(ref name) = self.type_name {
            vars.insert(String::from("receiver"), name.clone());
        }
        dbg!(vars)
    }
    fn update_query(&self, query: &str) -> Result<String> {
        let x = strfmt(query, &self.vars()).map_err(CodeError::from);
        dbg!(x)
    }

    fn is_typed(&self) -> bool {
        self.type_name.is_some()
    }

    fn query_mode(&self) -> Result<&'static str> {
        match self.is_typed() {
            true => match self.function_name.is_some() {
                true => Ok("methods"),
                false => Ok("types"),
            },
            false => match self.function_name.is_some() {
                true => Ok("functions"),
                false => Err(CodeError::TargetCanNotBeEmpty),
            },
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
