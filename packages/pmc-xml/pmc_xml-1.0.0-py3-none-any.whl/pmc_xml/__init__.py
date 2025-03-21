import json
from pathlib import Path

from pmc_xml.core.parser import PMC_XML_Parser


BASE_DIR = Path(__file__).resolve().parent
version_info = json.load(BASE_DIR.joinpath('version.json').open())

__version__ = version_info['version']
