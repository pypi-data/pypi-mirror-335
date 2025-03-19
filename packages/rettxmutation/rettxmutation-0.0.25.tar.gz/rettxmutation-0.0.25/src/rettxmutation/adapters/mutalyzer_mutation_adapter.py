# File: adapters/mutalyzer_mutation_adapter.py
import requests
import logging
import backoff
from typing import Dict

logger = logging.getLogger(__name__)

class MutationMappingError(Exception):
    """Raised when mapping a mutation fails."""
    pass

class MutationNormalizationError(Exception):
    """Raised when normalization of a mutation fails."""
    pass

class MutalyzerMutationAdapter():
    """
    Concrete implementation of IMutationService using the Mutalyzer API.

    This class implements:
      - map_mutation(description: str, target_transcript: str) -> str
      - normalize_mutation(description: str) -> Dict
    """
    def __init__(self,
                 target_assembly: str = "GRCH38",
                 map_base_url: str = "https://mutalyzer.nl/api/map/",
                 norm_base_url: str = "https://mutalyzer.nl/api/normalize/"):
        self.target_assembly = target_assembly
        self.MAP_BASE_URL = map_base_url
        self.NORM_BASE_URL = norm_base_url
        self.session = requests.Session()

    def close(self):
        """Close the underlying session."""
        self.session.close()

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_tries=5,
    )
    def map_mutation(self, description: str, target_transcript: str) -> str:
        """
        Map the input HGVS mutation to the target transcript using Mutalyzer's map API.
        
        Parameters:
            description (str): The input HGVS mutation (e.g., "NM_001110792.2:c.952C>T").
            target_transcript (str): The target transcript (e.g., "NM_004992.4").
        
        Returns:
            str: The mapped HGVS mutation on the target transcript.
        
        Raises:
            MutationMappingError: If mapping fails or no result is returned.
        """
        url = f"{self.MAP_BASE_URL}?description={description}&reference_id={target_transcript}&filter=true"
        logger.debug(f"Mapping mutation via URL: {url}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            mapped = data.get("mapped_description", "")
            if not mapped:
                raise MutationMappingError(f"No mapped description for {description} to {target_transcript}")
            logger.debug(f"Mapped description: {mapped}")
            return mapped
        except Exception as e:
            logger.error(f"Error mapping mutation {description} to {target_transcript}: {e}")
            raise MutationMappingError(f"Error mapping mutation {description} to {target_transcript}") from e

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_tries=5,
    )
    def normalize_mutation(self, description: str) -> Dict:
        """
        Normalize the mutation using Mutalyzer's normalization endpoint.
        
        Parameters:
            description (str): The input HGVS mutation string.
        
        Returns:
            dict: The JSON response from Mutalyzer containing normalized mutation details.
        
        Raises:
            MutationNormalizationError: If normalization fails or returns an empty response.
        """
        url = f"{self.NORM_BASE_URL}{description}"
        logger.debug(f"Normalizing mutation via URL: {url}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            norm_data = response.json()
            if not norm_data:
                raise MutationNormalizationError(f"Empty normalization data for {description}")
            logger.debug(f"Normalization data: {norm_data}")
            return norm_data
        except Exception as e:
            logger.error(f"Error normalizing mutation {description}: {e}")
            raise MutationNormalizationError(f"Error normalizing mutation {description}") from e
