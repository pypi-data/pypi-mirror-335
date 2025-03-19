# test_confidence_score.py
import pytest
from rettxmutation.analysis.mutation_filtering import MutationFilter
from rettxmutation.analysis.models import GeneMutation


class Keyword:
    def __init__(self, value, type):
        self.value = value
        self.type = type


@pytest.fixture
def mutation_filter():
    return MutationFilter()


#
# Keyword confidence tests
#
def test_calc_keyword_confidence_no_keywords(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    assert mutation_filter.calc_keyword_confidence(mutation, [], []) == 0.0


def test_calc_keyword_confidence_with_variant_in_mecp2(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    mecp2_keywords = [Keyword("c.916C>T", "variant_c")]
    variant_list = []
    assert mutation_filter.calc_keyword_confidence(mutation, mecp2_keywords, variant_list) == 0.4


def test_calc_keyword_confidence_with_variant_in_list(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    variant_list = [Keyword("c.916C>T", "variant_c")]
    assert mutation_filter.calc_keyword_confidence(mutation, [], variant_list) == 0.4


def test_calc_keyword_confidence_with_transcript_in_mecp2(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    mecp2_keywords = [Keyword("NM_004992.4", "reference_sequence")]
    assert mutation_filter.calc_keyword_confidence(mutation, mecp2_keywords, []) == 0.2


def test_calc_keyword_confidence_all_found(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    mecp2_keywords = [
        Keyword("c.916C>T", "variant_c"),
        Keyword("NM_004992.4", "reference_sequence")
    ]
    variant_list = [Keyword("c.916C>T", "variant_c")]
    # 0.4 + 0.4 + 0.2 = 1.0
    assert mutation_filter.calc_keyword_confidence(mutation, mecp2_keywords, variant_list) == 1.0


#
# Proximity confidence tests
#
def test_calc_proximity_confidence_full(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation NM_004992.4:c.916C>T."
    # Mutation and transcript are in the same sentence, very close
    assert mutation_filter.calc_proximity_confidence(document_text, mutation) == 1.0


def test_calc_proximity_confidence_zero(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation c.916C>T."
    # Only mutation is in the text, so confidence should be 0
    assert mutation_filter.calc_proximity_confidence(document_text, mutation) == 0.0


def test_calc_proximity_confidence_closeby(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation c.916C>T. The transcript is NM_004992.4."
    # Mutation and transcript are in the same document, with a bit of distance
    assert mutation_filter.calc_proximity_confidence(document_text, mutation) == 0.8003351677002152


def test_calc_proximity_confidence_default_values(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation c.916C>T. The transcript is NM_004992.4."
    # Mutation and transcript are in the same document, with a bit of distance
    assert mutation_filter.calc_proximity_confidence(document_text, mutation, alpha=0.01, beta=1.0) == 0.8003351677002152


def test_calc_proximity_confidence_change_beta(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation c.916C>T. The transcript is NM_004992.4."
    # Mutation and transcript are in the same document, with a bit of distance
    assert mutation_filter.calc_proximity_confidence(document_text, mutation, alpha=0.01, beta=2.0) == 0.7577685710361437


def test_calc_proximity_confidence_change_alpha(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    document_text = "This is a test document with a mutation c.916C>T. The transcript is NM_004992.4."
    # Mutation and transcript are in the same document, with a bit of distance
    assert mutation_filter.calc_proximity_confidence(document_text, mutation, alpha=0.1, beta=1.0) == 0.10536148886970764


def test_calc_proximity_confidence_variation_missing(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T")
    # This text has the transcript but NOT the variation
    document_text = "Transcript is NM_004992.4"
    # Expect the function to return 0.0 because variation is not found
    assert mutation_filter.calc_proximity_confidence(document_text, mutation) == 0.0


#
# Combined confidence tests
#
def test_calc_combined_confidence_full(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=1.0)
    document_text = "This is a test document with a mutation NM_004992.4:c.916C>T."
    mecp2_keywords = [
        Keyword("c.916C>T", "variant_c"),
        Keyword("NM_004992.4", "reference_sequence")
    ]
    variant_list = [Keyword("c.916C>T", "variant_c")]
    gene_mutations = mutation_filter.calculate_confidence_score(document_text, [mutation], mecp2_keywords, variant_list)

    assert gene_mutations[0].confidence == 1.0


def test_calc_combined_confidence_basechange(mutation_filter):
    # Change the confidence of the mutation to 0.5
    # With base confidence weight of 40, the final confidence should be:
    # 0.5 * 40 + 1.0 * 30 + 1.0 * 30 = 80
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=0.5)
    document_text = "This is a test document with a mutation NM_004992.4:c.916C>T."
    mecp2_keywords = [
        Keyword("c.916C>T", "variant_c"),
        Keyword("NM_004992.4", "reference_sequence")
    ]
    variant_list = [Keyword("c.916C>T", "variant_c")]
    gene_mutations = mutation_filter.calculate_confidence_score(
        document_text,
        [mutation],
        mecp2_keywords,
        variant_list,
        base_conf_weight=40,
        keyword_weight=30,
        proximity_weight=30)

    assert gene_mutations[0].confidence == 0.8


def test_calc_combined_confidence_keywordchange(mutation_filter):
    # Change the confidence of the mutation to 0.5
    # With base confidence weight of 40, the final confidence should be:
    # 0.5 * 40 + 1.0 * 30 + 1.0 * 30 = 80
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=0.5)
    document_text = "This is a test document with a mutation NM_004992.4:c.916C>T."
    mecp2_keywords = [
        Keyword("NM_004992.4", "reference_sequence")
    ]
    variant_list = [Keyword("c.916C>T", "variant_c")]
    gene_mutations = mutation_filter.calculate_confidence_score(
        document_text,
        [mutation],
        mecp2_keywords,
        variant_list,
        base_conf_weight=40,
        keyword_weight=30,
        proximity_weight=30)

    assert gene_mutations[0].confidence == 0.68


# Pass incorrect weights to the function
def test_calc_combined_confidence_error(mutation_filter):
    mutation = GeneMutation(gene_transcript="NM_004992.4", gene_variation="c.916C>T", confidence=0.5)
    document_text = "This is a test document with a mutation NM_004992.4:c.916C>T."
    mecp2_keywords = [
        Keyword("NM_004992.4", "reference_sequence")
    ]
    variant_list = [Keyword("c.916C>T", "variant_c")]

    # The function should raise a ValueError
    with pytest.raises(ValueError):
        mutation_filter.calculate_confidence_score(
            document_text,
            [mutation],
            mecp2_keywords,
            variant_list,
            base_conf_weight=50,
            keyword_weight=30,
            proximity_weight=30)
