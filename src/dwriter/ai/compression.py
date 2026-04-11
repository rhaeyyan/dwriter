from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryCompressionBudget:
    """Defines the limits for deterministic text compression."""

    max_chars: int = 4000
    max_lines: int = 60


class SummaryCompressor:
    """Applies deterministic compression to activity summaries and logs.

    This utility ensures the AI context remains high-signal by removing redundancy
    and prioritizing key structural metadata while staying within strict token/size
    budgets.
    """

    def __init__(self, budget: SummaryCompressionBudget = SummaryCompressionBudget()):
        self.budget = budget

    def compress(self, text: str) -> str:
        """Compresses the input text using normalization and a priority system.

        The compression process follows these steps:
        1. Normalize whitespace and remove empty lines.
        2. Remove duplicate lines (case-insensitive).
        3. Sort lines by priority (headers/scope first).
        4. Enforce character and line count budgets.

        Args:
            text (str): The raw text to compress.

        Returns:
            str: The compressed, high-signal output.
        """
        if not text:
            return ""

        # 1. Normalize whitespace and split into lines
        # Also filters out purely whitespace lines
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # 2. Remove duplicates (case-insensitive) while preserving original case
        seen = set()
        unique_lines = []
        for line in lines:
            normalized = line.lower()
            if normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)

        # 3. Priority system: Re-order based on structural importance
        # High priority: "Summary:", "- Scope:", or "- " (bullet points)
        high_priority = []
        normal_priority = []

        for line in unique_lines:
            if (
                line.startswith("Summary:")
                or line.startswith("- Scope:")
                or line.startswith("- ")
            ):
                high_priority.append(line)
            else:
                normal_priority.append(line)

        # Recombine based on priority (high priority first)
        final_lines = high_priority + normal_priority

        # 4. Enforce Budget: Line Count
        if len(final_lines) > self.budget.max_lines:
            final_lines = final_lines[: self.budget.max_lines]

        # 5. Enforce Budget: Character Count
        # We join back and then truncate if necessary, trying to be surgical
        compressed_text = "\n".join(final_lines)

        if len(compressed_text) > self.budget.max_chars:
            # Slicing at max_chars and trying to find the last complete line
            truncated = compressed_text[: self.budget.max_chars]
            last_newline = truncated.rfind("\n")
            if last_newline != -1:
                compressed_text = truncated[:last_newline]
            else:
                compressed_text = truncated

        return compressed_text.strip()


def compress_summary(text: str, max_chars: int = 1200, max_lines: int = 24) -> str:
    """Helper function to quickly compress text using default or custom budgets.

    Args:
        text (str): The text to compress.
        max_chars (int): Maximum character budget.
        max_lines (int): Maximum line budget.

    Returns:
        str: The compressed text.
    """
    budget = SummaryCompressionBudget(max_chars=max_chars, max_lines=max_lines)
    compressor = SummaryCompressor(budget)
    return compressor.compress(text)
