from typing import Optional
from pydantic import BaseModel, Field

class CoreGeneMutation(BaseModel):
    """
    Core mutation data model for standardized storage.

    Fields:
      - genomic_coordinate: Canonical genomic coordinate (e.g., "NC_000023.11:g.154030912G>A")
      - canonical_hgvs: HGVS on the canonical transcript (e.g., "NM_004992.4:c.916C>T")
      - alternate_hgvs: HGVS on the alternate transcript (e.g., "NM_001110792.2:c.952C>T")
      - protein_consequence: Protein-level consequence (e.g., "NP_004983.1:p.Arg306Cys")
      - mane_tag: Tag indicating MANE status (e.g., "MANE Plus Clinical")
      - source: Which external API was used (e.g., "Mutalyzer")
      - confidence_score: Confidence score for the mutation normalization process.
    """
    genomic_coordinate: str = Field(..., description="Canonical genomic coordinate (e.g., NC_000023.11:g.154030912G>A)")
    canonical_hgvs: str = Field(..., description="HGVS on the canonical transcript (e.g., NM_004992.4:c.916C>T)")
    alternate_hgvs: Optional[str] = Field(None, description="HGVS on the alternate transcript (e.g., NM_001110792.2:c.952C>T)")
    protein_consequence: Optional[str] = Field(None, description="Protein-level consequence (e.g., NP_004983.1:p.Arg306Cys)")
    mane_tag: Optional[str] = Field(None, description="Tag indicating MANE status (e.g., MANE Plus Clinical)")
    source: str = Field("Mutalyzer", description="Source of normalization")
    confidence_score: Optional[float] = Field(1.0, description="Confidence score for the mutation normalization")
