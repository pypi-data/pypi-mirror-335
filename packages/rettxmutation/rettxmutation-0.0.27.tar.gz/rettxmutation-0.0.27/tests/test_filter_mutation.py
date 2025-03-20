import pytest
import logging
from rettxmutation.analysis.models import GeneMutation
from rettxmutation.analysis.mutation_filtering import MutationFilter


@pytest.fixture
def mutations():
    """
    A list of GeneMutation instances to test the filter on.
    """
    return [
        GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=1.0),
        GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.1035A>G", confidence=1.0),
        GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.999G>A", confidence=0.5),
    ]


@pytest.fixture
def mutations_repeated():
    """
    A list of GeneMutation instances to test the filter on.
    """
    return [
        GeneMutation(gene_transcript="NM_001110792.2", gene_variation="c.916C>T", confidence=0.9),
        GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=1.0)
    ]


def test_filter_mutations(mutations, caplog):
    """
    Test that function filters mutations based on a minimum confidence level.
    """
    # To see log output in pytest, you can set the level:
    caplog.set_level(logging.INFO)

    filter_instance = MutationFilter()
    result = filter_instance.filter_mutations(mutations, 0.4)

    # We expect:
    #  - c.916C>T -> will be in result, confidence = 1.0
    #  - c.1035A>G -> will be in result, confidence = 1.0
    #  - c.999G>A -> will be in result, confidence = 0.5
    assert len(result) == 3
    # Check each mutation’s confidence
    assert result[0].confidence == 1.00  # c.916C>T
    assert result[1].confidence == 1.00  # c.1035A>G
    assert result[2].confidence == 0.50  # c.999G>A


def test_filter_out_mutations(mutations, caplog):
    """
    Test that function filters mutations based on a minimum confidence level.
    """
    # To see log output in pytest, you can set the level:
    caplog.set_level(logging.INFO)

    filter_instance = MutationFilter()
    result = filter_instance.filter_mutations(mutations, 0.6)

    # We expect:
    #  - c.916C>T -> will be in result, confidence = 1.0
    #  - c.1035A>G -> will be in result, confidence = 1.0
    #  - c.999G>A -> filtered out due to low confidence
    assert len(result) == 2
    # Check each mutation’s confidence
    assert result[0].confidence == 1.00  # c.916C>T
    assert result[1].confidence == 1.00  # c.1035A>G


def test_filter_out_mutations_second(mutations_repeated):
    """
    Test that function filters mutations based on a minimum confidence level.
    """
    filter_instance = MutationFilter()
    result = filter_instance.filter_mutations(mutations_repeated, 0.5)

    # We expect:
    #  - NM_004992.4:c.916C>T -> will be in result, confidence = 1.0
    #  - NM_001110792.2:c.916C>T -> filtered out due to lower confidence (it's a repeated mutation)
    assert len(result) == 1
    # Check each mutation’s confidence
    assert result[0].confidence == 1.00  # c.916C>T


def test_filter_mutations_same_confidence():
    filter_instance = MutationFilter()
    # Both have the same variation c.916C>T
    mutations = [
        GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=0.8),
        GeneMutation(gene_transcript="NM_001110792.2", gene_variation="c.916C>T", confidence=0.8)
    ]

    result = filter_instance.filter_mutations(mutations, 0.0)
    # Because both are duplicates, the code hits the 'else' block
    # but since 0.8 == 0.8, mutation.confidence > best_mutations[var].confidence is False,
    # so we never update best_mutations[var].

    assert len(result) == 1
    # The coverage should now show that line is executed.
