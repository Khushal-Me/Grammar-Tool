# Grammar Analyzer (FIRST and FOLLOW Sets Calculator)

A Python tool for analyzing context-free grammars (CFGs) and computing FIRST and FOLLOW sets. This tool is particularly useful for compiler construction and parsing theory applications.

## Features

- Computes FIRST and FOLLOW sets for context-free grammars
- Validates grammar structure and reports common errors
- Handles epsilon productions
- Detects unreachable nonterminals
- Provides detailed error reporting and logging
- Supports augmented grammar notation (S' -> S$$)

## Requirements

- Python 3.8 or higher
- No external dependencies required

## Installation

Clone this repository:
```bash
git clone https://github.com/Khushal-Me/grammar-analyzer.git
cd grammar-analyzer
```

## Usage

### Command Line Interface

Run the analyzer with:
```bash
python ff_compute.py <input_grammar_file> <output_file>
```

Example:
```bash
python ff_compute.py grammar.txt output.txt
```

### Grammar File Format

The input grammar file should follow these conventions:

1. One production rule per line
2. Use "->" to separate left and right-hand sides
3. Uppercase letters for nonterminals
4. Lowercase letters for terminals
5. Empty right-hand side for epsilon productions

Example grammar file:
```
S -> AB
A -> aA
A -> b
B -> c
B ->
```

### Output Format

The output file contains three lines for each nonterminal:
1. The nonterminal symbol
2. Comma-separated FIRST set
3. Comma-separated FOLLOW set

Example output:
```
S'
$$


S
a, b
$$

A
a, b
c

B
c
$$
```

### Using as a Library

You can also use the Grammar Analyzer as a library in your Python code:

```python
from grammar_analyzer import GrammarAnalyzer

# Initialize the analyzer (optional debug mode)
analyzer = GrammarAnalyzer(debug_mode=True)

# Parse and analyze the grammar
analyzer.parse_grammar_file("path/to/grammar.txt")

# Validate the grammar
analyzer.validate_grammar()

# Compute FIRST and FOLLOW sets
results = analyzer.analyze_grammar()

# Access the results
first_sets = results['FIRST']
follow_sets = results['FOLLOW']

# Write results to file
analyzer.write_results("output.txt")
```

## Error Handling

The tool provides comprehensive error checking and will report:
- Invalid grammar file format
- Undefined nonterminals
- Unreachable nonterminals
- Missing start symbol
- Invalid symbols in productions
- File I/O errors

Example error messages:
```
ERROR: Undefined nonterminal 'C' used in production
WARNING: Unreachable nonterminals found: {'D'}
ERROR: Invalid symbol '#' at line 5
```

## Technical Details

### Grammar Rules

1. Nonterminals must be uppercase letters (A-Z)
2. Terminals must be lowercase letters (a-z)
3. The start symbol must be 'S'
4. Empty productions represent epsilon (ε)
5. The tool automatically adds the augmented start production S' -> S$$

### FIRST Set Computation

The FIRST set of a symbol X is the set of terminals that can appear as the first symbol of any string derived from X. For a nonterminal A:
- If A -> a... is a production, then a is in FIRST(A)
- If A -> ε is a production, then ε is in FIRST(A)
- If A -> B... is a production, then FIRST(B) - {ε} is in FIRST(A)

### FOLLOW Set Computation

The FOLLOW set of a nonterminal A is the set of terminals that can appear immediately after A in any sentential form. For a nonterminal A:
- If S is the start symbol, then $ is in FOLLOW(S)
- If there is a production B -> αAβ, then FIRST(β) - {ε} is in FOLLOW(A)
- If there is a production B -> αA, or B -> αAβ where FIRST(β) contains ε, then FOLLOW(B) is in FOLLOW(A)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Khushal Mehta** 

## Acknowledgments

- Based on compiler construction theory and formal language concepts by Micheal Sipser
