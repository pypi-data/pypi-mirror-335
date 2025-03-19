"""CA Leginfo API."""
from typing import Sequence, Mapping
import dataclasses
import requests
from bs4 import BeautifulSoup
import logging

from . import constants

logging.basicConfig(level=logging.DEBUG)

@dataclasses.dataclass
class BillRecord:
   """Container class for bill records, used by get_bill_list."""
   bill_id: str = None
   subject: str = None
   author: str = None
   status: str = None

@dataclasses.dataclass
class BillStatus:
   """Container class for bill status."""
   lead_author: str = None
   topic: str = None
   house_location: str = None
   last_amended: str = None
   committee_location: str = None
   history: list = dataclasses.field(default_factory=list)

class CALegInfoClient:
  """Client for interacting with CA Leginfo."""

  def __init__(self):
    """Initializes CALegInfoClient."""
  
  def get_bill_digest(self, bill_id: str):
    """Scrapes the bill digest from a bill.
    
    Args:
        bill_id: The bill ID including the session. e.g. 202320240AB1939

    Returns:
        The bill digest as a string, or None if not found.
    """
    bill_text_url = constants.BILL_TEXT_QUERY + bill_id
    try:
      response = requests.get(bill_text_url)
      response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
      soup = BeautifulSoup(response.content, "html.parser")
      digest = soup.find(id='digesttext')

      if digest:
        return digest.text.strip()
      else:
        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

  def get_bill_title(self, bill_id: str):
    """
    Scrapes the title of a bill from a given bill ID and session ID.

    Args:
        bill_id: The bill ID including the session. e.g. 202320240AB1939

    Returns:
        The bill title as a string, or None if not found.
    """
    bill_text_url = constants.BILL_TEXT_QUERY + bill_id
    logging.debug(bill_text_url)

    try:
        response = requests.get(bill_text_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        title_element = soup.select_one("#bill_header h1") # more robust selector.
        logging.debug(f"Title element parsed: {title_element}")

        if title_element:
            return title_element.text.strip()
        else:
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
  def get_bill_status(self, bill_id: str) -> BillStatus:
    """Returns author info, topic, last amended date, and history.
    
    Args:
      bill_id: The bill ID including the session. e.g. 202320240AB1939

    Returns:
      The bill title as a string, or None if not found.
    """
    bill_status_url = constants.BILL_STATUS_QUERY + bill_id
    logging.debug(bill_status_url)

    status = BillStatus()

    try:
      response = requests.get(bill_status_url)
      response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
      # Inspect https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202320240AB2071
      # For details if this breaks.
      soup = BeautifulSoup(response.content, "html.parser")
      lead_author = soup.find(id="leadAuthors")
      topic = soup.select_one(".statusCellData #subject")
      house_location = soup.find(id="houseLoc")
      last_amended = soup.select_one(".statusCellData #lastAction")
      committee_location = soup.select_one(".statusCellData #latest_commitee_location")
      bill_history = soup.find(id="billhistory")

      if lead_author:
         status.lead_author = lead_author.text.strip()
      if topic:
         status.topic = topic.text.strip()
      if house_location:
         status.house_location = house_location.text.strip()
      if last_amended:
         status.last_amended = last_amended.text.strip()
      if committee_location:
         status.committee_location = committee_location.text.strip()
      if bill_history:
         tbody = bill_history.find('tbody')
         history_rows = tbody.find_all('tr')
         for row in history_rows:
            cells = row.find_all('td')
            row_dict = {'date': cells[0].text.strip(), 'action': cells[1].text.strip()}
            status.history.append(row_dict)
    
      return status

    except requests.exceptions.RequestException as e:
      logging.error(f"Error fetching URL: {e}")
      return None
    except Exception as e:
      logging.error(f"An unexpected error occurred: {e}")
      return None

  def get_bill_list(self, session_id: str, filter: str) -> Sequence:
    """Get list of all bills for a session.
    
    Args:
      session_id: string representing the leg session e.g. 20252026
      filter: A string to filter on (remove bills containing.)
        e.g. "Budget Act" to skip boring budget act bills.
    
    Returns:
      A list of BillRecord containers.
    """
    bill_search_url = constants.BILL_SEARCH_QUERY + session_id
    bill_list = []
    try:
      response = requests.get(bill_search_url)
      response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
      soup = BeautifulSoup(response.content, 'html.parser')

      bill_table = soup.find(id='bill_results')
      tbody = bill_table.find('tbody')
      bill_rows = tbody.find_all('tr')

      for row in bill_rows:
        bill_record = BillRecord()
        cells = row.find_all('td')

        # Schema is measure, subject, author, status.
        measure = cells[0]
        measure_link = measure.find('a', href=True)
        bill_record.bill_id = measure_link['href'].split('=')[-1]
        bill_record.subject = cells[1].text.strip()
        bill_record.author = cells[2].text.strip()
        bill_record.status = cells[3].text.strip()

        # Append record if not filtered.
        if filter not in bill_record.subject:
          bill_list.append(bill_record)

      return bill_list

    except requests.exceptions.RequestException as e:
      logging.error(f"Error fetching URL: {e}")
      return None
    except Exception as e:
      logging.error(f"An unexpected error occurred: {e}")
      return None
