from rettxmutation.analysis.models import GeneMutation


def test_from_hgvs():
    mutation = GeneMutation.from_hgvs_string("NM_004992.3:c.100A>T")
    assert mutation.gene_transcript == "NM_004992.3"
    assert mutation.gene_variation == "c.100A>T"


def test_add_hgvs():
    mutation = GeneMutation(
        gene_transcript="NM_004992.3",
        gene_variation="c.100A>T"
    )
    assert mutation.gene_transcript == "NM_004992.3"
    assert mutation.gene_variation == "c.100A>T"
    assert mutation.confidence == 0.0
