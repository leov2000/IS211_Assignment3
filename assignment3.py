import argparse
import logging
import urllib.request as urllib
from datetime import datetime
import csv
import re
from pprint import pprint
import json


def regex_config():
    """
    A configuration function delegated for regex configs.

    Parameters:
        None 

    Returns:
        A config dictionary with regex patterns
    """

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
    """
    A function used to aggregate browser-types to browser.

    Parameters:
        browser_list(list[str]): A list of user-agent types.
        regex_list(list[dict[str, regex]]): A list of regex patterns.

    Returns:
        A dictionary with the summarized browsers.

    Return Eg:
        {
            'Chrome' : int,
            'Firefox : int'
        }    

    """

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
    """
    A function that retrieves the browser index from the result payload.

    Parameters:
        result(list[list[str]]): The result payload converted into a list
    
    Returns:
        the result of calling the sum_browser_type which summarizes the user-agent 
        type into a dictionary.
    """

    browser_list = [browser[2] for browser in result]

    return sum_browser_type(browser_list)


def get_time_visits(result):
    """
    A function that retrieves the time hit index from the result payload.

    Parameters:
        result(list[list[str]]): The result payload converted into a list

    Returns:
        A list of time hits. 
    """

    time_list = [time_visit[1] for time_visit in result]

    return time_list


def sum_image_count(result):
    """
    A function used to search for case-insensitve image file extension types and provide a total count.

    Parameters:
        result(list[list[str]]): The result payload converted into a list

    Returns:
        An integer representing the sum of the image types in the result payload.

    """

    IMG_REG_PATTERN = '(?i).(?:jpg|jpeg|gif|png)$'
    image_list = [image[0]
                  for image in result if re.search(IMG_REG_PATTERN, image[0])]

    total_count = {
        'image_results': len(image_list),
        'total_results': len(result)
    }

    return total_count


def sum_time_visits(time_visit_list):
    """
    A function used to sum occurences by the hour.

    Parameters:
        time_visit_list(list[str]): A list of time visits in string format

    Returns: 
        A dictionary with the summary of all time visits.
    """

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
    """
    A function used to find and pluck the values summed from the browser_total_dicts
    with using a key from a list of the matched browser dict

    Eg:
    {
        'user-agent-Chrome-Browser-etc.etc.' : 22
    }

    {
        Chrome: ['user-agent-Chrome-Browser-etc.etc.' ....]
    }

    Parameters:
        user_agent_dict(dict[str, int]): a dictionary of user-agent sums
        matched_browser(dict[str, list[str]]): a dictionary browser -> user-agent relations

    Returns:
        A dictionary summary of all 4 browsers listed in payload.
    """

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
    """
    A function used to sum all user-agents

    Parameters:
        result(list[str]) - the plucked user-agent-browser result from the payload
    
    Returns:
        A dictionary with the summed user-agent-totals
    """

    browser_dict = {}

    for browser_type in result:
        if browser_type in browser_dict:
            browser_dict[browser_type] += 1
        else:
            browser_dict[browser_type] = 1

    return browser_dict


def image_hits(totals_dict):
    """
    A function used to generate the % and string formatting.

    Parameters: totals_dict(dict[str, int]): the image totals as well as the payload file totals.

    Returns:
        A string representing the amount of image files are contained within the payload.
    """

    image_total, file_total = tuple(totals_dict.values())
    percentage = (image_total / file_total) * 100

    return f'Image requests account for {percentage}% of all requests.'


def popular_browser(browser_dict):
    """
    A function used to sort and find the popular browser and format the string according to spec.

    Parameters:
        browser_dict(dict[str, int]): The browser totals for all 4 browsers in this payload.
    
    Returns:
        A string representing the popular browser.

    """

    sorted_browser_list = sorted(list(browser_dict.items()))
    head = sorted_browser_list[0]
    browser_name, hits = head

    return f'The popular browser is {browser_name} with # {hits} hits.'


def time_hits(time_dict):
    """
    A functioned used to sort and format the visits by the hour.

    Parameters:
        time_dict(dict[str, int]): The time totals
    
    Returns:
        A formatted string with the help of its respective formatting function

    """
    sorted_time_list = sorted(list(time_dict.items()))
    return [time_hits_formatted_message(item) for item in sorted_time_list]


def time_hits_formatted_message(time_item):
    """
    A time formatting function.

    Parameters:
        time_item:(tuple(str, int)): A tuple containing the hour string and time hits int
    
    Returns:
        A formatted string indicating the hits by the hour.
    """

    (hour, hits) = time_item

    return f'Hour {hour} has {hits} hits.'


def process_data(csvContents):
    """
    A function that receives a fetched csv payload, parses, and converts to list.

    Parameters:
        csvContents(bytes): csv data fetched
   
    Returns:
        A list of the payload. 
    """

    csvPayLoad = csv.reader(csvContents.decode('utf-8').splitlines())
    csvResults = [row for row in csvPayLoad]

    return csvResults


def json_file_meta_browser_details(dict_one, dict_two):
    """
    A function that generated a json file "browser-meta"

    Parameters:
        dict_one(dict[str, int]): user-agent totals
        dict_two(dict[str, int]): browser totals
   
    Prints:
        the user agent totals and browser totals. 
    """
    json_dict = {
        'browserTypeSum': dict_one,
        'browserSum': dict_two
    }

    with open('browser-meta.json', 'w') as json_file:
        json.dump(json_dict, json_file, indent=4)


def safe_int_checker(int_str):
    """
    A function that checks if the string is actually an int. used for the CLI.
    
    Parameters:
        int_str(str): A string representing an int.

    Returns:
        A tuple with a boolean as the first item and a value if its successfuly cast or None if it isnt.
    """

    try:
        num = int(int_str)
        return (True, num)
    except ValueError:
        return (False, None)


def print_time_hits(time_list):
    """
    A function used to pretty print the extra credit time hits

    Parameters:
        time_list(list[str])
    
    Prints:
        pretty prints a list.
    """
    print('-' * 80)
    print('\n\n')
    print('Answer:')
    pprint(time_list)
    print('\n\n')
    print('-' * 80)


def standard_print(string_result):
    """
    A function used to print the assignment results.

    Parameters:
        string_result(str): a formatted time string
    
    Print:
        Prints the formatted time string
    """
    print('-' * 80)
    print('\n\n')
    print(f'Answer: {string_result}')
    print('\n\n')
    print('-' * 80)


def print_all(result):
    """
    A function used to print all of the answers.

    Parameters:
        result(list)
    
    Prints:
        Assignment III, Assignment IV and Extra Credit
    """
    result_copy = result[:]
    time_hit_list = result_copy.pop()

    for answer in result_copy:
        standard_print(answer)

    print_time_hits(time_hit_list)


def get_data(url):
    """
    A subsidiary function to the main function that delegates retrieving and encapsulating 
    the results:

    Parameters:
        url:(str): an http url
    
    Returns:
        The list that fulfills Assignment III, Assignment IV and Extra Credit
    
    """

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
    """
    The primary function of this application.

    Parameters:
        None
    
    Logs:
        An error if the string url is entered incorrectly.
    """
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
