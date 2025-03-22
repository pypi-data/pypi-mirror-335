use std::env;
use std::path::PathBuf;

fn main() {
    // Set build time environment variable
    println!(
        "cargo:rustc-env=CARGO_BUILD_TIME={}",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs()
    );

    // Use pkg-config to find the speexdsp library
    let speexdsp = pkg_config::probe_library("speexdsp").unwrap();

    // Print cargo linking directives
    println!("cargo:rustc-link-lib=speexdsp");

    // If you installed with brew, you might need to specify the path
    if let Ok(brew_prefix) = std::process::Command::new("brew")
        .args(["--prefix"])
        .output()
    {
        if brew_prefix.status.success() {
            let prefix = String::from_utf8_lossy(&brew_prefix.stdout)
                .trim()
                .to_string();
            let lib_path = PathBuf::from(&prefix).join("lib");
            println!("cargo:rustc-link-search={}", lib_path.display());
        }
    }

    // Generate bindings
    let bindings = bindgen::Builder::default()
        .header_contents(
            "wrapper.h",
            "#include <speex/speex_preprocess.h>\n#include <speex/speex_echo.h>",
        )
        .clang_args(
            speexdsp
                .include_paths
                .iter()
                .map(|path| format!("-I{}", path.display())),
        )
        .generate()
        .expect("Unable to generate bindings");

    // Write the bindings to the $OUT_DIR/bindings.rs file
    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .expect("Couldn't write bindings!");

    // Ensure rerun if build script changes
    println!("cargo:rerun-if-changed=build.rs");
}
