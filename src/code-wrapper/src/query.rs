use std::collections::HashMap;
const GO_METHODS: &[&str] = &[
    // receiver is a pointer
    // func (*receiver).function()
    r#"
(
  (method_declaration 
    receiver: (parameter_list
      (parameter_declaration
        type: (pointer_type
                (type_identifier) @receiver_type)
        )
        (#eq? @receiver_type "{receiver}")
      )
    name: (field_identifier) @method_name
    body: (block) @body
    )
  (#eq? @method_name "{function}")
) @capture
"#,
    // receiver is a struct
    // func (receiver).function()
    r#"
(
  (method_declaration 
    receiver: (parameter_list
      (parameter_declaration
        type: (type_identifier) @receiver_type
        )
        (#eq? @receiver_type "{receiver}")
      )
    name: (field_identifier) @method_name
    body: (block) @body
    )
  (#eq? @method_name "{function}")
) @capture
"#,
];
const GO_FUNCTIONS: &[&str] = &[r#"
(
  (function_declaration
    name: (identifier) @function_name
    body: (block) @body
    )
  (#eq? @function_name "{function}")
) @capture
"#];

const GO_TYPES: &[&str] = &[
    // struct types
    // interface types
    r#"
(
  (type_declaration
    (type_spec
      name: (type_identifier) @receiver_type
      )
    )
  (#eq?  @receiver_type "{receiver}")
) @capture
"#,
    // alias types
    r#"
(
  (type_declaration
    (type_alias
      name: (type_identifier) @receiver_type
      )
    )
  (#eq?  @receiver_type "{receiver}")
) @capture
"#,
];

pub fn go() -> HashMap<String, Vec<String>> {
    let mut queries = HashMap::new();
    queries.insert(
        "methods".to_string(),
        GO_METHODS.iter().map(|s| s.to_string()).collect(),
    );
    queries.insert(
        "functions".to_string(),
        GO_FUNCTIONS.iter().map(|s| s.to_string()).collect(),
    );
    queries.insert(
        "types".to_string(),
        GO_TYPES.iter().map(|s| s.to_string()).collect(),
    );
    queries
}
