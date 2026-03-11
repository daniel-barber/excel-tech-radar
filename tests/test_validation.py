"""Tests for Excel loading and validation."""

import pytest
from pathlib import Path
from excel_radar.loader import (
    slugify,
    parse_boolean,
    RadarConfig,
    RingConfig,
    QuadrantConfig,
)


class TestSlugify:
    """Test slugify function."""

    def test_lowercase(self):
        assert slugify("Hello World") == "hello-world"

    def test_spaces_to_dashes(self):
        assert slugify("Test Case") == "test-case"

    def test_underscores_to_dashes(self):
        assert slugify("test_case") == "test-case"

    def test_trim_whitespace(self):
        assert slugify("  hello  ") == "hello"

    def test_already_slug(self):
        assert slugify("already-slug") == "already-slug"


class TestParseBoolean:
    """Test boolean parsing."""

    def test_true_values(self):
        assert parse_boolean(True) is True
        assert parse_boolean("TRUE") is True
        assert parse_boolean("true") is True
        assert parse_boolean("1") is True
        assert parse_boolean(1) is True
        assert parse_boolean("yes") is True
        assert parse_boolean("y") is True

    def test_false_values(self):
        assert parse_boolean(False) is False
        assert parse_boolean("FALSE") is False
        assert parse_boolean("false") is False
        assert parse_boolean("0") is False
        assert parse_boolean(0) is False
        assert parse_boolean("no") is False
        assert parse_boolean("n") is False
        assert parse_boolean("") is False

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            parse_boolean("invalid")

    def test_none_value(self):
        # pandas NaN handling
        import pandas as pd
        assert parse_boolean(pd.NA) is False
        assert parse_boolean(None) is False


class TestRadarConfig:
    """Test radar configuration models."""

    def test_ring_config(self):
        ring = RingConfig(
            id="adopt",
            name="Adopt",
            order=0,
            color="#4CAF50"
        )
        assert ring.id == "adopt"
        assert ring.name == "Adopt"
        assert ring.order == 0
        assert ring.color == "#4CAF50"

    def test_quadrant_config(self):
        quad = QuadrantConfig(
            id="techniques",
            name="Techniques"
        )
        assert quad.id == "techniques"
        assert quad.name == "Techniques"

    def test_radar_config_defaults(self):
        config = RadarConfig(
            title="Test Radar",
            subtitle="Q1 2026",
            rings=[
                RingConfig(id="ready", name="Ready", order=0, color="#4CAF50")
            ],
            quadrants=[
                QuadrantConfig(id="infra", name="Infrastructure")
            ]
        )
        assert config.title == "Test Radar"
        assert len(config.rings) == 1
        assert len(config.quadrants) == 1
        assert config.layout.startAngleDeg == 0


class TestRingQuadrantMapping:
    """Test ring and quadrant ID mapping."""

    def test_case_insensitive_mapping(self):
        # Test that "Ready", "ready", "READY" all map to same ID
        assert slugify("Ready") == slugify("ready")
        assert slugify("READY") == slugify("ready")

    def test_name_to_id_mapping(self):
        # Test that "Less Than 1 Year" maps to "less-than-1-year"
        assert slugify("Less Than 1 Year") == "less-than-1-year"
        assert slugify("1-3 Years") == "1-3-years"
        assert slugify("3+ Years") == "3+-years"


class TestEntryValidation:
    """Test entry validation."""

    def test_valid_entry(self):
        from excel_radar.loader import RadarEntry
        
        entry = RadarEntry(
            id="test-entry",
            name="Test Entry",
            ring="ready",
            quadrant="infrastructure",
            isNew=True,
            status="on-track",
            descriptionHtml="<p>Test description</p>",
            tags=["test", "example"],
        )
        
        assert entry.name == "Test Entry"
        assert entry.isNew is True
        assert len(entry.tags) == 2

    def test_empty_name_fails(self):
        from excel_radar.loader import RadarEntry
        
        with pytest.raises(ValueError):
            RadarEntry(
                id="test",
                name="",
                ring="ready",
                quadrant="infrastructure"
            )

    def test_tags_from_string(self):
        from excel_radar.loader import RadarEntry
        
        entry = RadarEntry(
            id="test",
            name="Test",
            ring="ready",
            quadrant="infrastructure",
            tags="cloud, aws, migration"
        )
        
        assert entry.tags == ["cloud", "aws", "migration"]

    def test_tags_empty_string(self):
        from excel_radar.loader import RadarEntry
        
        entry = RadarEntry(
            id="test",
            name="Test",
            ring="ready",
            quadrant="infrastructure",
            tags=""
        )
        
        assert entry.tags == []

