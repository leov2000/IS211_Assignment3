import argparse
import logging
import urllib.request as urllib
from datetime import datetime
import csv
import re
from pprint import pprint
import json


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


def sum_all_browsers(user_agent_dict, matched_browser):
    sum_dict = {}

    for browser_name, browser_aggregate in matched_browser.items():
        for browser in browser_aggregate:
            if browser in user_agent_dict:
                if browser_name not in sum_dict:
                    sum_dict[browser_name] = user_agent_dict[browser]
                else:
                    sum_dict[browser_name] += user_agent_dict[browser]

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

    return f'Image requests account for {percentage}% of all requests.'


def popular_browser(browser_dict):
    sorted_browser_list = sorted(list(browser_dict.items()))
    head = sorted_browser_list[0]
    browser_name, hits = head

    return f'The popular browser is {browser_name} with # {hits} hits.'


def time_hits(time_dict):
    sorted_time_list = sorted(list(time_dict.items()))

    return [time_hits_formatted_message(item) for item in sorted_time_list]


def time_hits_formatted_message(time_item):
    (hour, hits) = time_item

    return f'Hour {hour} has {hits} hits.'


def process_data(csvContents):
    csvPayLoad = csv.reader(csvContents.decode('utf-8').splitlines())
    csvResults = [row for row in csvPayLoad]

    return csvResults


def json_file_meta_browser_details(dict_one, dict_two):
    json_dict = {
        'browserTypeSum': dict_one,
        'browserSum': dict_two
    }

    with open('browser-meta.json', 'w') as json_file:
        json.dump(json_dict, json_file, indent=4)


def safe_int_checker(int_str):
    try:
        num = int(int_str)
        return (True, num)
    except ValueError:
        return (False, None)


def print_time_hits(time_list):
    print('-' * 80)
    print('\n\n')
    print('Answer:')
    pprint(time_list)
    print('\n\n')
    print('-' * 80)


def standard_print(string_result):
    print('-' * 80)
    print('\n\n')
    print(f'Answer: {string_result}')
    print('\n\n')
    print('-' * 80)


def print_all(result):
    result_copy = result[:]
    time_hit_list = result_copy.pop()

    for answer in result_copy:
        standard_print(answer)

    print_time_hits(time_hit_list)


def get_data(url):
    csvData = urllib.urlopen(url)
    result = process_data(csvData.read())

    image_count = sum_image_count(result)

    regex_list = regex_config()
    user_agent_dict = get_all_browser_types(result)
    matched_tally = regex_browser_search(list(user_agent_dict.keys()), regex_list)
    browser_count = sum_all_browsers(user_agent_dict, matched_tally)

    json_file_meta_browser_details(user_agent_dict, browser_count)

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

            logging.error(f'Error processing <{args.url}>')
            return SystemExit

        CLI = result != None

        while CLI:
            keyed = keyed = input(
                'Please Enter a number from [1 - 4] for the Assignment Answer\n\n 1 will print out Assignment III\n 2 will print out Assignment IV\n 3 will print out the Extra Credit\n 4 will print ALL\n\n Click any other key to exit\n\n')
            (is_int, cast_num) = safe_int_checker(keyed)

            if is_int and cast_num in range(1, 5):
                if cast_num == 3:
                    print_time_hits(result[cast_num-1])
                elif cast_num == 4:
                    print_all(result)
                else:
                    standard_print(result[cast_num-1])

            else:
                CLI = False


if __name__ == '__main__':
    main()
