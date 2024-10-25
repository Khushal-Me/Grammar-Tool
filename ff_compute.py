"""
Context-Free Grammar Analyzer
----------------------------
Author: Khushal Mehta
"""

import sys
from collections import defaultdict
from typing import Dict, Set, List, Optional

class CFGAnalyzer:
    """
    Analyzes context-free grammars by computing FIRST and FOLLOW sets for all symbols.
    Implements standard algorithms from compiler construction theory.
    """
    
    def __init__(self):
        # Symbol sets
        self.first_sets: Dict[str, Set[str]] = defaultdict(set)
        self.follow_sets: Dict[str, Set[str]] = defaultdict(set)
        self.productions: Dict[str, List[List[str]]] = defaultdict(list)
        
        # Grammar symbol categories
        self.nonterminals: Set[str] = set()
        self.terminals: Set[str] = set()
        
        # Special symbols
        self.EPSILON = ''
        self.EOF_MARKER = '$$'
        self.AUGMENTED_START = "S'"

    def load_grammar(self, grammar_path: str) -> None:
        """
        Loads and parses a grammar file, building internal representation.
        
        Args:
            grammar_path: Path to the grammar file containing production rules
            
        Format:
            - Each line should be in the form: A -> BC or A -> a
            - Uppercase letters represent nonterminals
            - Lowercase letters represent terminals
            - Empty right-hand side represents epsilon production
        """
        # Add augmented start production
        self._add_production(self.AUGMENTED_START, ["S", self.EOF_MARKER])
        self.nonterminals.add(self.AUGMENTED_START)
        
        try:
            with open(grammar_path) as file:
                for line in file:
                    if not (line := line.strip()):
                        continue
                    
                    # Parse production rule
                    lhs, rhs = map(str.strip, line.split("->"))
                    self._process_production(lhs, rhs)
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"Grammar file not found: {grammar_path}")
        except Exception as e:
            raise ValueError(f"Error parsing grammar file: {str(e)}")

    def _process_production(self, lhs: str, rhs: str) -> None:
        """
        Processes a single production rule, categorizing symbols and storing the rule.
        
        Args:
            lhs: Left-hand side nonterminal
            rhs: Right-hand side of the production (may be empty for epsilon)
        """
        if not rhs:  # Epsilon production
            self._add_production(lhs, [])
        else:
            symbols = []
            for symbol in rhs:
                if symbol.isupper():
                    self.nonterminals.add(symbol)
                    symbols.append(symbol)
                elif symbol.islower():
                    self.terminals.add(symbol)
                    symbols.append(symbol)
            
            self._add_production(lhs, symbols)
        
        self.nonterminals.add(lhs)

    def _add_production(self, lhs: str, rhs: List[str]) -> None:
        """
        Adds a production rule to the grammar.
        
        Args:
            lhs: Left-hand side nonterminal
            rhs: List of symbols in the right-hand side
        """
        self.productions[lhs].append(rhs)

    def compute_first_sets(self) -> None:
        """
        Computes FIRST sets for all grammar symbols using iterative algorithm.
        FIRST(X) contains all terminals that can begin strings derived from X.
        """
        changed = True
        while changed:
            changed = False
            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    original_size = len(self.first_sets[nonterminal])
                    
                    if not production:  # Epsilon production
                        self.first_sets[nonterminal].add(self.EPSILON)
                    else:
                        self._compute_production_first(nonterminal, production)
                    
                    if len(self.first_sets[nonterminal]) > original_size:
                        changed = True
        
        # Add EOF marker to augmented start symbol's FIRST set
        self.first_sets[self.AUGMENTED_START].add(self.EOF_MARKER)

    def _compute_production_first(self, nonterminal: str, production: List[str]) -> None:
        """
        Computes FIRST set contribution from a single production.
        
        Args:
            nonterminal: The nonterminal whose FIRST set is being computed
            production: List of symbols in the production's right-hand side
        """
        for symbol in production:
            if symbol in self.terminals:
                self.first_sets[nonterminal].add(symbol)
                break
            else:  # Nonterminal
                # Add all non-epsilon symbols from FIRST(symbol)
                self.first_sets[nonterminal].update(
                    self.first_sets[symbol] - {self.EPSILON}
                )
                if self.EPSILON not in self.first_sets[symbol]:
                    break
        else:  # All symbols can derive epsilon
            self.first_sets[nonterminal].add(self.EPSILON)

    def compute_follow_sets(self) -> None:
        """
        Computes FOLLOW sets for all nonterminals using iterative algorithm.
        FOLLOW(A) contains all terminals that can appear immediately after A.
        """
        # Initialize FOLLOW set of augmented start symbol with EOF marker
        self.follow_sets[self.AUGMENTED_START].add(self.EOF_MARKER)
        
        changed = True
        while changed:
            changed = False
            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    trailing = self.follow_sets[nonterminal].copy()
                    
                    # Process symbols from right to left
                    for symbol in reversed(production):
                        if symbol in self.nonterminals:
                            original_size = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(trailing)
                            
                            # Update trailing set for next symbol
                            if self.EPSILON in self.first_sets[symbol]:
                                trailing.update(self.first_sets[symbol] - {self.EPSILON})
                            else:
                                trailing = self.first_sets[symbol].copy()
                            
                            if len(self.follow_sets[symbol]) > original_size:
                                changed = True
                        else:  # Terminal
                            trailing = {symbol}
        
        # Clean up augmented start symbol's FOLLOW set
        self.follow_sets[self.AUGMENTED_START].clear()

    def write_analysis(self, output_path: str) -> None:
        """
        Writes computed FIRST and FOLLOW sets to output file.
        
        Args:
            output_path: Path to write the analysis results
        """
        def sort_with_eof_last(symbols: Set[str]) -> List[str]:
            """Helper to sort symbols with EOF marker at the end"""
            return sorted(
                [sym for sym in symbols if sym != self.EPSILON],
                key=lambda x: ('~', x) if x == self.EOF_MARKER else ('', x)
            )
        
        try:
            with open(output_path, 'w') as file:
                # Order nonterminals with augmented start first
                sorted_nonterminals = sorted(self.nonterminals - {self.AUGMENTED_START})
                sorted_nonterminals.insert(0, self.AUGMENTED_START)
                
                for nonterminal in sorted_nonterminals:
                    file.write(f"{nonterminal}\n")
                    
                    # Write FIRST set
                    first_symbols = sort_with_eof_last(self.first_sets[nonterminal])
                    file.write(f"{', '.join(first_symbols)}\n" if first_symbols else "\n")
                    
                    # Write FOLLOW set
                    follow_symbols = sort_with_eof_last(self.follow_sets[nonterminal])
                    file.write(f"{', '.join(follow_symbols)}\n" if follow_symbols else "\n")
                    
        except Exception as e:
            raise IOError(f"Error writing analysis to file: {str(e)}")

def main() -> None:
    """
    Main entry point for the grammar analyzer.
    
    Usage:
        python script.py <grammar_file> <output_file>
    """
    if len(sys.argv) != 3:
        print("Usage: python script.py <grammar_file> <output_file>")
        sys.exit(1)
    
    grammar_file, output_file = sys.argv[1:3]
    
    try:
        analyzer = CFGAnalyzer()
        analyzer.load_grammar(grammar_file)
        analyzer.compute_first_sets()
        analyzer.compute_follow_sets()
        analyzer.write_analysis(output_file)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()