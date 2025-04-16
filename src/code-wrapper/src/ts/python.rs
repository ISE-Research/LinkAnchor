use std::collections::HashMap;

use super::QueryMode;

const METHODS: &[&str] = &[r#"
(
 ( class_definition
  name: (identifier) @receiver_type
    body: (block
      (function_definition
        name: (identifier) @function_name
        ) @capture
      )
  )
  (#eq? @receiver_type "{receiver}")
  (#eq? @function_name "{function}")
 ) 
"#];
const FUNCTIONS: &[&str] = &[r#"
(
 (function_definition
    name: (identifier) @function_name
   )
  (#eq? @function_name "{function}")
 ) @capture
"#];

const TYPES: &[&str] = &[
    // class
    // class with inheritance
    // enums
    r#"
(
 ( class_definition
  name: (identifier) @receiver_type
  )
  (#eq? @receiver_type "{receiver}")
 ) @capture
"#,
];

pub fn queries() -> HashMap<QueryMode, Vec<String>> {
    let mut queries = HashMap::new();
    queries.insert(
        QueryMode::Methods,
        METHODS.iter().map(|s| s.to_string()).collect(),
    );
    queries.insert(
        QueryMode::Functions,
        FUNCTIONS.iter().map(|s| s.to_string()).collect(),
    );
    queries.insert(
        QueryMode::Types,
        TYPES.iter().map(|s| s.to_string()).collect(),
    );
    queries
}
