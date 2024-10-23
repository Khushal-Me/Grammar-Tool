import sys
from collections import defaultdict
from typing import Dict, Set, List

class GrammarAnalyzer:
    """
    A class to analyze context-free grammars and compute FIRST and FOLLOW sets.
    This implementation follows the standard algorithm for computing these sets
    as described in compiler construction theory.
    """
    
    def __init__(self):
        # Core data structures for grammar analysis
        self.first_sets: Dict[str, Set[str]] = defaultdict(set)   # Maps each symbol to its FIRST set
        self.follow_sets: Dict[str, Set[str]] = defaultdict(set)  # Maps each nonterminal to its FOLLOW set
        self.grammar_rules: Dict[str, List[List[str]]] = defaultdict(list)  # Maps nonterminals to their production rules
        
        # Sets to track grammar symbols
        self.nonterminal_symbols: Set[str] = set()  # All nonterminal symbols (uppercase letters)
        self.terminal_symbols: Set[str] = set()     # All terminal symbols (lowercase letters)
        
        # Special symbols
        self.EPSILON = ''           # Represents ε (empty string)
        self.END_MARKER = '$$'      # Represents end of input
        self.START_SYMBOL = "S'"    # Augmented grammar's start symbol

    def parse_grammar_file(self, filepath: str) -> None:
        """
        Reads and parses a grammar file, populating the internal data structures.
        Each line should be in the format: A -> BC or A -> a where:
        - Uppercase letters are nonterminals
        - Lowercase letters are terminals
        - Empty right-hand side represents epsilon production
        
        Args:
            filepath: Path to the grammar file
        """
        # First, add the augmented start production S' -> S$$
        self.grammar_rules[self.START_SYMBOL].append(["S", self.END_MARKER])
        self.nonterminal_symbols.add(self.START_SYMBOL)
        
        with open(filepath) as file:
            for line in file:
                # Skip empty lines
                if not (line := line.strip()):
                    continue
                    
                # Split into left and right sides of the production
                lhs, rhs = map(str.strip, line.split("->"))
                
                # Process the right-hand side of the production
                if not rhs:  # Empty RHS means epsilon production
                    self.grammar_rules[lhs].append([])
                else:
                    # Parse each symbol in the production
                    production_symbols = []
                    for symbol in rhs:
                        if symbol.isupper():  # Nonterminal
                            self.nonterminal_symbols.add(symbol)
                            production_symbols.append(symbol)
                        elif symbol.islower():  # Terminal
                            self.terminal_symbols.add(symbol)
                            production_symbols.append(symbol)
                    
                    self.grammar_rules[lhs].append(production_symbols)
                
                # Add left-hand side to nonterminals
                self.nonterminal_symbols.add(lhs)

    def compute_first_sets(self) -> None:
        """
        Computes FIRST sets for all grammar symbols.
        FIRST(X) is the set of terminals that can begin any string derived from X.
        The algorithm iteratively computes FIRST sets until no changes occur.
        """
        changed = True
        while changed:
            changed = False
            # Process each nonterminal's productions
            for nonterminal in self.nonterminal_symbols:
                for production in self.grammar_rules[nonterminal]:
                    initial_size = len(self.first_sets[nonterminal])
                    
                    if not production:  # Empty production (epsilon)
                        self.first_sets[nonterminal].add(self.EPSILON)
                    else:
                        self._process_production_for_first(nonterminal, production)
                    
                    # Check if the FIRST set grew
                    if len(self.first_sets[nonterminal]) > initial_size:
                        changed = True
        
        # Ensure END_MARKER is in FIRST(S')
        self.first_sets[self.START_SYMBOL].add(self.END_MARKER)

    def _process_production_for_first(self, nonterminal: str, production: List[str]) -> None:
        """
        Helper method to process a single production when computing FIRST sets.
        
        Args:
            nonterminal: The nonterminal whose FIRST set we're computing
            production: List of symbols in the production's right-hand side
        """
        for symbol in production:
            if symbol in self.terminal_symbols:
                self.first_sets[nonterminal].add(symbol)
                break
            else:  # symbol is a nonterminal
                # Add all non-epsilon symbols from FIRST(symbol)
                self.first_sets[nonterminal].update(
                    self.first_sets[symbol] - {self.EPSILON}
                )
                # If symbol cannot derive epsilon, stop here
                if self.EPSILON not in self.first_sets[symbol]:
                    break
        else:  # If we got through all symbols
            # If all symbols can derive epsilon, add epsilon to FIRST set
            self.first_sets[nonterminal].add(self.EPSILON)

    def compute_follow_sets(self) -> None:
        """
        Computes FOLLOW sets for all nonterminals.
        FOLLOW(A) is the set of terminals that can appear immediately after A in a sentential form.
        The algorithm iteratively computes FOLLOW sets until no changes occur.
        """
        # Initialize FOLLOW(S') with END_MARKER
        self.follow_sets[self.START_SYMBOL].add(self.END_MARKER)
        
        changed = True
        while changed:
            changed = False
            for nonterminal in self.nonterminal_symbols:
                for production in self.grammar_rules[nonterminal]:
                    # Start with FOLLOW(nonterminal) as the trailing set
                    trailing_symbols = self.follow_sets[nonterminal].copy()
                    
                    # Process the production from right to left
                    for symbol in reversed(production):
                        if symbol in self.nonterminal_symbols:
                            initial_size = len(self.follow_sets[symbol])
                            
                            # Add trailing symbols to FOLLOW(symbol)
                            self.follow_sets[symbol].update(trailing_symbols)
                            
                            # Update trailing symbols based on FIRST(symbol)
                            if self.EPSILON in self.first_sets[symbol]:
                                trailing_symbols.update(
                                    self.first_sets[symbol] - {self.EPSILON}
                                )
                            else:
                                trailing_symbols = self.first_sets[symbol].copy()
                            
                            if len(self.follow_sets[symbol]) > initial_size:
                                changed = True
                        else:  # symbol is a terminal
                            trailing_symbols = {symbol}
        
        # Clear FOLLOW(S') as per requirements
        self.follow_sets[self.START_SYMBOL].clear()

    def write_results(self, output_filepath: str) -> None:
        """
        Writes the computed FIRST and FOLLOW sets to the output file.
        Format:
        - One nonterminal per group of three lines
        - First line: nonterminal symbol
        - Second line: comma-separated FIRST set
        - Third line: comma-separated FOLLOW set
        
        Args:
            output_filepath: Path to the output file
        """
        def sort_key(item: str) -> tuple:
            """Custom sort key that puts END_MARKER last"""
            return ('~', item) if item == self.END_MARKER else ('', item)
        
        with open(output_filepath, 'w') as file:
            # Process nonterminals in order, with S' first
            sorted_nonterminals = sorted(self.nonterminal_symbols - {self.START_SYMBOL})
            sorted_nonterminals.insert(0, self.START_SYMBOL)
            
            for nonterminal in sorted_nonterminals:
                # Write nonterminal
                file.write(f"{nonterminal}\n")
                
                # Write FIRST set (excluding epsilon)
                first_set = sorted(
                    [sym for sym in self.first_sets[nonterminal] if sym != self.EPSILON],
                    key=sort_key if nonterminal == self.START_SYMBOL else None
                )
                file.write(f"{', '.join(first_set)}\n" if first_set else "\n")
                
                # Write FOLLOW set
                follow_set = sorted(self.follow_sets[nonterminal], key=sort_key)
                file.write(f"{', '.join(follow_set)}\n" if follow_set else "\n")

def main():
    """
    Main entry point of the program.
    Expects two command-line arguments:
    1. Path to input grammar file
    2. Path to output file for FIRST and FOLLOW sets
    """
    if len(sys.argv) != 3:
        print("Usage: python script.py <grammar_file> <output_file>")
        sys.exit(1)
    
    grammar_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Initialize and run the grammar analyzer
    analyzer = GrammarAnalyzer()
    analyzer.parse_grammar_file(grammar_file)
    analyzer.compute_first_sets()
    analyzer.compute_follow_sets()
    analyzer.write_results(output_file)

if __name__ == "__main__":
    main()