use std::path::PathBuf;

use crate::ts::Lang;
use crate::ts::Target;
use crate::Result;

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
        for (definition, documentation) in matches {
            println!("--- Documentation ---\n{}", documentation);
            println!("--- Definition ---\n{}", definition);
        }
    }
    Ok(())
}

#[test]
fn go() -> Result<()> {
    let targets = vec![
        Target::new_method("Type1", "method1"),
        Target::new_method("Type1", "method2"),
        Target::new_function("staticFunction"),
        Target::new_class("Type1"),
        Target::new_class("Type2"),
        Target::new_class("Type3"),
    ];
    find_targets_for_lang(targets, Lang::go())
}
