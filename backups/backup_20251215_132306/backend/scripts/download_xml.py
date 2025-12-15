"""
Enhanced XML download script with retry logic and proper error handling.
Downloads BOE XML documents with automatic retries on failure.
"""
import requests
import os
import sys
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

# Add script directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from boe_config import BOE_DOCUMENTS

# Add parent directory for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.paths import get_xml_dir
from app.utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def download_single_xml(url: str, output_path: str, slug: str) -> int:
    """
    Download a single XML file with retry logic.
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        slug: Company slug for logging
        
    Returns:
        Size of downloaded file in bytes
        
    Raises:
        requests.RequestException: If download fails after retries
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    logger.info(f"Downloading {slug} from {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    file_size = len(response.content)
    logger.info(f"Successfully saved {slug}.xml ({file_size} bytes)")
    
    return file_size

def download_all_xmls() -> Tuple[List[str], List[str]]:
    """
    Download all BOE XML documents.
    
    Returns:
        Tuple of (successful_downloads, failed_downloads)
    """
    xml_dir = get_xml_dir()
    os.makedirs(xml_dir, exist_ok=True)
    
    logger.info(f"Saving XMLs to {xml_dir}")
    logger.info(f"Processing {len(BOE_DOCUMENTS)} documents")
    
    successful = []
    failed = []
    
    for doc in BOE_DOCUMENTS:
        slug = doc['slug']
        boe_id = doc['boe_id']
        url = f"https://www.boe.es/diario_boe/xml.php?id={boe_id}"
        output_path = os.path.join(xml_dir, f"{slug}.xml")
        
        try:
            download_single_xml(url, output_path, slug)
            successful.append(slug)
        except RetryError as e:
            logger.error(f"Failed to download {slug} after retries: {e}")
            failed.append(slug)
        except Exception as e:
            logger.error(f"Unexpected error downloading {slug}: {e}")
            failed.append(slug)
    
    # Summary
    logger.info("="*60)
    logger.info(f"Download complete: {len(successful)} successful, {len(failed)} failed")
    
    if successful:
        logger.info(f"Successful: {', '.join(successful)}")
    
    if failed:
        logger.warning(f"Failed: {', '.join(failed)}")
        logger.warning("Failed downloads can be retried by running this script again")
    
    return successful, failed

if __name__ == "__main__":
    successful, failed = download_all_xmls()
    
    # Exit with error code if any downloads failed
    sys.exit(1 if failed else 0)
