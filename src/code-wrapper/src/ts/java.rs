use std::collections::HashMap;

use super::QueryMode;

const METHODS: &[&str] = &[
    // constructor declarations
    r#"
( 
  (class_declaration
    name: (identifier) @receiver_type
    body: (class_body
            (constructor_declaration
              name: (identifier) @method_name
              )@capture
            )
    )
  (#eq?  @receiver_type "{receiver}")
  (#eq?  @method_name "{function}")
)
"#,
    // method declarations
    // static method declarations
    r#"
( 
  (class_declaration
    name: (identifier) @receiver_type
    body: (class_body
            (method_declaration
              name: (identifier) @method_name
              )@capture
            )
    )
  (#eq?  @receiver_type "{receiver}")
  (#eq?  @method_name "{function}")
)
"#,
    // interface method declarations
    r#"
(
 (interface_declaration
   name: (identifier) @receiver_type
   body: (interface_body
            (method_declaration
              name: (identifier) @method_name
              ) @capture
           )
   )
  (#eq? @receiver_type "{receiver}")
  (#eq? @method_name "{function}")
 )
 "#,
];
// no static method declarations for Java
const FUNCTIONS: &[&str] = &[];

const TYPES: &[&str] = &[
    // class definitions
    r#"
( 
  (class_declaration
    name: (identifier) @receiver_type
    )
  (#eq?  @receiver_type "{receiver}")
)@capture
"#,
    // interface definitions
    r#"
(
 (interface_declaration
   name: (identifier) @receiver_type
   )
  (#eq? @receiver_type "{receiver}")
 ) @capture
"#,
    // enum definitions
    r#"
( 
  (enum_declaration
    name: (identifier) @receiver_type
    )
  (#eq?  @receiver_type "{receiver}")
)@capture
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
