use std::collections::HashMap;

pub const GO_METHODS: &[&str] = &[
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
pub const GO_FUNCTIONS: &[&str] = &[r#"
(
  (function_item
    name: (identifier) @func_name
    body: (_) @body)
  (#eq? @func_name "{function}")
)
"#];

pub fn go() -> HashMap<String, Vec<String>> {
    let mut queries = HashMap::new();
    queries.insert("methods".to_string(), GO_METHODS.iter().map(|s| s.to_string()).collect());
    queries.insert("functions".to_string(), GO_FUNCTIONS.iter().map(|s| s.to_string()).collect());
    queries
}
