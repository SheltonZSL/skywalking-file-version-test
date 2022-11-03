import importlib.util
import os
import random
import time
from typing import Union

import requests
from bs4 import BeautifulSoup


class PyPIScraper:
    def __init__(self, name: str, file_version_in_file: str):
        """
        This function is used to initialize the class.
        :param name: The name of the package.
        :param file_version_in_file: The version of the package in the file.
        """
        self.file_version_in_file = file_version_in_file
        self.feed = f'https://pypi.org/rss/project/{name}/releases.xml'
        self.pypi_url = f'https://pypi.org/project/{name}/'

    def get_website_source_code(self, url: str, num_retries=2) -> Union[str, bytes]:
        """
        This function is used to get the source code of the website.
        :param url: The url of the website.
        :param num_retries: The number of retries.
        :return: The source code of the website.
        """
        header = {'User-agent': 'wswp'}
        try:
            response = requests.get(url, header)
        except requests.exceptions.Timeout as e:
            time.sleep(random.randint(1, 2))
            response = None
            if num_retries > 0:
                return self.get_website_source_code(url, num_retries=num_retries - 1)
        return response.content

    def crawl_xml_version(self) -> list:
        """
        This function is used to crawl the version of the package.
        :return: The list of all versions of the package.
        """
        file_version_list = []
        rss = self.get_website_source_code(self.feed)
        soup = BeautifulSoup(rss, features="xml")
        version_list = soup.find_all('item')
        for item in version_list:
            versions = item.find_all('title')
            for number in versions:
                file_version_list.append(number.get_text())
        return file_version_list

    def get_python_version(self) -> list:
        """
        This function is used to get the version of Python.
        :return: The version of Python.
        """
        html = self.get_website_source_code(self.pypi_url)
        soup = BeautifulSoup(html, "html.parser")
        sidebar_section_classifier = soup.find('ul', class_='sidebar-section__classifiers')
        temp_lis = sidebar_section_classifier.find_all('li', recursive=False)
        number = 0
        ind = 0
        for elem in temp_lis:
            if 'Programming Language' in elem.text:
                ind = number
            number += 1
        py_version_classifier = temp_lis[ind]
        py_version_list = py_version_classifier.find_all('li')
        python_version = []
        for number in py_version_list:
            versions = number.get_text().strip()
            python_version.append(versions)
        return python_version

    def get_difference_version(self, file_version: list, file_version_in_file: str) -> list:
        """
        This function is used to get the difference between the latest version and the current version.
        :param file_version: The list of all versions of the package.
        :param file_version_in_file: The version of the package in the file.
        :return: The difference between the latest version and the current version.
        """
        difference_version_list = []
        for index in range(len(file_version)):
            difference_version_list.append(file_version[index])
            if file_version_in_file == file_version[index]:
                difference_version_list.remove(file_version[index])
                if not difference_version_list:
                    return 'This is latest version.'
                else:
                    difference_version_list.append(file_version[index])
                return difference_version_list

    def change_version(self, file_version: list, file_version_in_file: str) -> str:
        """
        This function is used to change the version of the package.
        :param file_version: The list of all versions of the package.
        :param file_version_in_file: The version of the package in the file.
        :return: The latest version of the package.
        """
        for index in range(len(file_version)):
            for num in range(6):
                if file_version_in_file == file_version[index][:num]:
                    file_version_in_file = file_version[index]
                    return file_version_in_file

    def scrape(self) -> None:
        """
        This function is used to scrape the version of the package.
        :return: The latest version of the package.
        """
        python_version = self.get_python_version()
        latest_file_version = self.crawl_xml_version()[0]
        file_version = self.crawl_xml_version()
        print(f'This is the file name for the test now: {file_name}')
        print(f'The latest version of file:{latest_file_version}')
        print(f'The current file version is:{self.file_version_in_file}')
        for index in range(len(python_version)):
            if '3.10' in python_version[index]:
                print('This file supports 3.10 version in Python')
                break
            elif 'Python :: 3' == python_version[index]:
                print('This file supports 3.x version  in Python')
                break
            elif 'Python' == python_version[index]:
                print('This file supports any versions in Python')
                break
        difference_version = self.get_difference_version(file_version, self.file_version_in_file)
        if difference_version is None:
            self.file_version_in_file = self.change_version(file_version, self.file_version_in_file)
            difference_version = self.get_difference_version(file_version, self.file_version_in_file)
        if type(difference_version) is list:
            for index in range(len(difference_version)):
                number = len(difference_version[index].split('.'))
                if number != 3:
                    difference_version[index] = difference_version[index] + '.0'
                elif number > 3:
                    difference_version[index].split('.').pop()
            print(difference_version)
            print(f'We are missing {len(difference_version)} versions:')
            get_number_of_versions(difference_version)


def crawl_file() -> list:
    """
    This function is used to crawl the file name and the python version of the file.
    :return: The file name and the python version of the file.
    """
    support_info = []
    base_path = '../skywalking/plugins'
    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith('sw_'):
                name = os.path.basename(entry)
                name = name.replace('.py', '')
                file_path = 'skywalking.plugins.' + name
                imported = importlib.import_module(file_path)
                support_matrix = getattr(imported, 'support_matrix')
                support_info.append(support_matrix)
        return support_info


def check_website(file_name: str, file_python_version: dict) -> str or list:
    """
    This function is used to check the website of the file.
    :param file_name: The name of the file.
    :param file_python_version: The python version of the file.
    :return: The website of the file.
    """
    for value in file_python_version.values():
        if '*' in value:
            print(f'This is the file name for the test now:{file_name}')
            print('This is the built-in module library. '
                  'All python version can use it')
            return []
    if 'psycopg[binary]' == file_name:
        file_name = 'psycopg-binary'
        return file_name
    else:
        return file_name


def get_number_of_versions(difference_version: list) -> None:
    """
    This function is used to get the number of versions
    :param difference_version: The difference version list
    :return: The number of versions
    """
    # TODO replaced above code with below code
    big_version_matrix = [x_y_z.split('.')[0] for x_y_z in difference_version]
    medium_version_matrix = [x_y_z.split('.')[1] for x_y_z in difference_version]
    small_version_matrix = [x_y_z.split('.')[2] for x_y_z in difference_version]
    if len(set(big_version_matrix)) == 1:
        print('Big version same')
    else:
        print('Big version different ')
        difference = int(big_version_matrix[0]) - int(big_version_matrix[1])
        print(f'The big version difference is:{difference}')

    if len(set(medium_version_matrix)) == 1:
        print('medium version same')
    else:
        difference = 0
        try:
            difference = int(max(medium_version_matrix)) - int(min(medium_version_matrix))
        except ValueError as e:
            print(e)
        print(f'The medium version difference is：{difference}')
    if len(set(small_version_matrix)) == 1:
        print(set(small_version_matrix))
        print('small version same')
    else:
        difference = 0
        try:
            difference = int(max(small_version_matrix)) - int(min(small_version_matrix))
        except ValueError as e:
            print(e)
        print(f'The small version difference is：{difference}')


def get_current_file_version(support_matrix: dict) -> str:
    """
    Get the current file version
    :param support_matrix: The support matrix of the file
    :return: file_version_in_file
    """
    file_version = support_matrix[num][file_name]['>=3.6']
    if len(file_version) > 1:
        if file_version[0] > file_version[1]:
            file_version = file_version[0]
        else:
            file_version = file_version[1]
    else:
        file_version = file_version[0]
    return file_version


if __name__ == '__main__':
    support_matrix = crawl_file()
    for num in range(len(support_matrix)):
        for file_name in support_matrix[num]:
            file_python_version = support_matrix[num][file_name]
            name = check_website(file_name, file_python_version)
            file_version_in_file = get_current_file_version(support_matrix)
            if name:
                time.sleep(0.5)
                version = PyPIScraper(name=name, file_version_in_file=file_version_in_file)
                version.scrape()
