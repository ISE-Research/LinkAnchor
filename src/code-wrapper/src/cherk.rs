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
    separator: String,
    queries: HashMap<String, Vec<String>>,
    language_fn: tree_sitter::Language,
    file_extension: String,
}
impl Lang {
    fn go() -> Self {
        Self {
            separator: ".".to_string(),
            queries: query::go(),
            language_fn: tree_sitter_go::LANGUAGE.into(),
            file_extension: "go".to_string(),
        }
    }
    fn rust() -> Self {
        unimplemented!("Rust support is not implemented yet.");
    }
}

struct Target {
    function_name: Option<String>,
    type_name: Option<String>,
}

impl Lang {
    fn vars(&self) -> HashMap<String, String> {
        let mut vars = HashMap::new();
        vars.insert(String::from("function"), self.function_name.clone());
        vars.insert(
            String::from("receiver"),
            self.type_name.clone().unwrap_or_default(),
        );
        vars
    }
    fn is_typed(&self) -> bool {
        self.type_name.is_some()
    }
    fn find_in(file: &Path, target: Target) -> (String, String) {
        let mut parser = Parser::new();

        parser
            .set_language(&tree_sitter_go::LANGUAGE.into())
            .expect("Error loading Go grammar");
        // For Go, we differentiate between methods and functions.

        let qs = self.lang.queries[if self.is_typed() {
            "methods"
        } else {
            "functions"
        }]
        .iter()
        .filter_map(|q_fstr| strfmt(q_fstr, &self.vars()).ok())
        .collect::<Vec<_>>();

        let source = fs::read_to_string(file_path).ok()?;
        let tree = parser.parse(&source, None)?;
        for q in qs {
            let query = Query::new(&self.lang.language_fn, &q).expect("Error creating query");
            let mut query_cursor = QueryCursor::new();
            let mut matches = query_cursor.matches(&query, tree.root_node(), source.as_bytes());

            // For simplicity, return the first match we find.
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

                        return Some((definition, documentation.into()));
                    }
                }
            }
        }
        None
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

/// Create a tree-sitter parser and query for the target function/method,
/// then search the file for matching nodes.
impl ParsedPath {}

fn main() {
    let codebase_dir = "/home/ark/Documents/Code/University/BGSU/git-anchor/src/gotest";

    println!("Searching in codebase: {}", codebase_dir);

    let queries = vec![
        //"Mamad.SayHello",
        "Mamad.SayHello()",
        //"Mamad.SayGoodBye()",
        //"Mamad.SayGoodBye",
    ];
    for query in queries {
        let full_method_path = query;
        let language = infer_language(full_method_path);
        let parsed_path = parse_full_path(full_method_path, language.clone());
        println!("Parsed path: {:?}", parsed_path);
        // Walk the directory recursively.
        for entry in WalkDir::new(codebase_dir) {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.is_file() {
                // Filter files by extension based on language.
                let ext = path.extension().and_then(|s| s.to_str()).unwrap_or("");
                if ext == language.file_extension {
                    if let Some((definition, documentation)) = parsed_path.find_in(path) {
                        println!("Matching definition found for: {}", full_method_path);
                        println!("Found in file: {:?}", path);
                        println!("--- Definition ---\n{}", definition);
                        println!("--- Documentation ---\n{}", documentation);
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod test {
    #[test]
    fn main() {
        super::main();
    }
}
