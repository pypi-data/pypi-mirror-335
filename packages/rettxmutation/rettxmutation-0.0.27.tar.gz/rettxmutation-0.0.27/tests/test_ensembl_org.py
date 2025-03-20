import json
import pytest
import requests
from unittest.mock import patch, MagicMock, mock_open
from rettxmutation.analysis.ensembl_org import EnsemblOrgService, InvalidMutationError
from rettxmutation.analysis.models import GeneMutationCollection


# Mock API response for the request
MOCK_API_RESPONSE = [
    {
        "T": {
            "spdi": [
                "NC_000023.11:154030911:G:A",
                "LRG_764:111191:C:T"
            ],
            "id": [
                "rs28935468",
                "CM993354",
                "COSV100318414"
            ],
            "hgvsc": [
                "ENST00000303391.11:c.916C>T",
                "NM_004992.4:c.916C>T"
            ],
            "hgvsp": [
                "ENSP00000301948.6:p.Arg306Cys",
                "NP_004983.1:p.Arg306Cys"
            ],
            "hgvsg": [
                "NC_000023.11:g.154030912G>A"
            ],
            "input": "NM_004992.4:c.916C>T"
        }
    }
]

TEST_TRANSCRIPTS_JSON = {
    "ENST00000303391": "11",
    "ENST00000369957": "5",
    "ENST00000407218": "5",
    "ENST00000415944": "4",
    "ENST00000453960": "7",
    "ENST00000486506": "5",
    "ENST00000628176": "2",
    "ENST00000630151": "3",
    "ENST00000637917": "2",
    "ENST00000674996": "2",
    "ENST00000675526": "2",
    "ENST00000713611": "1",
    "NM_001110792": "2",
    "NM_001316337": "2",
    "NM_001369391": "2",
    "NM_001369392": "2",
    "NM_001369393": "2",
    "NM_001369394": "2",
    "NM_001386137": "1",
    "NM_001386138": "1",
    "NM_001386139": "1",
    "NM_004992": "4",
    "XM_024452383": "2",
    "XM_047442115": "1",
    "XM_047442116": "1",
    "XM_047442117": "1",
    "XM_047442118": "1",
    "XM_047442119": "1",
    "XM_047442120": "1",
    "XM_047442121": "1",
    "NM_123": None
}


@pytest.fixture
def ensembl_service():
    """Fixture to initialize the EnsemblOrgService."""
    service = EnsemblOrgService()
    yield service
    service.close()


@pytest.fixture
def mock_latest_transcripts_file():
    from unittest.mock import mock_open, patch
    test_json = json.dumps(TEST_TRANSCRIPTS_JSON)
    with patch("rettxmutation.analysis.ensembl_org.open", mock_open(read_data=test_json)):
        yield


@pytest.fixture
def mock_latest_transcripts_json():
    """
    Returns a JSON string for the `_load_latest_transcripts` method.
    """
    return """{
        "ENST00000303391": "11",
        "NM_004992": "4",
        "NM_001110792": "2",
        "LRG_764t1": null
    }"""


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_fetch_variations_success(mock_get, ensembl_service):
    # Mock the GET request to return a successful response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value=MOCK_API_RESPONSE)
    )

    # Call the method
    result = ensembl_service._fetch_variations("NM_004992.4", "c.916C>T")

    # Assert the response matches the mocked data
    assert result == MOCK_API_RESPONSE
    mock_get.assert_called_once_with(
        "https://rest.ensembl.org/variant_recoder/human/NM_004992.4:c.916C>T?content-type=application/json"
    )


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_parse_to_model_success(mock_get, ensembl_service):
    # Mock the GET request to return the mocked response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value=MOCK_API_RESPONSE)
    )

    # Call the `fetch_variations` method
    api_response = ensembl_service._fetch_variations("NM_004992.4", "c.916C>T")

    # Parse the response into a GeneMutationCollection model
    result = ensembl_service._parse_to_model(api_response)

    # Verify the parsed model
    assert isinstance(result, GeneMutationCollection)
    mutation = result.mutation_info
    assert mutation.spdi == ["NC_000023.11:154030911:G:A", "LRG_764:111191:C:T"]
    assert mutation.hgvsc == ["ENST00000303391.11:c.916C>T", "NM_004992.4:c.916C>T"]
    assert mutation.hgvsp == ["ENSP00000301948.6:p.Arg306Cys", "NP_004983.1:p.Arg306Cys"]
    assert mutation.hgvsg == ["NC_000023.11:g.154030912G>A"]
    assert mutation.id == ["rs28935468", "CM993354", "COSV100318414"]
    assert mutation.input == "NM_004992.4:c.916C>T"

    assert result.mutation_id == "NM_004992.4:c.916C>T"


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_fetch_variations_invalid_mutation(mock_get, ensembl_service):
    # Mock the GET request to simulate a 400 error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_get.return_value = mock_response

    # Test invalid mutation handling
    with pytest.raises(InvalidMutationError, match="The mutation position or base is invalid."):
        ensembl_service._fetch_variations("NM_004992.4", "invalid_variant")


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_fetch_variations_connection_error(mock_get, ensembl_service, caplog):
    """
    Because the code re-raises the ConnectionError, we now expect the call
    to fail, not return a dict.
    """
    # Simulate a connection error with a custom message
    mock_get.side_effect = requests.exceptions.ConnectionError("Simulated connection error")

    # Since it re-raises, we do not get a return value; we expect an exception
    with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
        ensembl_service._fetch_variations("NM_004992.4", "c.916C>T")

    # Confirm the exception contains our custom message
    assert "Simulated connection error" in str(exc_info.value)

    # We can still check logs if you want
    assert "Error during API call" in caplog.text
    assert "ConnectionError" in caplog.text


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_get_mutation_invalid(mock_get, ensembl_service):
    # Mock the GET request to return the mocked response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value=MOCK_API_RESPONSE)
    )

    # Call the `fetch_variations` method
    api_response = ensembl_service._fetch_variations("NM_004992.4", "c.916C>T")

    # Parse the response into a GeneMutationCollection model
    result = ensembl_service._parse_to_model(api_response)

    correct_result = result.get_mutation_by_transcript("NM_004992.4", "hgvsc")
    assert correct_result == "c.916C>T"

    with pytest.raises(ValueError):
        result.get_mutation_by_transcript("NM_004992.4", "invalid")

    empty_result = result.get_mutation_by_transcript("empty_transcript", "hgvsc")
    assert empty_result is None


@pytest.mark.parametrize("test_input,expected", [
    ("NM_001110792.1", "NM_001110792.2"),  # Existing, recognized transcript with version
    ("NM_001110792", "NM_001110792.2"),    # Existing, recognized transcript without version
    ("NM_004992", "NM_004992.4"),  # Existing, recognized transcript with version
    ("NM_004992.1", "NM_004992.4"),  # Existing, recognized transcript with version
    ("NM_004992.2", "NM_004992.4"),  # Existing, recognized transcript with version
    ("LRG_764t1", "LRG_764t1")            # Transcript with null versioning
])
def test_get_latest_transcript_found(mock_latest_transcripts_json, test_input, expected):
    """
    Test that recognized transcripts (with or without versions) return the correct latest version.
    """
    with patch("builtins.open", mock_open(read_data=mock_latest_transcripts_json)):
        service = EnsemblOrgService()
        assert service._get_latest_transcript(test_input) == expected


def test_get_latest_transcript_unrecognized(mock_latest_transcripts_json):
    """
    Test that an unrecognized transcript raises a ValueError.
    """
    with patch("builtins.open", mock_open(read_data=mock_latest_transcripts_json)):
        service = EnsemblOrgService()
        with pytest.raises(ValueError) as exc_info:
            service._get_latest_transcript("NM_99999999")
        assert "Unrecognized transcript ID" in str(exc_info.value)

        # Call the `_get_latest_transcript` method with non existing transcript
        with pytest.raises(ValueError):
            service._get_latest_transcript("NM_1234")

        # Call the `_get_latest_transcript` method with non existing transcript
        with pytest.raises(ValueError):
            service._get_latest_transcript("123.abc")


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_get_gene_mutation_collection_success(mock_get, ensembl_service, mock_latest_transcripts_file):
    """
    Test the 'happy path' where:
      - The transcript is recognized (e.g., 'NM_004992').
      - The GET request returns a valid 200 response with the MOCK_API_RESPONSE.
      - We confirm `get_gene_mutation_collection` returns a GeneMutationCollection.
    """
    # Mock the GET request to return the known successful response
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value=MOCK_API_RESPONSE)
    )

    # Call the method under test
    collection = ensembl_service.get_gene_mutation_collection("NM_004992", "c.916C>T")

    # Validate the result
    assert isinstance(collection, GeneMutationCollection)
    mutation = collection.mutation_info
    assert mutation.spdi == ["NC_000023.11:154030911:G:A", "LRG_764:111191:C:T"]
    assert mutation.hgvsc == ["ENST00000303391.11:c.916C>T", "NM_004992.4:c.916C>T"]
    assert mutation.hgvsp == ["ENSP00000301948.6:p.Arg306Cys", "NP_004983.1:p.Arg306Cys"]
    assert mutation.hgvsg == ["NC_000023.11:g.154030912G>A"]
    assert mutation.id == ["rs28935468", "CM993354", "COSV100318414"]
    assert mutation.input == "NM_004992.4:c.916C>T"

    # Make sure the request was actually called with the correct "latest" transcript version
    # From TEST_TRANSCRIPTS_JSON, "NM_004992" -> "4"
    expected_url = (
        f"{ensembl_service.BASE_URL}/NM_004992.4:c.916C>T?content-type=application/json"
    )
    mock_get.assert_called_once_with(expected_url)


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_get_gene_mutation_collection_invalid_mutation(mock_get, ensembl_service, mock_latest_transcripts_file):
    """
    Test a 400 status code from the API, which should raise an InvalidMutationError
    when calling get_gene_mutation_collection.
    """
    # Mock the GET request to simulate a 400 (bad request)
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
    mock_get.return_value = mock_response

    # Attempting to fetch with an invalid variant should raise InvalidMutationError
    with pytest.raises(InvalidMutationError, match="The mutation position or base is invalid."):
        ensembl_service.get_gene_mutation_collection("NM_004992", "invalid_variant")


@patch("rettxmutation.analysis.ensembl_org.requests.Session.get")
def test_get_gene_mutation_collection_api_errors(mock_get, ensembl_service, mock_latest_transcripts_file):
    """
    Test other API errors (500, 503, etc.) should raise an HTTPError when calling get_gene_mutation_collection.
    Test a ValueError when the transcript is not recognized.
    """
    # Mock the GET request to simulate a 500 (internal server error)
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
    mock_get.return_value = mock_response

    # Simulate an uncontrollable API error
    with pytest.raises(requests.exceptions.HTTPError, match="500 Internal Server Error"):
        ensembl_service.get_gene_mutation_collection("NM_004992", "invalid_variant")

    # Simulate a generic exception
    mock_get.side_effect = Exception("Simulated API error")
    with pytest.raises(Exception, match="Simulated API error"):
        ensembl_service.get_gene_mutation_collection("NM_004992", "invalid_variant")
