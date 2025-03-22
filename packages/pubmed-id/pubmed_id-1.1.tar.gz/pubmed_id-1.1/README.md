# pubmed-id

Simple interface to query or scrape IDs from [PubMed](https://pubmed.ncbi.nlm.nih.gov/) (The US National Library of Medicine).

> This tool was originally developed to obtain temporal data for the well-known [PubMed graph dataset](https://github.com/nelsonaloysio/pubmed-temporal).

## Usage

### Command line interface

A CLI is included that allows querying the PubMed via their API or by web scraping.

```bash
usage: pubmed-id [-h] [-o OUTPUT_FILE] [-m {api,citedin,refs,scrape}]
                 [-w WORKERS] [-c SIZE] [--email ADDRESS] [--tool NAME]
                 [--quiet] [--log-level {critical,error,warning,info,debug}]
                 ID [ID ...]

positional arguments:
  ID                    IDs to query (separated by whitespaces).

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        File to write results to (default: 'PubMedAPI.json').
  -m {api,citedin,refs,scrape}, --method {api,citedin,refs,scrape}
                        Method to obtain data with (default: 'api').
  -w WORKERS, --max-workers WORKERS
                        Number of processes to use (optional).
  -c SIZE, --chunksize SIZE
                        Number of objects sent to each worker (optional).
  --email ADDRESS       Your e-mail address (required to query API only).
  --tool NAME           Tool name (optional, used to query API only).
  --quiet               Does not print results (limited to a single item only
                        by default).
  --log-level {critical,error,warning,info,debug}
                        Logging level (optional).
```

### Importing as a class

Quick example on how to obtain data from the API:

```python
>>> from pubmed_id import PubMedAPI
>>> api = PubMedAPI(email="myemail@domain.com", tool="MyToolName")
```

For more information on the API, please check the [official documentation](https://www.ncbi.nlm.nih.gov/home/develop/api/).


#### Obtain data from API

By default, the returned data is a dictionary with the PMCID, the PMID, and the DOI of a paper:

```python
>>> api(6798965)

{
  "pmcid": "PMC1163140",
  "pmid": "6798965",
  "doi": "10.1042/bj1970405"
}
```

Either an integer (PMID), a string (PMID or PMCID), or a list is accepted as input when calling the class directly.

**Note:** NCBI recommends that users post no more than three URL requests per second and limit large jobs to either weekends or between 9:00 PM and 5:00 AM Eastern time during weekdays. See more: [Usage Guidelines](https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen).

#### Scrape data from website

Scraping the PMID or PMICD instead returns more data (strings shortened for brevity):

```python
>>> api(6798965, method="scrape")

{
  "6798965": {
    "date": "1981 Aug 1",
    "title": "Characterization of N-glycosylated...",
    "abstract": "The N epsilon-glycosylation of...",
    "author_names": "A Le Pape;J P Muh;A J Bailey",
    "author_ids": "6798965;6798965;6798965",
    "doi": "PMC1163140",
    "pmid": "6798965"
  }
}
```

**Note**: some papers are unavailable from the API, but still return data when scraped, e.g., [PMID 15356126](https://pubmed.ncbi.nlm.nih.gov/15356126/).

#### Get paper references

Returns list of references from a paper:

```python
>>> api(6798965, method="refs")

{
  "6798965": [
    "7430347",
    "..."
  ]
}
```

#### Get citations for a paper

Returns list of citations to a paper:

```python
>>> api(6798965, method="citedin")

{
  "15356126": [
    "32868408",
    "..."
  ]
}
```

___

### References

* [PubMed API](https://www.ncbi.nlm.nih.gov/home/develop/api/)
