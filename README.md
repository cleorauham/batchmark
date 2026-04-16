# batchmark

> CLI tool for running and comparing benchmark suites across git branches

---

## Installation

```bash
pip install batchmark
```

Or install from source:

```bash
git clone https://github.com/yourname/batchmark.git && cd batchmark && pip install -e .
```

---

## Usage

Run benchmarks on the current branch and compare against another:

```bash
batchmark run --suite benchmarks/ --compare main
```

Run against multiple branches at once:

```bash
batchmark run --suite benchmarks/ --compare main --compare dev --output results.json
```

View a summary report from a previous run:

```bash
batchmark report results.json
```

**Example output:**

```
Branch       Benchmark         Avg Time    Delta
-----------  ----------------  ----------  -------
main         matrix_multiply   120.4ms     baseline
feature/opt  matrix_multiply   98.1ms      -18.5%
```

---

## Configuration

Optionally add a `batchmark.toml` to your project root to define suite paths, iterations, and warmup runs:

```toml
[batchmark]
suite = "benchmarks/"
iterations = 10
warmup = 2
```

---

## License

MIT © 2024 yourname