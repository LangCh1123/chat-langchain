import os
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from langchain.tools import tool

from croptalk.load_data import SOB

load_dotenv("secrets/.env.secret")


@tool("get-SOB-metrics")
def get_sob_metrics_for_crop_county(state_abbreviation: Optional[str] = None,
                                    county_name: Optional[str] = None,
                                    commodity_name: Optional[str] = None,
                                    insurance_plan_name: Optional[str] = None,
                                    metric: Optional[str] = None,
                                    coverage_level: Optional[float] = None) -> str:
    """
    This tool is used to query the summary of business data (SOB) to retrieve insurance program metrics by coverage level.
    If the arguments are not available, set them as "None".

    Args:
        state_abbreviation: two letter string of State abbreviation (California -> CA, North Dakota -> ND and so on)
        county_name: name of county provided
        commodity_name: name of commodity
        insurance_plan_name: provided plan name abbreviation
        metric : choice from ["pct_liability_indemnified", "cost_to_grower", "policies_sold_count", "premium_per_quantity"]
        coverage_level : choice between [0.5, 0.65, 0.7, 0.75, 0.8]

    Returns: the tool returns a string which gives the coverage level with their
            associated percentage indemnified statistic

    """

    sob = SOB[SOB["commodity_year"] == 2023]

    if commodity_name is not None:
        commodity_name = commodity_name.lower()

    filters = {
        "state_abbreviation": state_abbreviation,
        "county_name": county_name,
        "insurance_plan_name_abbreviation": insurance_plan_name,
        "commodity_name": commodity_name,
        "coverage_level": coverage_level
    }

    # Create a boolean mask
    mask = pd.Series(True, index=sob.index)

    for column, value in filters.items():
        if value is not None:
            mask = mask & (sob[column] == value)

    sob = sob[mask]

    # run a validation for arguments.

    # aggregation step on the filter that are provided
    # this should be customized based on the request

    # sum or a mean
    # this should be customized based on the request

    if not sob.empty:

        # todo improve this text
        filter_values = ""
        for column, filter in filters.items():
            if filter is not None:
                filter_values += f"{column} = {filter} "
        response = f"In 2023, we observe the following data for {filter_values}:\b "
        if metric == "policies_sold_count":
            response += f"Total of {metric}: {sob[metric].sum()}"
        else:
            weighted_mean = (sob[metric] * (sob['policies_sold_count']/sob['policies_sold_count'].sum())).mean()
            response += f"Mean of {metric}: {weighted_mean}"
        return response

    return f"MISSING_DATA : The requested metric ({metric}) for state : {state_abbreviation}, " \
           f" county : {county_name}, commodity : {commodity_name} and insurance plan : {insurance_plan_name}, " \
           f"is not available within the summary of business data. Make sure that you are providing an " \
           "existing combination of county, commodity and insurance plan name."


@tool("wfrp-commodities-tool")
def get_wfrp_commodities(reinsurance_yr: str, state_code: str, county_code: str) -> Optional[str]:
    """
    This tool is used to find commodities associated with the Whole Farm Revenue Protection (WFRP) insurance program
    for a given reinsurance year, state code and county code. Do not use this tool unless you are explicitly asked
    about available commodities for the WFRP program.

    To use this tool, you must provide all three arguments [reinsurance_yr, state_code and county_code]
    Do not make up those arguments if they are not provided explicitly.

    Args:
        reinsurance_yr (str): year of reinsurance
        state_code: (str) : state code
        county_code: (str) : county code

    Returns: Optional[str]
    """
    url = f"http://dev.lookup-api.cropguard.online/v1/lookups/GetWFRPCommodities"
    headers = {
        'accept': 'application/json',
        'api-key': os.environ["CROPGUARD_API_KEY"],
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json={"ReinsuranceYear": reinsurance_yr,
                                                         "StateCode": state_code,
                                                         "CountyCode": county_code})

    if response.status_code == 200:
        print("API call successful")
        response_data = response.json()
        # Process the response data as needed
        commodity_list = [i["AGR Commodity Name"] for i in response_data]
        return f"Available commodities for the WFRP program (year {reinsurance_yr}, state_code {state_code}, and " \
               f"county_code {county_code}) are : " + str(commodity_list)

    else:
        print("API call failed with status code:", response.status_code)
        return None


tools = [get_wfrp_commodities, get_sob_metrics_for_crop_county]
