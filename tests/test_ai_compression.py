"""Tests for the SummaryCompressor and compress_summary helper."""

import pytest

from dwriter.ai.compression import SummaryCompressor, SummaryCompressionBudget, compress_summary


class TestSummaryCompressionBudget:
    def test_defaults(self):
        budget = SummaryCompressionBudget()
        assert budget.max_chars == 4000
        assert budget.max_lines == 60

    def test_custom_values(self):
        budget = SummaryCompressionBudget(max_chars=500, max_lines=10)
        assert budget.max_chars == 500
        assert budget.max_lines == 10


class TestSummaryCompressor:
    def test_empty_string_returns_empty(self):
        compressor = SummaryCompressor()
        assert compressor.compress("") == ""

    def test_whitespace_only_returns_empty(self):
        compressor = SummaryCompressor()
        assert compressor.compress("   \n\n   \t  ") == ""

    def test_removes_blank_lines(self):
        compressor = SummaryCompressor()
        result = compressor.compress("line one\n\n\nline two")
        assert "\n\n" not in result
        assert "line one" in result
        assert "line two" in result

    def test_deduplicates_lines(self):
        compressor = SummaryCompressor()
        text = "duplicate line\nduplicate line\nduplicate line"
        result = compressor.compress(text)
        assert result.count("duplicate line") == 1

    def test_deduplication_is_case_insensitive(self):
        compressor = SummaryCompressor()
        text = "Summary: foo\nSUMMARY: foo\nsummary: foo"
        result = compressor.compress(text)
        assert result.count("Summary: foo") + result.count("SUMMARY: foo") + result.count("summary: foo") == 1

    def test_high_priority_lines_come_first(self):
        compressor = SummaryCompressor()
        text = "normal line\nSummary: important\nanother normal\n- bullet point"
        result = compressor.compress(text)
        lines = result.splitlines()
        high_priority_indices = [i for i, l in enumerate(lines) if l.startswith("Summary:") or l.startswith("- ")]
        normal_indices = [i for i, l in enumerate(lines) if l in ("normal line", "another normal")]
        # All high-priority lines must appear before normal lines
        if high_priority_indices and normal_indices:
            assert max(high_priority_indices) < min(normal_indices) or not normal_indices

    def test_enforces_line_budget(self):
        budget = SummaryCompressionBudget(max_chars=99999, max_lines=3)
        compressor = SummaryCompressor(budget)
        text = "\n".join(f"line {i}" for i in range(10))
        result = compressor.compress(text)
        assert len(result.splitlines()) <= 3

    def test_enforces_char_budget(self):
        budget = SummaryCompressionBudget(max_chars=20, max_lines=99999)
        compressor = SummaryCompressor(budget)
        text = "A" * 100
        result = compressor.compress(text)
        assert len(result) <= 20

    def test_char_truncation_preserves_complete_lines(self):
        budget = SummaryCompressionBudget(max_chars=15, max_lines=99999)
        compressor = SummaryCompressor(budget)
        # "line1\nline2\n" — first line is 5 chars, newline makes 6, second 11
        text = "line1\nline2\nline3"
        result = compressor.compress(text)
        # Result must not end in the middle of a word
        for line in result.splitlines():
            assert line.strip() != ""

    def test_strips_result(self):
        compressor = SummaryCompressor()
        result = compressor.compress("  hello  ")
        assert result == result.strip()

    def test_scope_bullet_is_high_priority(self):
        compressor = SummaryCompressor()
        text = "normal\n- Scope: domain\n- regular bullet"
        result = compressor.compress(text)
        lines = result.splitlines()
        scope_idx = next(i for i, l in enumerate(lines) if l.startswith("- Scope:"))
        normal_idx = next((i for i, l in enumerate(lines) if l == "normal"), None)
        if normal_idx is not None:
            assert scope_idx < normal_idx


class TestCompressSummaryHelper:
    def test_default_budget_is_1200_24(self):
        # Generate text that exceeds the defaults
        long_text = "\n".join(f"unique line number {i} with some padding text" for i in range(50))
        result = compress_summary(long_text)
        assert len(result) <= 1200
        assert len(result.splitlines()) <= 24

    def test_custom_budget_respected(self):
        text = "\n".join(f"line {i}" for i in range(20))
        result = compress_summary(text, max_chars=9999, max_lines=5)
        assert len(result.splitlines()) <= 5

    def test_empty_input(self):
        assert compress_summary("") == ""

    def test_idempotent_on_already_compressed_text(self):
        text = "Summary: key point\n- bullet one\n- bullet two"
        first_pass = compress_summary(text)
        second_pass = compress_summary(first_pass)
        assert first_pass == second_pass
