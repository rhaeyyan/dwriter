"""Tests for the AI fact extraction module."""

from unittest.mock import MagicMock, patch
import pytest

from dwriter.ai.fact_extractor import extract_facts, project_extracted_facts
from dwriter.ai.schemas.extraction import ExtractedFact, FactBatch
from dwriter.config import AIConfig
from dwriter.graph.projector import GraphProjector


@pytest.fixture
def mock_config() -> AIConfig:
    config = AIConfig()
    return config


@pytest.fixture
def mock_entry() -> MagicMock:
    entry = MagicMock()
    entry.uuid = "entry-1"
    entry.content = "I always prefer Python for backend services."
    return entry


@patch("dwriter.ai.engine.get_ai_client")
def test_extract_facts_returns_facts(mock_get_client, mock_config, mock_entry):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_batch = FactBatch(facts=[
        ExtractedFact(text="Prefers Python for backend", category="preference")
    ])
    
    mock_client.chat.completions.create.return_value = mock_batch
    
    facts = extract_facts([mock_entry], mock_config)
    assert len(facts) == 1
    assert facts[0].text == "Prefers Python for backend"


def test_extract_facts_empty_entries_returns_empty(mock_config):
    facts = extract_facts([], mock_config)
    assert facts == []


@patch("dwriter.ai.engine.get_ai_client")
def test_extract_facts_exception_returns_empty(mock_get_client, mock_config, mock_entry):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    
    facts = extract_facts([mock_entry], mock_config)
    assert facts == []


def test_project_extracted_facts(tmp_path):
    projector = GraphProjector(graph_path=tmp_path / "test.lbug")
    
    facts = [
        ExtractedFact(text="Fact 1", category="preference"),
        ExtractedFact(text="Fact 2", category="goal")
    ]
    
    entry_uuid = "source-entry-uuid"
    
    project_extracted_facts(facts, entry_uuid, projector)
    
    rows = projector.run_cypher("MATCH (f:Fact) RETURN f.text AS text")
    assert len(rows) == 2
    texts = {row["text"] for row in rows}
    assert texts == {"Fact 1", "Fact 2"}
