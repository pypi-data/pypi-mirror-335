# Python Bindings to speexdsp using rust and maturin/pyo3

install: `uv sync`

test: `RUST_BACKTRACE=full uv run examples/basic_async.py` or whatever. This will also build the rust part if anything changed.


## Publish

If not installed, install `cargo install cargo-workspaces`

On **main**, run `cargo ws version patch` / `cargo ws version minor` / `cargo ws version major` etc. based on what to bump
-> this will update the Cargo.toml version, create a new git tag and push. The CI will publish commits with new tags to [pypi](https://pypi.org/project/speex-py/)