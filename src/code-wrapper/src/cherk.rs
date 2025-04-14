use walkdir::WalkDir;

use crate::ts::{Lang, Target};

fn main() {
    let codebase_dir = "/home/ark/Documents/Code/University/BGSU/git-anchor/src/gotest";

    println!("Searching in codebase: {}", codebase_dir);

    let targets = vec![
        Target::new_method("Mamad", "SayHello"),
        Target::new_method("Mamad", "SayGoodBye"),
    ];
    for target in targets {
        let lang = Lang::go();

        println!("Target: {target}");
        // Walk the directory recursively.
        for entry in WalkDir::new(codebase_dir) {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.is_file() {
                // Filter files by extension based on language.
                if lang.accepts(path) {
                    if let Ok(matches) = lang.find_in(&target, path) {
                        println!("Matching definition found for: {target}");
                        println!("Found {} in file: {path:?}", matches.len());
                        for (definition, documentation) in matches {
                            println!("--- Definition ---\n{}", definition);
                            println!("--- Documentation ---\n{}", documentation);
                        }
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
