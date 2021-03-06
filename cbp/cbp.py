import pandas as pd
from pandas import DataFrame
import requests
import sys

emp_imputation = {'a': 10,
                  'b': 60,
                  'c': 175,
                  'e': 375,
                  'f': 750,
                  'g': 1750,
                  'h': 3750,
                  'i': 7500,
                  'j': 17500,
                  'k': 37500,
                  'l': 75000,
                  'm': 110000}

naics_year = {
    2014: 'NAICS2012',
    2013: 'NAICS2012',
    2012: 'NAICS2012',
    2011: 'NAICS2007',
    2010: 'NAICS2007',
    2009: 'NAICS2007',
    2008: 'NAICS2007'
}


class Counties(DataFrame):
    """
    DataFrame of County Business Patterns data for all counties in a given state.

    Parameters
    ----------
    state_fips : str
        Two-digit FIPS code for the state
    year : str or int, optional
        Year of data to download (if downloading data). Default is 2015.
    read_from : str, optional
        Must be one of 'api' and 'csv'. Default is 'api'.
    key : str, optional
        API key from the Census Bureau
    variables : list, optional
        List of variables (as str) to download, default list is provided
    filepath : str, optional
        File path to csv file if that option is desired
    impute_emp : bool, optional
        If True and read_from='api', imputes midpoint of employment range for industries with a flag \
        instead of an estimate

    """

    def __init__(self, state_fips, year=2014, read_from='api', key=None, variables=None, filepath=None,
                 impute_emp=True):

        dtypes = {
            'NAICS2012': str,
            'county': str,
            'state': str
        }

        if read_from == 'api':

            if not key:
                raise ValueError('If reading from Census API, must provide API key in the key parameter')

            baseurl = 'http://api.census.gov/data/{}/cbp'.format(year)

            if variables:
                cbp_vars = ','.join(variables)
            else:
                cbp_vars = 'EMP,EMP_F,ESTAB,NAICS2012,NAICS2012_TTL,GEO_TTL'

            url = '{baseurl}?get={cbp_vars}&for=county:*&in=state:{state_fips}&key={key}'.format(**locals())

            try:
                req = requests.get(url)
                req.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print err
                sys.exit(1)

            results = pd.read_json(req.text, orient='index', dtype=dtypes).T
            results.columns = results.iloc[0]
            results.drop(results.index[0], inplace=True)

            cbp_dtypes = {
                'EMP': int,
                'ESTAB': int
            }

            for variable in cbp_dtypes.keys():
                results[variable] = results[variable].astype(cbp_dtypes[variable])

            data = results

            if impute_emp:
                data['EMP'] = data.apply(lambda x: emp_imputation[x.EMP_F] if x.EMP_F else x.EMP, axis=1)

            data.drop('EMP_F', axis=1, inplace=True)

        elif read_from == 'csv':

            if not filepath:
                raise ValueError('If reading from CSV file, must provide path to file in filepath parameter')

            data = pd.read_csv(filepath_or_buffer=filepath, dtype=dtypes)

        else:
            raise ValueError('Valid options for the read_from parameter are "api" and "csv".')

        DataFrame.__init__(self, data=data)

    def get_county(self, county):
        """
        Returns a subset of the Counties DataFrame for one or more specified counties.

        Parameters
        ----------
        county : str or list
            County FIPS code or list of FIPS codes

        Returns
        -------
        DataFrame

        """

        if isinstance(county, list):
            result = self[self.county.isin(county)]
        elif isinstance(county, str):
            result = self[self.county == county]
        else:
            raise TypeError('County identifier must be str')
        return result

    def two_digit(self, county=None):
        """
        Returns a reduced version of the Counties DataFrame with only 2-digit NAICS codes, filtered by county if
        optional parameter is passed.

        Parameters
        ----------
        county : str or list, optional
            County FIPS code or list of FIPS codes

        Returns
        -------

        """
        two_digits = self[(self.NAICS2012.str.len() == 2) |
                          (self.NAICS2012.str.contains('-'))]

        if county:
            if isinstance(county, list):
                result = two_digits[two_digits.county.isin(county)]
            elif isinstance(county, str):
                result = two_digits[two_digits.county == county]
            else:
                raise TypeError('County identifier must be str')
            return result

        else:
            return two_digits

    def three_digit(self, county=None):
        """
        Returns a reduced version of the Counties DataFrame with only 3-digit NAICS codes, filtered by county if
        optional parameter is passed.

        Parameters
        ----------
        county : str or list, optional
            County FIPS code or list of FIPS codes

        Returns
        -------

        """
        three_digits = self[(self.NAICS2012.str.len() == 3) | (self.NAICS2012 == '00')]

        if county:
            if isinstance(county, list):
                result = three_digits[three_digits.county.isin(county)]
            elif isinstance(county, str):
                result = three_digits[three_digits.county == county]
            else:
                raise TypeError('County identifier must be str')
            return result

        else:
            return three_digits

    def four_digit(self, county=None):
        """
        Returns a reduced version of the Counties DataFrame with only 4-digit NAICS codes, filtered by county if
        optional parameter is passed.

        Parameters
        ----------
        county : str or list, optional
            County FIPS code or list of FIPS codes

        Returns
        -------

        """
        four_digits = self[(self.NAICS2012.str.len() == 4) | (self.NAICS2012 == '00')]

        if county:
            if isinstance(county, list):
                result = four_digits[four_digits.county.isin(county)]
            elif isinstance(county, str):
                result = four_digits[four_digits.county == county]
            else:
                raise TypeError('County identifier must be str')
            return result

        else:
            return four_digits

    def total(self):
        """
        Returns a DataFrame with totals of employment and establishments for each NAICS2012 code in the Counties object.

        Returns
        -------
        DataFrame

        """
        grouped = self.groupby(by='NAICS2012')

        agg_by = {
            'EMP': 'sum',
            'ESTAB': 'sum'
        }

        return grouped.agg(agg_by)
