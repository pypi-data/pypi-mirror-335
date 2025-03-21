# XML parser for PubMed Central (PMC) Database

## Installation
```bash
python3 -m pip install pmc_xml
```

## Usage

### CommandLine
```bash
pmc_xml --help

# parse single
pmc_xml PMC6039336

# parse batch
pmc_xml PMC6039336,PMC6031859,PMC6031856

# parse multiple
pmc_xml PMC6039336 PMC6031859 PMC6031856

# save file
pmc_xml PMC6039336,PMC6031859,PMC6031856 -o out.jl
```

### Python
```python
from pmc_xml import PMC_XML_Parser

pmc = PMC_XML_Parser()

for article in pmc.parse('PMC6039336,PMC6031859,PMC6031856'):
    print(article)        # Article<30003002>
    print(article.data)   # dict object
    print(article.to_json(indent=2))   # json string
    print(article.pmid, article.title, article.abstract) # by attribute
    print(article['pmid'], article['title'], article['abstract']) # by key
```
