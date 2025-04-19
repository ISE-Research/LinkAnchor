use std::path::PathBuf;

use super::Lang;
use super::Result;
use super::Target;

fn find_targets_for_lang(targets: Vec<Target>, lang: Lang) -> Result<()> {
    let file_path = format!("./src/ts/test/samples/code.{}", lang.file_extension);
    let file_path = PathBuf::from(file_path);

    println!("Searching in codebase: {:?}", &file_path);

    for target in targets {
        println!("Target: {target}");
        let matches = lang.find_in(&target, &file_path)?;
        println!("Match found for: {target}");
        println!("Found {} in file: {file_path:?}", matches.len());
        assert!(!matches.is_empty());
        for (definition, documentation) in &matches {
            println!("--- Documentation ---\n{}", documentation);
            println!("--- Definition ---\n{}", definition);
        }

        matches.iter().all(|(def, _doc)| !def.is_empty());
        matches.iter().all(|(_def, doc)| !doc.is_empty());
    }
    Ok(())
}

#[test]
fn go() -> Result<()> {
    let targets = vec![
        Target::new_class("Struct1"),
        Target::new_method("Struct1", "method1"),
        Target::new_method("Struct1", "method2"),
        Target::new_class("Alias1"),
        Target::new_class("Interface1"),
        Target::new_function("staticFunction"),
    ];
    find_targets_for_lang(targets, Lang::go())
}

#[test]
fn python() -> Result<()> {
    let targets = vec![
        Target::new_class("Type1"),
        Target::new_method("Type1", "method1"),
        Target::new_method("Type1", "__init__"),
        Target::new_class("Type2"),
        Target::new_class("Enum1"),
        Target::new_function("static_function"),
    ];
    find_targets_for_lang(targets, Lang::python())
}

#[test]
fn java() -> Result<()> {
    let targets = vec![
        Target::new_class("Class1"),
        Target::new_method("Class1", "method1"),
        Target::new_method("Class1", "Class1"),
        Target::new_method("Class1", "static1"),
        Target::new_class("Class2"),
        Target::new_method("Class2", "interfaceMethod1"),
        Target::new_class("Interface1"),
        Target::new_method("Interface1", "interfaceMethod1"),
        Target::new_class("Enum1"),
    ];
    find_targets_for_lang(targets, Lang::java())
}
