# kradle/docs.py
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from kradle.generated.skills import skills_docs
from kradle.generated.world import world_docs
import re
from difflib import get_close_matches


@dataclass
class DocFormat:
    """Configuration for documentation formatting."""

    indent: str = "    "
    show_types: bool = True


class LLMDocsForExecutingCode:
    """Interface for accessing and formatting code documentation."""

    def __init__(self):
        """Initialize with pre-generated documentation."""
        self.docs = {"skills": skills_docs, "world": world_docs}
        self.format = DocFormat()
        self.normalized_names = self._build_normalized_lookup()

    def _build_normalized_lookup(self) -> Dict[str, Tuple[str, str]]:
        """Build lookup dictionary of normalized names to actual function names."""
        lookup = {}
        for module, functions in self.docs.items():
            for func_name in functions:
                normalized = self._normalize_name(func_name)
                lookup[normalized] = (module, func_name)
                lookup[self._normalize_name(f"{module}.{func_name}")] = (
                    module,
                    func_name,
                )
        return lookup

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for matching."""
        return re.sub(r"[^a-zA-Z0-9]", "", name.lower())

    def _find_best_match(
        self, query: str, module: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """Find the best matching function for a query."""
        normalized_query = self._normalize_name(query)

        # Direct match
        if normalized_query in self.normalized_names:
            module_name, func_name = self.normalized_names[normalized_query]
            if module and module != module_name:
                return None
            return (module_name, func_name)

        # Fuzzy match
        potential_matches = []
        for norm_name, (mod_name, func_name) in self.normalized_names.items():
            if module and mod_name != module:
                continue
            if not "." in norm_name:
                potential_matches.append(norm_name)

        close_matches = get_close_matches(
            normalized_query, potential_matches, n=1, cutoff=0.7
        )
        if close_matches:
            return self.normalized_names[close_matches[0]]

        return None

    def get(
        self,
        module: Optional[str] = None,
        skill: Optional[str] = None,
        params: bool = True,
        returns: bool = True,
        examples: bool = True,
    ) -> str:
        """Get formatted documentation."""
        if skill:
            match = self._find_best_match(skill, module)
            if match:
                mod, func = match
                return self._format_function(
                    mod, func, self.docs[mod][func], params, returns, examples
                )
            else:
                suggestions = self.search(skill)
                if suggestions:
                    return (
                        f"Function '{skill}' not found.\n\nDid you mean one of these?\n"
                        + "\n".join(f"  {s}" for s in suggestions[:3])
                    )
                return f"Function '{skill}' not found."

        modules = [module] if module else ["skills", "world"]
        docs = []

        for mod in modules:
            if mod not in self.docs:
                continue

            for func_name, info in sorted(self.docs[mod].items()):
                docs.append(
                    self._format_function(
                        mod, func_name, info, params, returns, examples
                    )
                )
                docs.append("-" * 80)

        return "\n".join(filter(None, docs))

    def _format_function(
        self,
        module: str,
        name: str,
        info: Dict,
        show_params: bool,
        show_returns: bool,
        show_examples: bool,
    ) -> str:
        """Format a single function's documentation."""
        ind = self.format.indent
        lines = []

        # Function name and signature
        param_str = ", ".join(
            f"{p[0]}: {p[1]}" if self.format.show_types else p[0]
            for p in info["params"]
        )

        lines.append(f"FUNCTION: {module}.{name}")
        lines.append(f"{module}.{name}({param_str})")

        # Description
        lines.append("\nDESCRIPTION")
        lines.append(f"{ind}{info['desc']}")

        # Parameters
        if show_params and info["params"]:
            lines.append("\nPARAMETERS")
            for param in info["params"]:
                param_desc = f"{ind}{param[0]} ({param[1]})"
                if param[2]:
                    param_desc += f" - {param[2]}"
                lines.append(param_desc)

        # Returns
        if show_returns and info["returns"]:
            lines.append("\nRETURNS")
            lines.append(f"{ind}{info['returns'][0]} - {info['returns'][1]}")

        # Example
        if show_examples and info["example"]:
            lines.append("\nJAVASCRIPT CODE EXAMPLE")
            lines.append("```")
            lines.append(info["example"])
            lines.append("```")

        return "\n".join(lines)

    def search(self, query: str) -> List[str]:
        """Search for functions containing query in name or description.
        Returns formatted strings with function name and complete description."""
        query = self._normalize_name(query)
        results = []

        for module, functions in self.docs.items():
            for func_name, info in functions.items():
                normalized_name = self._normalize_name(func_name)
                if query in normalized_name or query in self._normalize_name(
                    info["desc"]
                ):
                    results.append(f"{module}.{func_name} - {info['desc']}")

        return sorted(results) if results else []

    def __str__(self) -> str:
        """Return string representation of all documentation."""
        return self.get()

    def __repr__(self) -> str:
        """Return string representation of the class."""
        return f"LLMDocsForExecutingCode(modules=[{', '.join(self.docs.keys())}])"


# Example usage
if __name__ == "__main__":
    docs = LLMDocsForExecutingCode()
    # Get documentation
    print(docs)

    # Get documentation for a specific function
    print(docs.get(skill="smelt"))

    # Search for functions
    print("\nSearch results for 'craft':")
    for result in docs.search("smelt"):
        print(result)
