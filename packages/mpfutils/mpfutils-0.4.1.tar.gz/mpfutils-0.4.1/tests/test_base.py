from src.mpfutils.ai import OpenAIClient
from src.mpfutils.cosmosdb import CosmosDBContainer
from src.mpfutils.azstorage import AzsContainerClient
import pytest
import logging
import os

logging.basicConfig(level=logging.INFO)

@pytest.mark.skip("Expensive test")
def test_openai_client():
    c = OpenAIClient()
    capital = c.run_prompt("What is the capital of France?")
    assert "Paris" in capital

@pytest.mark.skip("SAS test")
def test_azstorage_client_sas():
    sas_url = os.getenv("MPFU_AZSTORAGE_TEST_SAS")
    c = AzsContainerClient("mpfutils-test", sas_url=sas_url)
    url = c.upload_blob("test.txt", "This is a test")
    assert url.startswith("https://")
    data = c.download_blob("mpfutils-test", "test.txt")
    assert data == b"This is a test"

def test_cosmosdb_upsert_item():
    c = CosmosDBContainer("mpfutils", "tests")
    item = {
        "id": "test",
        "name": "Test",
        "description": "This is a test"
    }
    result = c.upsert_item(item)

def test_cosmosdb_read_item():
    c = CosmosDBContainer("mpfutils", "tests")
    item = c.get_item("test")
    assert item["name"] == "Test"

def test_cosmosdb_upsert_item_2():
    c = CosmosDBContainer("mpfutils", "tests")
    item = {
        "id": "test",
        "name": "Test upsert",
        "description": "This is a test"
    }
    result = c.upsert_item(item)

def test_cosmosdb_read_item_2():
    c = CosmosDBContainer("mpfutils", "tests")
    item = c.get_item("test")
    assert item["name"] == "Test upsert"

def test_cosmosdb_delete_item():
    c = CosmosDBContainer("mpfutils", "tests")
    result = c.delete_item("test")
    assert result == True

def test_get_item_not_found():
    c = CosmosDBContainer("mpfutils", "tests")
    items = c.get_all_items()
    assert len(items) == 0
