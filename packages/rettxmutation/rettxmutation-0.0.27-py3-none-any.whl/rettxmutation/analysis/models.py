import logging
from mutalyzer_hgvs_parser import to_model
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


logger = logging.getLogger(__name__)


class GeneMutation(BaseModel):
    """
    Model to represent a mutation:
        gene_transcript = NM_004992.4
        gene_variation = c.916C>T
    """
    gene_transcript: str = Field(..., description="Gene transcript identifier")
    gene_variation: str = Field(..., description="Gene variation (HGVS nomenclature)")
    confidence: Optional[float] = Field(None, description="Confidence score")
    mutalyzer_model: dict = Field(None, description="The mutalyzer dict returned when parsing the mutation")

    @classmethod
    def from_hgvs_string(cls, hgvs_string: str) -> "GeneMutation":
        """
        Split an HGVS string like 'NM_004992.4:c.916C>T' into transcript and variation,
        then build a GeneMutation model instance.
        """
        try:
            model = to_model(hgvs_string, start_rule=None)
            logger.debug(f"mutalyzer_model = {model}")
            # Split and remove any leading/trailing spaces
            transcript, variation = hgvs_string.split(":", 1)
            transcript = transcript.strip()
            variation = variation.strip()
            logger.debug(f"transcript = {transcript}")
            logger.debug(f"variation = {variation}")
        except Exception as e:
            logger.error(f"Invalid HGVS mutation: {e}")
            raise

        return cls(
            gene_transcript=transcript,
            gene_variation=variation,
            confidence=0,
            mutalyzer_model=model
        )

    @model_validator(mode="after")
    def validate_mutation(cls, values):
        """
        Validate the mutation using pyhgvs at the model level.
        This allows cross-checking of transcript vs. variation if needed.
        """
        transcript = values.gene_transcript
        variation = values.gene_variation

        try:
            hgvs_string = f"{transcript}:{variation}"
            model = to_model(hgvs_string)
            values.mutalyzer_model = model
            logger.debug(f"Mutalyzer model: {model}")

        except Exception as exc:
            logger.error(f"Invalid HGVS mutation: {variation}. Error: {exc}")
            raise ValueError(
                f"Invalid HGVS mutation: {variation}. Error: {exc}"
            ) from exc

        # Set confidence to 0 if not provided
        if values.confidence is None:
            values.confidence = 0

        return values

    def to_hgvs_string(self) -> str:
        """
        Return a full HGVS string in the format '{gene_transcript}:{gene_variation}'.
        Example: 'NM_004992.4:c.916C>T'
        """
        return f"{self.gene_transcript}:{self.gene_variation}"

    def get_transcript(self) -> str:
        """
        Return the transcript without the version number, if present.
        Example: 'NM_004992'
        """
        transcript = self.gene_transcript.split(".", 1)[0]
        return transcript


class ProteinMutation(BaseModel):
    """
    Model to represent a protein mutation:
        protein_transcript = NP_004983.1
        protein_variation = p.Arg306Cys
    """
    protein_transcript: str = Field(..., description="Protein transcript identifier")
    protein_variation: str = Field(..., description="Protein variation (HGVS nomenclature)")
    confidence: Optional[float] = Field(None, description="Confidence score")
    mutalyzer_model: dict = Field(None, description="The mutalyzer dict returned when parsing the mutation")

    @classmethod
    def from_hgvs_string(cls, hgvs_string: str) -> "ProteinMutation":
        """
        Split an HGVS string like 'NP_004983.1:p.(Arg306Cys)' into transcript and variation,
        then build a ProteinMutation model instance.
        """
        try:
            model = to_model(hgvs_string, start_rule=None)
            logger.debug(f"mutalyzer_model = {model}")
            # Split and remove any leading/trailing spaces
            transcript, variation = hgvs_string.split(":", 1)
            transcript = transcript.strip()
            variation = variation.strip()
            logger.debug(f"transcript = {transcript}")
            logger.debug(f"variation = {variation}")
        except Exception as e:
            logger.error(f"Invalid HGVS mutation: {e}")
            raise

        return cls(
            protein_transcript=transcript,
            protein_variation=variation,
            confidence=0,
            mutalyzer_model=model
        )

    @model_validator(mode="after")
    def validate_protein_mutation(cls, values):
        """
        Validate the mutation using pyhgvs at the model level.
        This allows cross-checking of transcript vs. variation if needed.
        """
        transcript = values.protein_transcript
        variation = values.protein_variation

        try:
            hgvs_string = f"{transcript}:{variation}"
            model = to_model(hgvs_string)
            values.mutalyzer_model = model
            logger.debug(f"Mutalyzer model: {model}")

        except Exception as exc:
            logger.error(f"Invalid HGVS mutation: {variation}. Error: {exc}")
            raise ValueError(
                f"Invalid HGVS mutation: {variation}. Error: {exc}"
            ) from exc

        # Set confidence to 0 if not provided
        if values.confidence is None:
            values.confidence = 0

        return values


# Word data model, extracted from a document by OCR tool
class WordData(BaseModel):
    word: str = Field(..., description="The word extracted from the document")
    confidence: float = Field(..., description="Confidence score of the extracted word")
    page_number: int = Field(..., description="Page number where the word was found")
    offset: int = Field(None, description="Offset of the word in the page")
    length: int = Field(None, description="Length of the word")

# Line data model, extracted from a document by OCR tool
class LineData(BaseModel):
    line: str = Field(..., description="The line extracted from the document")
    page_number: int = Field(..., description="Page number where the line was found")
    length: int = Field(None, description="Length of the line")

# Mecp2 keyword model
class Keyword(BaseModel):
    value: str = Field(..., description="The value of the detected keyword")
    type: str = Field(..., description="The type of the keyword (e.g., 'gene_name', 'variant_c', etc.)")
    count: int = Field(1, description="Number of occurrences of the keyword")
    confidence: Optional[float] = Field("", description="Confidence score of the detected keyword")


# Document model
class Document(BaseModel):
    raw_text: str = Field(..., description="The extracted text from the document")
    cleaned_text: Optional[str] = Field("", description="The cleaned version of the extracted text")
    summary: Optional[str] = Field("", description="Summary of the document content")
    language: str = Field(..., description="Language of the extracted text")
    words: List[WordData] = Field(..., description="List of extracted words with confidence scores")
    lines: List[LineData] = Field(..., description="List of extracted lines")
    keywords: Optional[List[Keyword]] = Field(None, description="List of detected mecp2 keywords")
    text_analytics_result: Optional[List[Keyword]] = Field(None, description="List of detected keywords from text analytics")

    def find_word_confidence(self, word_to_find: str) -> Optional[float]:
        """
        Finds a word in the word data and returns its confidence value.

        :param word_to_find: The word to search for in the words data.
        :return: The confidence score of the word if found, else None.
        """
        for word_data in self.words:
            if word_to_find in word_data.word:
                return word_data.confidence
        return None

    def dump_keywords(self, separator: str = "\n") -> str:
        """
        Dump the instance's keywords into a single string for serialization.
        Each keyword's value is separated by a space.
        """
        if not self.keywords:
            return ""
        return separator.join(keyword.value for keyword in self.keywords)

    def dump_text_analytics_keywords(self, separator: str = "\n") -> str:
        """
        Dump the instance's text analytics keywords into a single string for serialization.
        Each keyword's value is separated by a space.
        """
        if not self.text_analytics_result:
            return ""
        return separator.join(keyword.value for keyword in self.text_analytics_result)

    def dump_all_content(self) -> dict:
        """
        Dump the document content into a dictionary for serialization.
        """
        return {
            "cleaned_text": self.cleaned_text,
            "language": self.language,
            "keywords": self.dump_keywords()
        }

    def dump_plain_text(self) -> str:
        """
        Generates a plain text output concatenating cleaned_text with keywords (only keywords.value).
        """
        keywords_text = " ".join(keyword.value for keyword in self.keywords) if self.keywords else ""
        return f"{self.cleaned_text.strip()} {keywords_text}".strip()


class MutationDetail(BaseModel):
    """
    Model to represent a mutation with different notations.
    """
    spdi: List[str] = Field(..., description="SPDI format identifiers")
    id: List[str] = Field(..., description="IDs associated with the mutation (e.g., dbSNP, ClinVar, etc.)")
    hgvsp: List[str] = Field(..., description="Protein-level HGVS notations")
    hgvsc: List[str] = Field(..., description="Coding sequence-level HGVS notations")
    hgvsg: List[str] = Field(..., description="Genomic-level HGVS notations")
    input: str = Field(..., description="The input string that triggered the query")

    def get_mutation_by_transcript(
        self, 
        transcript: str, 
        notation_type: str = "hgvsc"
    ) -> Optional[str]:
        """
        Find the mutation in HGVS notation (`hgvsc` or `hgvsp`) for a given transcript.
        Returns the mutation string (e.g., 'c.952C>T' or 'p.Arg306Cys') or None if not found.
        """
        if notation_type not in {"hgvsc", "hgvsp"}:
            raise ValueError("Invalid notation_type. Use 'hgvsc' or 'hgvsp'.")

        notation_list = getattr(self, notation_type, [])
        for notation in notation_list:
            if notation.startswith(transcript):
                return notation.split(':', 1)[1]

        return None


# Constant to represent the standard transcripts
STANDARD_GENE_TRANSCRIPT = "NM_004992.4"
GENE_NOTATION_TYPE = "hgvsc"
STANDARD_PROTEIN_TRANSCRIPT = "NP_004983.1"
PROTEIN_NOTATION_TYPE = "hgvsp"


class GeneMutationCollection(BaseModel):
    """
    Model to represent a collection of mutations for a gene.
    """
    mutation_id: str = Field(..., description="Unique identifier for the mutation")
    mutation_info: MutationDetail = Field(..., description="Different notations for the same mutation")
    gene_mutation: Optional[GeneMutation] = Field(None, description="Gene mutation in HGVS notation")
    protein_mutation: Optional[ProteinMutation] = Field(None, description="Protein mutation in HGVS notation")
    confidence: Optional[float] = Field(None, description="Confidence score for the mutation")

    def get_mutation_by_transcript(self, transcript: str, notation_type: str = "hgvsc") -> Optional[str]:
        return self.mutation_info.get_mutation_by_transcript(transcript, notation_type)
