import logging

import requests
import tablib
from bs4 import BeautifulSoup


url_list = ['https://en.wikipedia.org/wiki/McLaren']


headers = ('Full name',
           'Website',
           'Chassis',
           'Engine',
           'Tyres',
           'Constructor titles',
           'Driver titles',
           'Races entered',
           'Race victories',
           'Pole positions',
           'Fastest laps')


def parse_page(soup_instance):
    """Parse Wikipedia page with F1 team data."""
    t = soup_instance.find('table', attrs={'class': 'infobox vcard'})
    data = t.find_all('tr')
    parsed_data = {}

    for tr in data:
        try:
            attr = tr.th.text
        except AttributeError:
            continue

        if attr in ['Full name', 'Website', 'Chassis', 'Engine', 'Tyres',
                    'Races entered', 'Race victories', 'Pole positions',
                    'Fastest laps']:
            parsed_data[attr] = tr.td.text
            continue

        if 'Constructors' in attr:
            parsed_data['Constructor titles'] = tr.td.text.split()[0]
            continue

        if 'Drivers' in attr:
            parsed_data['Driver titles'] = tr.td.text.split()[0]
            continue
    return parsed_data


def sanitize(data_dict):
    res = data_dict.copy()

    for k, v in res.items():
        try:
            ind = v.index('[')
            logging.warning(r" Sanitizing: '{0}' : '{1}'".format(k, v))
            res[k] = v[:ind]
        except (AttributeError, ValueError):
            continue

    k = 'Races entered'
    v = res[k]
    try:
        v = int(v)
    except ValueError:
        logging.warning(r" Sanitizing: '{0}' : '{1}'".format(k, v))
        res[k] = fetch_num(v)
    return res


def fetch_num(st):

    for item in st.split():
        try:
            num = int(item)
            return num
        except ValueError:
            continue


def make_dataset_row(data_dict):
    row = [data_dict.get(item) for item in headers]
    return tuple(row)


def main():
    logging.basicConfig(level=logging.WARN)

    data = []
    for url in url_list:
        print("\n* Parsing data from {0}".format(url))
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        parsed_data = parse_page(soup)
        if parsed_data:
            parsed_data = sanitize(parsed_data)
            row = make_dataset_row(parsed_data)
            data.append(row)
        else:
            logging.warning("Parsing failed for '{0}'".format(url))
            continue

    table = tablib.Dataset(*data, headers=headers)

    file_name = 'f1_data_'  + '.csv'

    with open(file_name, 'w') as fp:
        print(table.csv, file=fp)
    print("\n* Done. Results are exported into '{0}'".format(file_name))


if __name__ == '__main__':
    main()