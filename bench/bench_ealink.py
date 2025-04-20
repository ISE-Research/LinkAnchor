import os
import logging
import data_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def ensure_dataset_available():
    # Check if the dataset is already downloaded and extracted
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    # Check if `data_dir`/ealink directory exists
    if os.path.exists(os.path.join(data_dir, "ealink")):
        logger.info("EALink dataset already available.")
    else:
        data_gen.prepare_ealink_dataset()


ensure_dataset_available()
