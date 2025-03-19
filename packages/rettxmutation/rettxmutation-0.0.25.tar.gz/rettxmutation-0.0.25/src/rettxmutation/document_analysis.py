import logging
from typing import BinaryIO, List, Tuple
from rettxmutation.analysis.text_cleaner import TextCleaner
from rettxmutation.analysis.ocr_extractor import OcrExtractor
from rettxmutation.analysis.models import Document, GeneMutation
from rettxmutation.analysis.mutation_filtering import MutationFilter
from rettxmutation.analysis.text_analytics import HealthcareTextAnalyzer
from rettxmutation.analysis.openai_rettx_agents import OpenAIRettXAgents
from rettxmutation.analysis.gene_variant_detector import GeneVariantDetector
from rettxmutation.analysis.document_processing import DynamicDocumentPreprocessor
from rettxmutation.analysis.ensembl_org import EnsemblOrgService, GeneMutationCollection
from rettxmutation.models.gene_models import CoreGeneMutation
from rettxmutation.services.mutation_service_factory import create_mutation_service


logger = logging.getLogger(__name__)


class RettXDocumentAnalysis:
    """
    High-level orchestrator that uses the various sub-components
    for a full end-to-end document analysis workflow.
    """

    def __init__(
        self,
        doc_analysis_endpoint: str,
        doc_analysis_key: str,
        cognitive_services_endpoint: str,
        cognitive_services_key: str,
        openai_key: str,
        openai_model_version: str,
        openai_endpoint: str,
        openai_model_name: str,
        binarize: bool = False,
        sharpen: bool = False,
        contrast_threshold: float = 25.0
    ):
        # Initialize sub-components
        self.ocr_extractor = OcrExtractor(doc_analysis_endpoint, doc_analysis_key)
        self.text_cleaner = TextCleaner()
        self.gene_variant_detector = GeneVariantDetector()
        self.health_analyzer = HealthcareTextAnalyzer(cognitive_services_endpoint,
                                                      cognitive_services_key)
        self.openai_mutation_extractor = OpenAIRettXAgents(
            api_key=openai_key,
            api_version=openai_model_version,
            azure_endpoint=openai_endpoint,
            model_name=openai_model_name
        )
        self.mutation_filter = MutationFilter()
        #self.ensembl_org_service = EnsemblOrgService()
        self.mutation_service = create_mutation_service(provider="mutalyzer")

        # Initialize the image preprocessor
        self.file_preprocessor = DynamicDocumentPreprocessor(
            binarize=binarize,
            sharpen=sharpen,
            contrast_threshold=contrast_threshold)

    def preprocess_image(self,
                         file_stream: BinaryIO,
                         binarize: bool,
                         sharpen: bool,
                         contrast_threshold: float) -> BinaryIO:
        """
        Preprocess image files to improve OCR accuracy.
        The input is a file stream, the output is a preprocessed image.
        """
        if file_stream is None:
            return None
        return self.file_preprocessor.preprocess_image(file_stream, binarize, sharpen, contrast_threshold)

    def extract_text(self, file_stream: BinaryIO) -> Document:
        """
        Extract text from the document using OCR, clean it, and detect gene variants.
        """
        document = self.ocr_extractor.extract_text(file_stream)
        document.cleaned_text = self.text_cleaner.clean_ocr_text(document.raw_text)
        document.keywords = self.gene_variant_detector.detect_mecp2_keywords(document.cleaned_text)

        # Validate what was the OCR confidence score of the detected keywords
        for keyword in document.keywords:
            confidence_value = document.find_word_confidence(keyword.value)
            if confidence_value is not None:
                logger.debug(f"Found {keyword} with confidence {confidence_value}")
                keyword.confidence = confidence_value
            else:
                logger.warning(f"{keyword} was not found")
                keyword.confidence = 0.0
        logger.debug(f"Mecp2 keyword confidence {document.keywords}")

        return document

    def summarize_and_correct(self,
                              document: Document) -> Document:
        """
        Summarize the text and correct it based on additional insights.
        Gets additional insights from Azure Healthcare Text Analytics.
        """
        # Summarize the text using OpenAI powered agent
        document.summary = self.openai_mutation_extractor.summarize_report(
            document_text=document.cleaned_text,
            keywords=document.dump_keywords())
        logger.debug(f"OpenAI summary: {document.summary}")

        # Analyze with Azure healthcare text analytics
        doc_analysis_result = self.health_analyzer.analyze_text(document.summary)
        document.text_analytics_result = self.health_analyzer.extract_variant_information(
            doc_analysis_result,
            confidence_threshold=0.0)
        logger.debug(f"TA4H: {document.text_analytics_result}")

        # Correct the summary with additional inputs from TA4H
        corrected_summary = self.openai_mutation_extractor.correct_summary_mistakes(
            document_text=document.summary,
            keywords=document.dump_keywords(),
            text_analytics=document.dump_text_analytics_keywords())
        logger.debug(f"Corrected summary: {corrected_summary}")
        return corrected_summary

    def extract_mutations(self,
                          document: Document,
                          min_confidence: float) -> List[GeneMutation]:
        """
        Extract mutations from the summary text and calculate confidence score.
        """
        # Extract mutations with OpenAI
        list_mutations = self.openai_mutation_extractor.extract_mutations(
            document_text=document.summary,
            mecp2_keywords=document.dump_keywords(),
            variant_list=document.dump_text_analytics_keywords()
        )
        # Calculate confidence score for each mutation
        list_mutations = self.mutation_filter.calculate_confidence_score(
            document_text=document.cleaned_text,
            mutations=list_mutations,
            mecp2_keywords=document.keywords,
            variant_list=document.text_analytics_result,
            base_conf_weight=20,
            keyword_weight=70,
            proximity_weight=10
        )
        # Final check, to filter mutations based on identified variants and keywords
        list_mutations = self.mutation_filter.filter_mutations(
            mutations=list_mutations,
            min_confidence=min_confidence
        )
        return list_mutations

    def fetch_gene_mutation_collection(self,
                                       list_mutations: List[GeneMutation]) -> List[GeneMutationCollection]:
        """
        Fetch detailed gene mutation data from EnsemblOrg.
        """
        mutation_details = []
        for mutation in list_mutations:
            try:
                # Fetch gene mutation details, with the different transcripts
                details = self.ensembl_org_service.get_gene_mutation_collection(
                    mutation.gene_transcript, mutation.gene_variation)
                # Update the confidence score of the mutation
                details.confidence = mutation.confidence
                details.gene_mutation.confidence = mutation.confidence
                details.protein_mutation.confidence = mutation.confidence
                # Add the mutation to the list
                mutation_details.append(details)
            except Exception as e:
                logger.error(f"Error fetching mutation details: {e}")
                raise ValueError(f"Error fetching mutation details: {e}")

        return mutation_details


    def analyze_document(self,
                         file_stream: BinaryIO,
                         min_confidence: float = 0.0) -> Tuple[Document, List[CoreGeneMutation]]:
        """
        Analyze a document end-to-end, the input is a file stream.
        The output is a list of CoreGeneMutation objects.
        """
        try:
            # Extract text from the document
            document = self.extract_text(file_stream)

            # Check if the document is a valid gene mutation report
            is_valid, confidence_score = self.openai_mutation_extractor.validate_document(document_text=document.cleaned_text)
            if not is_valid:
                logger.error(f"Document is not a valid gene mutation report. Confidence score: {confidence_score}")
                return None, []

            # Summarize and correct the text
            document.summary = self.summarize_and_correct(document)

            # Extract mutations from the summary
            list_mutations = self.extract_mutations(document, min_confidence)

            # Fetch detailed gene mutation data
            #list_mutations_with_all_transcripts = self.fetch_gene_mutation_collection(list_mutations)
            list_mutations_with_all_transcripts = []
            for mutation in list_mutations:
                mutation_hgvs = mutation.gene_transcript + ":" + mutation.gene_variation
                core_mutation = self.mutation_service.get_core_mutation(input_hgvs=mutation_hgvs)
                list_mutations_with_all_transcripts.append(core_mutation)

            logger.debug(f"List of mutations with all transcripts: {list_mutations_with_all_transcripts}")

            return document, list_mutations_with_all_transcripts

        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
