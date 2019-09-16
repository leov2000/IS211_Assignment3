import argparse
import logging
import urllib.request as urllib
from datetime import datetime
import csv
import re
import pprint


def regex_config():
    safari = '^(?!.*Chrome).*Safari'
    explorer = 'MSIE'
    firefox = 'Firefox'
    chrome = 'Chrome'

    regex_list = [
        {'Safari': safari},
        {'Explorer': explorer},
        {'Firefox': firefox},
        {'Chrome': chrome}
    ]

    return regex_list


def regex_browser_search(browser_list, regex_list):
    total_dict = {}

    for regex in regex_list:
        regex_result = []
        key, regex_val = list(regex.items())[0]
        total_dict[key] = regex_result

        for browser in browser_list:
            if re.search(regex_val, browser):
                regex_result.append(browser)

    return total_dict


def get_all_browser_types(result):
    browser_list = [browser[2] for browser in result]
    return sum_browser_type(browser_list)


def get_time_visits(result):
    time_list = [time_visit[1] for time_visit in result]
    return time_list


def sum_image_count(result):
    IMG_REG_PATTERN = '(?i).(?:jpg|jpeg|gif|png)$'
    image_list = [image[0]
                  for image in result if re.search(IMG_REG_PATTERN, image[0])]

    total_count = {
        'image_results': len(image_list),
        'total_results': len(result)
    }

    return total_count


def sum_time_visits(time_visit_list):
    sum_dict = {}
    FORMAT = '%Y-%m-%d %H:%M:%S'

    for time in time_visit_list:
        date_obj = datetime.strptime(time, FORMAT)
        hour_num = date_obj.strftime('%H')

        if hour_num in sum_dict:
            sum_dict[hour_num] += 1
        else:
            sum_dict[hour_num] = 1

    return sum_dict


def sum_all_browsers(browser_totals_dict, matched_browser):
    sum_dict = {}

    for browser_name, browser_aggregate in matched_browser.items():
        for browser in browser_aggregate:
            if browser in browser_totals_dict:
                if browser_name not in sum_dict:
                    sum_dict[browser_name] = browser_totals_dict[browser]
                else:
                    sum_dict[browser_name] += browser_totals_dict[browser]

    return sum_dict


def sum_browser_type(result):
    browser_dict = {}

    for browser_type in result:
        if browser_type in browser_dict:
            browser_dict[browser_type] += 1
        else:
            browser_dict[browser_type] = 1

    return browser_dict


def image_hits(totals_dict):
    image_total, file_total = tuple(totals_dict.values())
    percentage = (image_total / file_total) * 100

    return f"Image requests account for {percentage}% of all requests."


def popular_browser(browser_dict):
    sorted_browser_list = sorted(list(browser_dict.items()))
    head = sorted_browser_list[0]
    browser_name, hits = head

    return f"The popular browser is {browser_name} with # {hits} hits."


def time_hits(time_dict):
    sorted_time_list = sorted(list(time_dict.items()))
    return [time_hits_formatted_message(item) for item in sorted_time_list]


def time_hits_formatted_message(time_item):
    hour, hits = time_item
    return f"Hour {hour} has {hits} hits."


def process_data(csvContents):
    csvPayLoad = csv.reader(csvContents.decode('utf-8').splitlines())
    csvResults = [row for row in csvPayLoad]

    return csvResults


def get_data(url):
    csvData = urllib.urlopen(url)
    result = process_data(csvData.read())

    image_count = sum_image_count(result)

    regex_list = regex_config()
    browser_dict = get_all_browser_types(result)
    matched_tally = regex_browser_search(list(browser_dict.keys()), regex_list)
    browser_count = sum_all_browsers(browser_dict, matched_tally)

    time_list = get_time_visits(result)
    time_total = sum_time_visits(time_list)

    image_percentage = image_hits(image_count)
    top_browser = popular_browser(browser_count)
    hits_by_the_hour = time_hits(time_total)

    return [
        image_percentage,
        top_browser,
        hits_by_the_hour
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()

    logging.basicConfig(filename='errors.log',
                        level=logging.ERROR, format='%(message)s')
    logging.getLogger('assignment3')

    if(args.url):
        try:
            result = get_data(args.url)
        except (ValueError, urllib.HTTPError):
            print(
                f'Something went wrong, you entered in <{args.url}>, please check your url param for errors')
            return SystemExit


if __name__ == '__main__':
    main()
