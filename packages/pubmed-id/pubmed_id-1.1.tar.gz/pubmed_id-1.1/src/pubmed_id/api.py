import logging as log
from functools import partial, wraps
from requests import Response, Session
from time import sleep
from typing import Callable, Optional, Union

from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import process_map

URL = "ncbi.nlm.nih.gov"
API_ENDPOINT = "pmc/utils/idconv/v1.0"
API_CITATIONS = "entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed"
METHODS = ["api", "citedin", "refs", "scrape"]


def souper(func: Callable) -> Callable:
    """
    Decorator function to scrape data with BeautifulSoup.
    """
    @wraps(func)
    @staticmethod
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return func_wrapper


class PubMedAPI():
    """
    PubMed class to obtain data from PubMed ID(s) using the API or scraping.

    :param email: E-mail address to query the API.
    :param tool: Tool name to query the API.
    """
    def __init__(
        self,
        email: str = "",
        tool: str = "PubMedAPI",
        log_format: Optional[str] = None,
        log_level: Optional[str] = None,
    ) -> None:
        self.email = email
        self.tool = tool

        if log_level:
            log.basicConfig(format=log_format or "%(asctime)s - %(levelname)s - %(message)s",
                            level=getattr(log, log_level.upper()))

        self._session = Session()

    def __call__(
        self,
        ids: Union[str, int, list],
        method: str = "api",
        max_workers: Optional[int] = None,
        chunksize: Optional[int] = None,
        **kwargs
    ) -> list:
        """
        Multiprocessing wrapper for the `api`, `citedin`, `refs`, and `scrape` methods.

        :param ids: List of PubMed IDs.
        :param method: Method to use to obtain data.
        :param max_workers: Number of workers to use.
        :param chunksize: Number of IDs to process at a time.
        :param kwargs: Additional keyword arguments for the method.
        """
        assert ids is not None and type(ids) in (str, int, list),\
            "Argument `ids` must be a non-empty string, integer, or list."

        assert method in METHODS,\
            f"Argument `method` must be one in {METHODS}."

        assert max_workers is None or (type(max_workers) == int and max_workers > 0),\
            "Argument `max_workers` must be a positive integer if defined."

        assert chunksize is None or (type(chunksize) == int and chunksize > 0),\
            "Argument `chunksize` must be a positive integer if defined."

        if type(ids) in (str, int):
            return getattr(self, method)(ids, **kwargs)

        max_workers = max_workers or 1

        if not chunksize:
            chunksize = max(len(ids) // (max_workers + 2), 1) if max_workers > 1 else 1

        if len(ids) > chunksize:
            data = list(process_map(partial(getattr(self, method), **kwargs),
                                    ids,
                                    ascii=True,
                                    max_workers=max_workers,
                                    chunksize=chunksize,
                                    total=len(ids),
                                    desc=f"Requesting data (workers: {max_workers}, "
                                        f"chunksize: {chunksize})"))
        else:
            data = [getattr(self, method)(id, **kwargs) for id in ids]

        if method == "api":
            return data

        return {id: data[i] for i, id in enumerate(ids)}

    def api(
        self,
        ids: Union[str, int, list],
        idtype: Optional[str] = None,
        versions: str = "no",
        batchsize: int = 100
    ) -> Union[dict, list]:
        """
        Obtain data from PubMed ID(s) using the API.

        Returns a dictionary if `ids` is a string or integer;
        otherwise, returns a list of dictionaries indexed by id.

        **Warning**: the returned results are NOT ordered!

        :param ids: PubMed ID(s) to obtain data from.
        :param idtype: Type of ID to use for the query.
            Choosing 'pmcid' equals prefixing 'PMC' to input IDs.
        :param versions: Include versions of the article.
        :param batchsize: Number of IDs to process at a time.
        """
        assert idtype in (None, "pmid", "pmcid"),\
            "Argument `idtype` must be either 'pmid' or 'pmcid' if defined."
        assert versions in ("no", "yes"),\
            "Argument `versions` must be either 'no' or 'yes'."

        if not self.email or any(_ not in self.email for _ in ("@", ".")):
            raise ValueError("Please provide a valid e-mail address to query the API.")

        records = []

        for batch in (range(1) if isinstance(ids, (str, int)) else range(0, len(ids), batchsize)):
            url = f"https://{URL}/{API_ENDPOINT}/?"\
                  f"&tool={self.tool}"\
                  f"&email={self.email}"\
                  f"&format=json"\
                  f"&versions={versions}"\
                  f"{f'&idtype={idtype}' if idtype else ''}"\
                  f"&ids={','.join([f'{id}' for id in ([ids] if isinstance(ids, (str, int)) else list(ids)[batch:batch+batchsize])])}"

            r = self._request(url)

            if r is not None and r.status_code == 200:
                records += r.json()["records"]

        if type(ids) in (str, int):
            return records[0] if records else None

        return records

    def citedin(self, id: Union[str, int]) -> list:
        """
        Returns list of PubMed IDs that the given PubMed ID is cited in.

        See [reference](https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/).

        :param id: PubMed ID to obtain data from.
        """
        url = f"https://eutils.{URL}/"\
              f"{API_CITATIONS}_citedin"\
              f"&format=json"\
              f"&id={id}"

        r = self._request(url)

        if r is not None and r.status_code == 200:
            return (r.json()["linksets"] or [{}])[0].get("linksetdbs", [{"links": []}])[0]["links"]

        log.debug(f"Failed to obtain data for PubMed ID: {id}")
        return []

    def refs(self, id: Union[str, int]) -> list:
        """
        Returns list of PubMed IDs that the given PubMed ID references.

        See [reference](https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/).

        :param id: PubMed ID to obtain data from.
        """
        url = f"https://eutils.{URL}/"\
              f"{API_CITATIONS}_refs"\
              f"&format=json"\
              f"&id={id}"

        r = self._request(url)

        if r is not None and r.status_code == 200:
            return (r.json()["linksets"] or [{}])[0].get("linksetdbs", [{"links": []}])[0]["links"]

        log.debug(f"Failed to obtain data for PubMed ID: {id}")
        return []

    def scrape(self, id: Union[str, int]) -> dict:
        """
        Returns data from PubMed ID via scraping. Note that
        an empty dictionary is returned if the request fails.

        :param id: PubMed ID to obtain data from.
        """
        fields = ["date", "title", "abstract", "author_names", "author_ids", "doi", "pmid"]
        r = self._request(f"https://pubmed.{URL}/{id}/")

        if r is not None and r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            return {field: getattr(self, f"_scrape_{field}")(soup) for field in fields}

        log.debug(f"Failed to obtain data for PubMed ID: {id}")
        return {}

    def _request(
        self,
        url: str,
        timeout: Optional[int] = 60,
        max_retries: Optional[int] = 5,
        interval_on_error: Optional[int] = 1
    ) -> Response:
        """
        Request data from URL.

        :param url: URL to request data from.
        :param timeout: Timeout for the request.
        :param max_retries: Maximum number of retries.
        :param interval_on_error: Interval to wait on error.
        """
        retries = 0
        while retries < (max_retries or 1):
            try:
                r = self._session.get(url, timeout=timeout)
                if r.status_code == 200:
                    return r
            except Exception as e:
                log.debug(f"{e} ({retries}/{max_retries}): {url}")
                sleep(interval_on_error or 0)
            retries += 1

    @souper
    def _scrape_date(soup):
        return soup.find("span", {"class": "cit"}).text.strip().split(":")[0].split(";")[0]

    @souper
    def _scrape_title(soup):
        return soup.find("h1", {"class": "heading-title"}).text.strip()

    @souper
    def _scrape_abstract(soup):
        return soup.find("div", {"class": "abstract-content selected"}).find("p").text.strip()

    @souper
    def _scrape_author_names(soup):
        return ";".join([
            a.text for a in
            soup.find("div", {"class": "authors-list"}).find_all("a", {"class": "full-name"})]
        )

    @souper
    def _scrape_author_ids(soup):
        return ";".join([
            a["href"].split("author_id=")[-1] for a in
            soup.find("div", {"class": "authors-list"}).find_all("a", {"class": "full-name"})
        ])

    @souper
    def _scrape_doi(soup):
        return soup.find("ul", {"class": "identifiers"}).find("a", {"class": "id-link"}).text.strip()

    @souper
    def _scrape_pmid(soup):
        return soup.find("ul", {"class": "identifiers"}).find("strong").text.strip()
