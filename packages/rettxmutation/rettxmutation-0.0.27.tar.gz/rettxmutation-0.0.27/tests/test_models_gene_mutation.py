# test_models.py
import pytest
from rettxmutation.analysis.models import GeneMutation, ProteinMutation

# Mock mutalyzer json model
MOCK_MUTALYZER_GENE_MODEL = {
    "type": "description_dna",
    "reference": {
        "id": "NM_004992.4"
    },
    "coordinate_system": "c",
    "variants": [
        {
            "location": {
                    "type": "point",
                    "position": 916
            },
            "type": "substitution",
            "source": "reference",
            "deleted": [
                {
                    "sequence": "C",
                    "source": "description"
                }
            ],
            "inserted": [
                {
                    "sequence": "T",
                    "source": "description"
                }
            ]
        }
    ]
}

MOCK_MUTALYZER_PROTEIN_MODEL = {
    "type": "description_protein",
    "reference": {
        "id": "NP_004983.1"
    },
    "coordinate_system": "p",
    'predicted': True,
    "variants": [
        {
            "location": {
                "type": "point",
                "amino_acid": "Arg",
                "position": 306
            },
            "type": "substitution",
            "source": "reference",
            "inserted": [
                {
                    "sequence": "Cys",
                    "source": "description"
                }
            ]
        }
    ]
}


def test_from_hgvs_string_valid():
    mutation = GeneMutation.from_hgvs_string("NM_004992.4:c.916C>T")
    assert mutation.gene_transcript == "NM_004992.4"
    assert mutation.gene_variation == "c.916C>T"
    assert mutation.confidence == 0
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_GENE_MODEL


def test_from_hgvs_string_invalid():
    with pytest.raises(Exception):
        GeneMutation.from_hgvs_string("InvalidString")


def test_model_validation():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T",
        confidence=0.9
    )
    assert mutation.gene_transcript == "NM_004992.4"
    assert mutation.gene_variation == "c.916C>T"
    assert mutation.confidence == 0.9
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_GENE_MODEL


def test_to_hgvs_string():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T"
    )
    assert mutation.to_hgvs_string() == "NM_004992.4:c.916C>T"


def test_get_transcript():
    mutation = GeneMutation(
        gene_transcript="NM_004992.4",
        gene_variation="c.916C>T"
    )
    assert mutation.get_transcript() == "NM_004992"


def test_get_transcript_without_version():
    mutation = GeneMutation(
        gene_transcript="NM_004992",
        gene_variation="c.916C>T"
    )
    assert mutation.get_transcript() == "NM_004992"


def test_invalid_gene_mutation():
    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992,4",
            gene_variation="c.916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation="c.916C>"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation=".916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation="c916>T"
        )


def test_invalid_gene_mutation_with_none_fields():
    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript=None,
            gene_variation="c.916C>T"
        )

    with pytest.raises(ValueError):
        GeneMutation(
            gene_transcript="NM_004992.4",
            gene_variation=None
        )


def test_protein_from_hgvs_string_valid():
    mutation = ProteinMutation.from_hgvs_string("NP_004983.1:p.(Arg306Cys)")
    assert mutation.protein_transcript == "NP_004983.1"
    assert mutation.protein_variation == "p.(Arg306Cys)"
    assert mutation.confidence == 0
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_PROTEIN_MODEL


def test_protein_from_hgvs_string_invalid():
    with pytest.raises(Exception):
        ProteinMutation.from_hgvs_string("InvalidString")


def test_protein_model_validation():
    mutation = ProteinMutation(
        protein_transcript="NP_004983.1",
        protein_variation="p.(Arg306Cys)",
        confidence=0.9
    )
    assert mutation.protein_transcript == "NP_004983.1"
    assert mutation.protein_variation == "p.(Arg306Cys)"
    assert mutation.confidence == 0.9
    assert mutation.mutalyzer_model == MOCK_MUTALYZER_PROTEIN_MODEL


def test_invalid_protein_mutation():
    with pytest.raises(Exception):
        ProteinMutation(
            gene_transcript="NP_004983,1",
            gene_variation="p.(Arg306Cys"
        )

    with pytest.raises(Exception):
        ProteinMutation(
            gene_transcript="NP_004983.1",
            gene_variation="p(Arg306Cys)"
        )
