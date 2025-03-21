"""Main funda scraper module"""

import argparse
import datetime
import json
import multiprocessing as mp
import os
from collections import OrderedDict
from typing import List, Optional, Dict
from urllib.parse import urlparse, urlunparse
import pickle

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from funda_monitor.config.core import config
from funda_monitor.preprocess import clean_date_format, preprocess_data
from funda_monitor.utils import logger, get_cookies, COOKIE_PATH


class FundaScraper(object):
    """
    A class used to scrape real estate data from the Funda website.
    """

    def __init__(
        self,
        area: str,
        want_to: str,
        page_start: int = 1,
        n_pages: int = 1,
        find_past: bool = False,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        days_since: Optional[int] = None,
        property_type: Optional[str] = None,
        min_floor_area: Optional[str] = None,
        max_floor_area: Optional[str] = None,
        sort: Optional[str] = None,
        previous_csv: Optional[str] = None,
    ):
        """

        :param area: The area to search for properties, formatted for URL compatibility.
        :param want_to: Specifies whether the user wants to buy or rent properties.
        :param page_start: The starting page number for the search.
        :param n_pages: The number of pages to scrape.
        :param find_past: Flag to indicate whether to find past listings.
        :param min_price: The minimum price for the property search.
        :param max_price: The maximum price for the property search.
        :param days_since: The maximum number of days since the listing was published.
        :param property_type: The type of property to search for.
        :param min_floor_area: The minimum floor area for the property search.
        :param max_floor_area: The maximum floor area for the property search.
        :param sort: The sorting criterion for the search results.
        """
        # Init attributes
        self.area = area.lower().replace(" ", "-")
        self.property_type = property_type
        self.want_to = want_to
        self.find_past = find_past
        self.page_start = max(page_start, 1)
        self.n_pages = max(n_pages, 1)
        self.page_end = self.page_start + self.n_pages - 1
        self.min_price = min_price
        self.max_price = max_price
        self.days_since = days_since
        self.min_floor_area = min_floor_area
        self.max_floor_area = max_floor_area
        self.sort = sort
        self.previous_csv = previous_csv
        self.existing_house_ids = set()

        # Instantiate along the way
        self.links: List[str] = []
        self.raw_df = pd.DataFrame()
        self.clean_df = pd.DataFrame()
        self.base_url = config.base_url
        self.selectors = config.css_selector

        # Load existing house IDs if previous CSV provided
        if self.previous_csv:
            self._load_existing_house_ids()

        # Get cookies
        try:
            with open(COOKIE_PATH.joinpath("cookies.pkl").__str__(), "rb") as file:
                self.cookies = pickle.load(file)
        except FileNotFoundError:
            self.cookies = get_cookies()
        
        self.requests_session = self._get_requests_session(self.cookies)


    def __repr__(self):
        return (
            f"FundaScraper(area={self.area}, "
            f"want_to={self.want_to}, "
            f"n_pages={self.n_pages}, "
            f"page_start={self.page_start}, "
            f"find_past={self.find_past}, "
            f"min_price={self.min_price}, "
            f"max_price={self.max_price}, "
            f"days_since={self.days_since}, "
            f"min_floor_area={self.min_floor_area}, "
            f"max_floor_area={self.max_floor_area}, "
            f"find_past={self.find_past})"
            f"min_price={self.min_price})"
            f"max_price={self.max_price})"
            f"days_since={self.days_since})"
            f"sort={self.sort})"
        )

    @property
    def to_buy(self) -> bool:
        """Determines if the search is for buying or renting properties."""
        if self.want_to.lower() in ["buy", "koop", "b", "k"]:
            return True
        elif self.want_to.lower() in ["rent", "huur", "r", "h"]:
            return False
        else:
            raise ValueError("'want_to' must be either 'buy' or 'rent'.")

    @property
    def check_days_since(self) -> int:
        """Validates the 'days_since' attribute."""
        if self.find_past:
            raise ValueError("'days_since' can only be specified when find_past=False.")

        if self.days_since in [None, 1, 3, 5, 10, 30]:
            return self.days_since
        else:
            raise ValueError("'days_since' must be either None, 1, 3, 5, 10 or 30.")

    @property
    def check_sort(self) -> str:
        """Validates the 'sort' attribute."""
        if self.sort in [
            None,
            "relevancy",
            "date_down",
            "date_up",
            "price_up",
            "price_down",
            "floor_area_down",
            "plot_area_down",
            "city_up" "postal_code_up",
        ]:
            return self.sort
        else:
            raise ValueError(
                "'sort' must be either None, 'relevancy', 'date_down', 'date_up', 'price_up', 'price_down', "
                "'floor_area_down', 'plot_area_down', 'city_up' or 'postal_code_up'. "
            )

    @staticmethod
    def _check_dir(base_dir: str = "data") -> None:
        """Ensures the existence of the directory for storing data.
        
        Args:
            base_dir: Base directory to create if it doesn't exist
        """
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            logger.info(f"Created directory: {base_dir}")

    @staticmethod
    def _create_run_dir() -> str:
        """Creates a new directory for the current scraping run using timestamp.
        
        Returns:
            Path to the created run directory
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join("data", f"run_{timestamp}")
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            os.makedirs(os.path.join(run_dir, "html"))
            logger.info(f"Created run directory: {run_dir}")
        return run_dir

    @staticmethod
    def _get_requests_session(cookies : List[Dict]) -> requests.Session:
        """Return a request session instance with given cookies."""
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(
                cookie["name"], 
                cookie["value"], 
                domain=cookie["domain"], 
                path=cookie["path"])
        return session 
    
    
    def _get_links_from_one_parent(self, url: str) -> List[str]:
        """Scrapes all available property links from a single Funda search page."""
        response = self.requests_session.get(url, headers=config.header)
        soup = BeautifulSoup(response.text, "lxml")

        script_tag = soup.find_all("script", {"type": "application/ld+json"})[0]
        json_data = json.loads(script_tag.contents[0])
        urls = [item["url"] for item in json_data["itemListElement"]]
        return urls

    def reset(
        self,
        area: Optional[str] = None,
        property_type: Optional[str] = None,
        want_to: Optional[str] = None,
        page_start: Optional[int] = None,
        n_pages: Optional[int] = None,
        find_past: Optional[bool] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        days_since: Optional[int] = None,
        min_floor_area: Optional[str] = None,
        max_floor_area: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> None:
        """Resets or initializes the search parameters."""
        if area is not None:
            self.area = area
        if property_type is not None:
            self.property_type = property_type
        if want_to is not None:
            self.want_to = want_to
        if page_start is not None:
            self.page_start = max(page_start, 1)
        if n_pages is not None:
            self.n_pages = max(n_pages, 1)
        if find_past is not None:
            self.find_past = find_past
        if min_price is not None:
            self.min_price = min_price
        if max_price is not None:
            self.max_price = max_price
        if days_since is not None:
            self.days_since = days_since
        if min_floor_area is not None:
            self.min_floor_area = min_floor_area
        if max_floor_area is not None:
            self.max_floor_area = max_floor_area
        if sort is not None:
            self.sort = sort

    @staticmethod
    def remove_duplicates(lst: List[str]) -> List[str]:
        """Removes duplicate links from a list."""
        return list(OrderedDict.fromkeys(lst))
    
    @staticmethod
    def remove_link_overlap(first_url : str, second_url : str, delimeter : str = "/") -> str:
        """Removes the overlapping part in a 2 links and return their concat.
        
            :example:
            >>> remove_overlap("funda/en", "/en/something/something")
            'funda/en/something/something'
        """

        first_url = first_url.split(delimeter)
        second_url = second_url.split(delimeter)

        for _, path in enumerate(reversed(first_url)):
            try:
                second_url.remove(path)
            except Exception:
                continue
        
        return delimeter.join(first_url + second_url)

    @staticmethod
    def fix_link(link: str) -> str:
        """Fixes a given property link to ensure proper URL formatting."""
        # link_url = urlparse(link)
        # link_path = link_url.path.split("/")
        # property_id = link_path.pop(5)
        # property_address = link_path.pop(4).split("-")
        # link_path = link_path[2:4]
        # property_address.insert(1, property_id)
        # link_path.extend(["-".join(property_address), "?old_ldp=true"])
        # fixed_link = urlunparse(
            # (link_url.scheme, link_url.netloc, "/".join(link_path), "", "", "")
        # )
        return link + "?old_ldp=true"

    def _load_existing_house_ids(self) -> None:
        """Load house IDs from a previous CSV file to skip already scraped houses."""
        try:
            df = pd.read_csv(self.previous_csv)
            if 'house_id' not in df.columns:
                logger.warning(f"No 'house_id' column found in {self.previous_csv}")
                return
            self.existing_house_ids = set(df['house_id'].astype(str))
            logger.info(f"Loaded {len(self.existing_house_ids)} existing house IDs from {self.previous_csv}")
        except FileNotFoundError:
            logger.warning(f"Previous CSV file not found: {self.previous_csv}")
        except Exception as e:
            logger.error(f"Error loading previous CSV: {str(e)}")

    def _extract_house_id(self, url: str) -> str:
        """Extract house ID from a Funda URL."""
        try:
            return url.split("/")[-2].split("-")[-1]
        except (IndexError, AttributeError):
            return ""

    def fetch_all_links(self, page_start: int = None, n_pages: int = None) -> None:
        """Collects all available property links across multiple pages."""

        page_start = self.page_start if page_start is None else page_start
        n_pages = self.n_pages if n_pages is None else n_pages

        logger.info("*** Phase 1: Fetch all the available links from all pages *** ")
        urls = []
        main_url = self._build_main_query_url()

        for i in tqdm(range(page_start, page_start + n_pages)):
            try:
                item_list = self._get_links_from_one_parent(
                    f"{main_url}&search_result={i}"
                )
                urls += item_list
            except IndexError:
                self.page_end = i
                logger.info(f"*** The last available page is {self.page_end} ***")
                break

        urls = self.remove_duplicates(urls)
        
        # Filter out URLs with existing house IDs
        if self.existing_house_ids:
            filtered_urls = []
            skipped_count = 0
            for url in urls:
                house_id = self._extract_house_id(url)
                if house_id not in self.existing_house_ids:
                    filtered_urls.append(url)
                else:
                    skipped_count += 1
            urls = filtered_urls
            logger.info(f"Skipped {skipped_count} already scraped houses")

        fixed_urls = [self.fix_link(url) for url in urls]

        logger.info(
            f"*** Got all the urls. {len(fixed_urls)} houses found from {self.page_start} to {self.page_end} ***"
        )
        self.links = fixed_urls

    def _build_main_query_url(self) -> str:
        """Constructs the main query URL for the search."""
        query = "koop" if self.to_buy else "huur"

        main_url = (
            f"{self.base_url}/zoeken/{query}?selected_area=%5B%22{self.area}%22%5D"
        )

        if self.property_type:
            property_types = self.property_type.split(",")
            formatted_property_types = [
                "%22" + prop_type + "%22" for prop_type in property_types
            ]
            main_url += f"&object_type=%5B{','.join(formatted_property_types)}%5D"

        if self.find_past:
            main_url = f'{main_url}&availability=%5B"unavailable"%5D'

        if self.min_price is not None or self.max_price is not None:
            min_price = "" if self.min_price is None else self.min_price
            max_price = "" if self.max_price is None else self.max_price
            main_url = f"{main_url}&price=%22{min_price}-{max_price}%22"

        if self.days_since is not None:
            main_url = f"{main_url}&publication_date={self.check_days_since}"

        if self.min_floor_area or self.max_floor_area:
            min_floor_area = "" if self.min_floor_area is None else self.min_floor_area
            max_floor_area = "" if self.max_floor_area is None else self.max_floor_area
            main_url = f"{main_url}&floor_area=%22{min_floor_area}-{max_floor_area}%22"

        if self.sort is not None:
            main_url = f"{main_url}&sort=%22{self.check_sort}%22"

        logger.info(f"*** Main URL: {main_url} ***")
        return main_url

    @staticmethod
    def get_value_from_css(soup: BeautifulSoup, selector: str) -> str:
        """Extracts data from HTML using a CSS selector."""
        result = soup.select(selector)
        if len(result) > 0:
            result = result[0].text
        else:
            result = "na"
        return result

    def scrape_one_link(self, link_with_index: tuple) -> List[str]:
        """Scrapes data from a single property link."""
        index, link = link_with_index  # Unpack the tuple correctly (enumerate gives (index, item))
        logger.info(f"Scraping link {index + 1}: {link}")

        try:
            # Initialize for each page
            response = self.requests_session.get(link, headers=config.header)
            logger.debug(f"Response status code: {response.status_code}")

            # Save HTML content with sequential numbering
            html_path = os.path.join(self.current_run_dir, "html", f"{index + 1}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.debug(f"Saved HTML content to: {html_path}")
            logger.debug(f"Successfully scraped listing #{index + 1}")

            soup = BeautifulSoup(response.text, "lxml")
            # Log HTML content for CSS selector debugging
            logger.debug("HTML content for CSS selectors:")
            logger.debug(response.text)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch or save content for {link}: {str(e)}")
            return ["na"] * 28  # Return empty data for all fields

        # Get the value according to respective CSS selectors
        if self.to_buy:
            if self.find_past:
                list_since_selector = self.selectors.date_list
            else:
                list_since_selector = self.selectors.listed_since
        else:
            if self.find_past:
                list_since_selector = ".fd-align-items-center:nth-child(9) span"
            else:
                list_since_selector = ".fd-align-items-center:nth-child(7) span"

        raw_price = self.get_value_from_css(soup, self.selectors.price)
        
        result = [
            link,
            raw_price,
            self.get_value_from_css(soup, self.selectors.address),
            self.get_value_from_css(soup, self.selectors.descrip),
            self.get_value_from_css(soup, list_since_selector),
            self.get_value_from_css(soup, self.selectors.zip_code),
            self.get_value_from_css(soup, self.selectors.size),
            self.get_value_from_css(soup, self.selectors.year),
            self.get_value_from_css(soup, self.selectors.living_area),
            self.get_value_from_css(soup, self.selectors.kind_of_house),
            self.get_value_from_css(soup, self.selectors.building_type),
            self.get_value_from_css(soup, self.selectors.num_of_rooms),
            self.get_value_from_css(soup, self.selectors.num_of_bathrooms),
            self.get_value_from_css(soup, self.selectors.layout),
            self.get_value_from_css(soup, self.selectors.energy_label),
            self.get_value_from_css(soup, self.selectors.insulation),
            self.get_value_from_css(soup, self.selectors.heating),
            self.get_value_from_css(soup, self.selectors.ownership),
            self.get_value_from_css(soup, self.selectors.exteriors),
            self.get_value_from_css(soup, self.selectors.parking),
            self.get_value_from_css(soup, self.selectors.neighborhood_name),
            self.get_value_from_css(soup, self.selectors.date_list),
            self.get_value_from_css(soup, self.selectors.date_sold),
            self.get_value_from_css(soup, self.selectors.term),
            self.get_value_from_css(soup, self.selectors.price_sold),
            self.get_value_from_css(soup, self.selectors.last_ask_price),
            self.get_value_from_css(soup, self.selectors.last_ask_price_m2).split("\r")[
                0
            ],
        ]

        # Deal with list_since_selector especially, since its CSS varies sometimes
        if clean_date_format(result[4]) == "na":
            for i in range(6, 16):
                selector = f".fd-align-items-center:nth-child({i}) span"
                update_list_since = self.get_value_from_css(soup, selector)
                if clean_date_format(update_list_since) == "na":
                    pass
                else:
                    result[4] = update_list_since

        # Fix link 
        photos_link = self.remove_link_overlap(
            self.base_url,
            soup.select(self.selectors.photo)[0].get("href") 
        )

        # Clean up the retried result from one page
        result = [r.replace("\n", "").replace("\r", "").strip() for r in result]
        result.append(photos_link)
        return result

    def scrape_pages(self) -> None:
        """Scrapes data from all collected property links."""

        logger.info("*** Phase 2: Start scraping from individual links ***")
        logger.info(f"Total links to scrape: {len(self.links)}")

        # Create run directory at the start
        self.current_run_dir = self._create_run_dir()
        logger.info(f"Created run directory for this session: {self.current_run_dir}")

        df = pd.DataFrame({key: [] for key in self.selectors.keys()})
        logger.debug("Initialized empty DataFrame with selector keys")

        # Scrape pages with multiprocessing to improve efficiency
        # TODO: use asyncio instead
        pools = mp.cpu_count()
        logger.info(f"Using {pools} CPU cores for parallel scraping")
        # Create list of tuples with (link, index) for sequential numbering
        links_with_index = list(enumerate(self.links))
        content = process_map(self.scrape_one_link, links_with_index, max_workers=pools)
        logger.info("Completed parallel scraping of all links")

        for i, c in enumerate(content):
            df.loc[len(df)] = c

        # Extract city safely with error handling
        def extract_city(url):
            try:
                return url.split("/")[6] if url != "na" else "na"
            except (IndexError, AttributeError):
                return "na"
                
        df["city"] = df["url"].map(extract_city)
        df["log_id"] = datetime.datetime.now().strftime("%Y%m-%d%H-%M%S")
        if not self.find_past:
            df = df.drop(["term", "price_sold", "date_sold"], axis=1)
        logger.info(f"*** All scraping done: {df.shape[0]} results ***")
        self.raw_df = df

    def save_csv(self, df: pd.DataFrame, filepath: str = None) -> None:
        """Saves the scraped data to a CSV file."""
        if filepath is None:
            self._check_dir()
            date = str(datetime.datetime.now().date()).replace("-", "")
            status = "unavailable" if self.find_past else "unavailable"
            want_to = "buy" if self.to_buy else "rent"
            filepath = f"./data/houseprice_{date}_{self.area}_{want_to}_{status}_{len(self.links)}.csv"
        
        # Add scrape_date column at the beginning
        df = df.copy()  # Create a copy to avoid modifying the original DataFrame
        scrape_date = datetime.datetime.now().strftime("%Y-%m-%d")
        df.insert(0, 'scrape_date', scrape_date)
        
        df.to_csv(filepath, index=False)
        logger.info(f"*** File saved: {filepath}. ***")

    def run(
        self, raw_data: bool = False, save: bool = False, filepath: str = None
    ) -> pd.DataFrame:
        """
        Runs the full scraping process, optionally saving the results to a CSV file.

        :param raw_data: if true, the data won't be pre-processed
        :param save: if true, the data will be saved as a csv file
        :param filepath: the name for the file
        :return: the (pre-processed) dataframe from scraping
        """
        logger.info("=== Starting Funda Scraper ===")
        logger.info(f"Area: {self.area}")
        logger.info(f"Type: {'Buy' if self.to_buy else 'Rent'}")
        logger.info(f"Pages: {self.page_start} to {self.page_start + self.n_pages - 1}")
        
        # Phase 1: Fetch links
        self.fetch_all_links()
        
        # Phase 2: Scrape individual pages
        self.scrape_pages()
        logger.info(f"Total properties scraped: {len(self.raw_df)}")

        # Phase 3: Process data
        if raw_data:
            logger.info("Using raw data without preprocessing")
            df = self.raw_df
        else:
            logger.info("\n=== Phase 3: Cleaning and preprocessing data ===\n")
            df = preprocess_data(df=self.raw_df, is_past=self.find_past)
            self.clean_df = df
            logger.info(f"Final dataset shape: {df.shape}\n")

        # Phase 4: Save results
        if save:
            logger.info("=== Phase 4: Saving results ===")
            self.save_csv(df, filepath)

        logger.info("=== Scraping process completed successfully ===")
        return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--area",
        type=str,
        help="Specify which area you are looking for",
        default="amsterdam",
    )
    parser.add_argument(
        "--want_to",
        type=str,
        help="Specify you want to 'rent' or 'buy'",
        default="rent",
        choices=["rent", "buy"],
    )
    parser.add_argument(
        "--find_past",
        action="store_true",
        help="Indicate whether you want to use historical data",
    )
    parser.add_argument(
        "--previous_csv",
        type=str,
        help="Path to previous CSV file to skip already scraped houses",
        default=None,
    )
    parser.add_argument(
        "--page_start", type=int, help="Specify which page to start scraping", default=1
    )
    parser.add_argument(
        "--n_pages", type=int, help="Specify how many pages to scrape", default=1
    )
    parser.add_argument(
        "--min_price", type=int, help="Specify the min price", default=None
    )
    parser.add_argument(
        "--max_price", type=int, help="Specify the max price", default=None
    )
    parser.add_argument(
        "--days_since",
        type=int,
        help="Specify the days since publication",
        default=None,
    )
    parser.add_argument(
        "--sort",
        type=str,
        help="Specify sorting",
        default=None,
        choices=[
            None,
            "relevancy",
            "date_down",
            "date_up",
            "price_up",
            "price_down",
            "floor_area_down",
            "plot_area_down",
            "city_up" "postal_code_up",
        ],
    )
    parser.add_argument(
        "--raw_data",
        action="store_true",
        help="Indicate whether you want the raw scraping result",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Indicate whether you want to save the data",
    )

    args = parser.parse_args()
    scraper = FundaScraper(
        area=args.area,
        want_to=args.want_to,
        find_past=args.find_past,
        page_start=args.page_start,
        n_pages=args.n_pages,
        min_price=args.min_price,
        max_price=args.max_price,
        days_since=args.days_since,
        sort=args.sort,
        previous_csv=args.previous_csv,
    )
    df = scraper.run(raw_data=args.raw_data, save=args.save)
    print(df.head())
