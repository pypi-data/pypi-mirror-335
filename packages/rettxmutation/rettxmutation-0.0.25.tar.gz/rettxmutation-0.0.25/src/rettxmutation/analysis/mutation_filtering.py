import re
import math
import logging
from typing import List
from rettxmutation.analysis.models import GeneMutation, Keyword


logger = logging.getLogger(__name__)


class MutationFilter:

    def calc_keyword_confidence(
        self,
        mutation: GeneMutation,
        mecp2_keywords: List[Keyword],
        variant_list: List[Keyword]
    ) -> float:
        """
        Calculates confidence for a mutation based on:
        - presence of the variant in mecp2_keywords (type=variant_c),
        - presence of the variant in the variant_list,
        - presence of the transcript in mecp2_keywords (type=reference_sequence).
        The result is a value between 0.0 and 1.0.
        """

        transcript = mutation.gene_transcript
        variation = mutation.gene_variation

        logger.debug(f"[KeywordConfidence] Checking {mutation.to_hgvs_string()}")

        # We'll add contributions in steps
        confidence = 0.0

        # 1) Check if variation is in mecp2_keywords (variant_c)
        if any(k.value == variation and k.type == "variant_c" for k in mecp2_keywords):
            logger.debug("  => Found variation in mecp2_keywords (variant_c), +0.4")
            confidence += 0.4

        # 2) Check if variation is in known variant list
        if any(k.value == variation for k in variant_list):
            logger.debug("  => Found variation in variant_list, +0.4")
            confidence += 0.4

        # 3) Check if transcript is recognized in reference_sequences
        if any(k.value == transcript and k.type == "reference_sequence" for k in mecp2_keywords):
            logger.debug("  => Found transcript in mecp2_keywords (reference_sequence), +0.2")
            confidence += 0.2

        # Clamp to 1.0
        keyword_confidence = min(confidence, 1.0)

        logger.debug(f"[KeywordConfidence] Final => {keyword_confidence}")
        return keyword_confidence

    def calc_proximity_confidence(
        self,
        document_text: str,
        mutation: GeneMutation,
        alpha: float = 0.01,
        beta: float = 1.0
    ) -> float:
        """
        Calculates a proximity-based confidence for a mutation.
        Uses exponential decay for:
        1) absolute distance between transcript/variant (alpha),
        2) relative distance to transcript length (beta).
        Returns a confidence in the range [0..1].
        """
        # Extract transcript (without version number) and variation
        transcript = mutation.get_transcript()
        variation = mutation.gene_variation

        logger.debug(f"[ProximityConfidence] Checking {mutation.to_hgvs_string()}")

        # Default proximity confidence is 0.0
        proximity_conf = 0.0

        # Find the transcript in the document text
        transcript_pattern = re.escape(transcript) + r"(\.\d+)?\b"  # Match transcript with optional version
        transcript_match = re.search(transcript_pattern, document_text)
        if not transcript_match:
            logger.debug("  => Transcript not found in document_text; proximity=0.0")
            return 0.0  # No proximity confidence
        transcript_index = transcript_match.start()

        # Find the variation in the document text
        variation_index = document_text.find(variation)
        if variation_index == -1:
            logger.debug("  => Variation not found in document_text; proximity=0.0")
            return 0.0  # No proximity confidence

        # Distance is absolute difference between starting indexes
        distance = abs(transcript_index - variation_index)

        # Raw proximity from absolute distance
        raw_proximity = math.exp(-alpha * distance)

        # Relative distance based on transcript length
        relative_dist = distance / max(len(transcript), 1)
        transcript_factor = math.exp(-beta * relative_dist)

        # Combine the two
        combined = raw_proximity + transcript_factor

        # Clamp to [0..1]
        proximity_conf = min(combined, 1.0)

        logger.debug(
            f"[ProximityConfidence] distance={distance}, raw={raw_proximity:.4f}, "
            f"trans_factor={transcript_factor:.4f}, combined={proximity_conf:.4f}"
        )

        return proximity_conf

    def calculate_confidence_score(
        self,
        document_text: str,
        mutations: List[GeneMutation],
        mecp2_keywords: List[Keyword],
        variant_list: List[Keyword],
        base_conf_weight: int = 40,
        keyword_weight: int = 30,
        proximity_weight: int = 30,
        alpha: float = 0.01,
        beta: float = 1.0
    ) -> List[GeneMutation]:
        """
        Combines keyword_confidence and proximity_confidence into a final score.
        For each mutation:
        1) calculate keyword_conf  (via calc_keyword_confidence)
        2) calculate proximity_conf (via calc_proximity_confidence)
        3) final_conf = (keyword_weight * keyword_conf) + (proximity_weight * proximity_conf)
        Clamped to 1.0.

        Args:
            document_text (str): The cleaned text.
            mutations (List[GeneMutation]): List of GeneMutation objects.
            mecp2_keywords (List[Keyword]): Keywords for MECP2 gene transcripts/variations.
            variant_list (List[Keyword]): Known variant list data.
            keyword_weight (float): Weight for keyword-based confidence.
            proximity_weight (float): Weight for proximity-based confidence.
            alpha (float): Distance decay factor for absolute distance.
            beta (float): Distance decay factor for relative distance.

        Returns:
            List[GeneMutation]: The updated list of GeneMutation objects with final confidences.
        """
        logger.debug("Running consolidate_confidence with separate scoring methods...")

        updated_mutations = []

        # Validate weights, must sum to 100
        if base_conf_weight + keyword_weight + proximity_weight != 100:
            raise ValueError(f"Weights must sum to 100, got {base_conf_weight}, {keyword_weight}, {proximity_weight}")

        for mutation in mutations:
            # (A) Compute keyword-based confidence
            k_conf = self.calc_keyword_confidence(
                mutation=mutation,
                mecp2_keywords=mecp2_keywords,
                variant_list=variant_list)

            # (B) Compute proximity-based confidence
            p_conf = self.calc_proximity_confidence(
                document_text=document_text,
                mutation=mutation,
                alpha=alpha,
                beta=beta)

            # (C) Combine
            final_conf = (
                (base_conf_weight / 100 * mutation.confidence)
                + (keyword_weight / 100 * k_conf)
                + (proximity_weight / 100 * p_conf)
            )
            final_conf = min(final_conf, 100)

            # Update the mutation object
            mutation.confidence = round(final_conf, 2)

            logger.debug(
                f"[Consolidated] {mutation.to_hgvs_string()} => "
                f"keyword_conf={k_conf:.2f}, proximity_conf={p_conf:.2f}, "
                f"final={mutation.confidence:.2f}"
            )

            updated_mutations.append(mutation)

        logger.debug(f"Done. Processed {len(updated_mutations)} mutations.")
        return updated_mutations

    def filter_mutations(
        self,
        mutations: List[GeneMutation],
        min_confidence: float
    ) -> List[GeneMutation]:
        """
        1. If multiple mutations share the same variation (e.g. 'c.538C>T'), keep only the one with the highest confidence.
        2. Exclude all mutations with confidence < min_confidence.
        """
        logger.debug("Filtering mutations. Keeping duplicates with highest confidence, dropping below min_confidence.")

        # Dictionary to track the best mutation for each variation
        # Key: the gene_variation (e.g. "c.538C>T"), Value: GeneMutation object
        best_mutations = {}

        for mutation in mutations:
            var = mutation.gene_variation

            # If we haven't seen this variation before, store it
            if var not in best_mutations:
                logger.debug(f"Adding new variation: {var} with confidence {mutation.confidence}")
                best_mutations[var] = mutation
            else:
                # We have a duplicate variant, so keep the one with the highest confidence
                logger.debug(f"Duplicate variation: {var}")
                logger.debug(f"  => Current confidence: {mutation.confidence}")
                logger.debug(f"  => Best confidence: {best_mutations[var].confidence}")
                if mutation.confidence > best_mutations[var].confidence:
                    logger.debug(f"  => Replacing with higher confidence {mutation.confidence}")
                    best_mutations[var] = mutation

        # Now filter by min_confidence
        filtered_mutations = [
            m for m in best_mutations.values()
            if m.confidence >= min_confidence
        ]

        logger.debug(f"Filtered mutations: started with {len(mutations)}, "
                    f"kept {len(filtered_mutations)} after deduplication and confidence threshold.")
        return filtered_mutations
