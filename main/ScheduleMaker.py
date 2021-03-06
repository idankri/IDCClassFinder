"""
@author: Idan Kringel
Updated to IDC website as of March 2020
Written using python 3.7
requirements:
* python 3.7
* Selenium
* Chrome Webdriver (Maybe later add support for other webdrivers)

TODO:
* Debug and verify everything works
* Extract to JSON file (or any other convenient storage alternative)
* Write code for using the data in the JSON file (find vacant classes, find schedule for specific class, etc..)
"""

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from collections import defaultdict
import time
import re
from main.Retry import retry
import json

CHROME_DRIVER = r'C:\Webdrivers\chromedriver.exe'
JSON_PATH = r'C:\Users\User\Documents\Projects\IDCClassFinder\main\data.json'

YEDION_URL = r'http://portal.idc.ac.il/he/main/services/newsletter_regulations/yedion/pages/thisyearheb.aspx'

SCHOOL_XPATH = r'//*[@id="ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_CurriculumPickerSchedule_School"]'
YEAR_XPATH = r'//*[@id="ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_CurriculumPickerSchedule_StudyYear"]'
SPEC_XPATH = r'//*[@id="ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_CurriculumPickerSchedule_Specialization"]'
SEARCH_XPATH = r'//*[@id="ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_CurriculumPickerSchedule_CurriculumSearch"]'

FIRST_SEMESTER_LINK_ID = u'ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_ScheduleResults_ScheduleSemesterLinks_ctl01_ShowSchedules'
SECOND_SEMESTER_LINK_ID = u'ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_ScheduleResults_ScheduleSemesterLinks_ctl03_ShowSchedules'


class ScheduleMaker:
    def __init__(self):
        self.driver = self.init_driver()
        self.class_dict = defaultdict(lambda: defaultdict(list))

    @staticmethod
    def init_driver():
        """
        Init a new chrome driver on and go to relevant page
        :return: a selenium chrome driver
        """
        driver = webdriver.Chrome(CHROME_DRIVER)
        driver.get(YEDION_URL)
        driver.find_elements_by_link_text(u'מערכת שעות')[0].click()
        return driver

    def table_generator(self, semester: int):
        """
        A generator, in each iteration makes driver goto next table and then yields
        :param semester: 1 for first Semester else 2
        """
        school_num = DriverUtils.get_option_num(self.driver, SCHOOL_XPATH)
        for current_school in range(1, school_num):
            DriverUtils.select_option(self.driver, SCHOOL_XPATH, current_school)

            year_num = DriverUtils.get_option_num(self.driver, YEAR_XPATH)
            for current_year in range(1, year_num):
                DriverUtils.select_option(self.driver, YEAR_XPATH, current_year)

                specs_num = DriverUtils.get_option_num(self.driver, SPEC_XPATH)
                for current_spec in range(1, specs_num):
                    DriverUtils.select_option(self.driver, SPEC_XPATH, current_spec)
                    time.sleep(0.5)
                    try:
                        self.driver.find_elements_by_xpath(SEARCH_XPATH)[0].click()
                        time.sleep(0.5)
                        sem_id = FIRST_SEMESTER_LINK_ID if semester == 1 else SECOND_SEMESTER_LINK_ID
                        self.driver.find_element_by_id(sem_id).click()
                        time.sleep(1)
                        yield
                    except selenium.common.exceptions.NoSuchElementException:
                        pass

    def tear_down(self):
        """
        Quits the web driver, and deletes reference to the class dict
        """
        self.driver.quit()
        self.class_dict = None

    def main(self, semester=1):
        """
        Currently a main flow of the ScheduleMaker
        :param semester: which semester to create
        :return:
        """
        for _ in self.table_generator(semester):
            try:
                self._extract_all_times_from_table()
            except Exception as e:
                print(e)
        self.class_dict = dict(self.class_dict)
        # self.class_dict = {k: dict(v) for k, v in self.class_dict}
        self.create_json()
        self.tear_down()

    def create_json(self):
        """
        Document the data that was collected into the dict to a json file.
        :return: a json file.
        """
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.class_dict, f, ensure_ascii=False, indent=4)

    def _extract_all_times_from_table(self):
        """
        Iterates through all tables and extracting the class dict (containing schedule for each class)
        :param class_dict:
        :return: the class_dict
        """
        # goes through days 1 (sunday) to 6 (friday)
        for i in range(1, 7):
            text = DriverUtils.get_table_data(self.driver,
                                              r'//*[@id="ScheduleTab"]/table[2]/tbody/tr[2]/td[]', i)
            self._find_classes_by_hours(text, i)

    def _find_classes_by_hours(self, text: str, day: int):
        """
        Extract the Schedule for each class from given data using Regex
        :param text: text (should be extracted from table)
        :param class_dict: class_dict for the data to be extracted
        :param day: 1 for sunday, 6 for friday, etc..
        :return: the class dict
        """
        reg = re.compile(
            r"(?P<time_frame>\d{1,2}:\d{2} - \d{1,2}:\d{2})\n[^a-zA-Z0-9]*(?P<class_room>[a-zA-Z0-9\.]+)")
        all_times = reg.findall(text)
        for time_frame, class_room in all_times:
            if time_frame not in self.class_dict[class_room][day]:
                self.class_dict[class_room][day].append(time_frame)


class DriverUtils:
    @staticmethod
    @retry(selenium.common.exceptions.NoSuchElementException, tries=3, delay=2)
    def get_option_num(driver, xpath):
        se = Select(driver.find_element_by_xpath(xpath))
        return len(se.options)

    @staticmethod
    @retry(selenium.common.exceptions.NoSuchElementException, tries=3, delay=2)
    def select_option(driver, xpath: str, option: int):
        se = Select(driver.find_element_by_xpath(xpath))
        se.select_by_visible_text(se.options[option].text)

    @staticmethod
    @retry(selenium.common.exceptions.NoSuchElementException, tries=3, delay=2)
    def get_table_data(driver, xpath: str, td_num):
        text = driver.find_element_by_xpath(xpath[:-1] + str(td_num) + ']').text
        return text
    

if __name__ == '__main__':
    sm = ScheduleMaker()
    sm.main(semester=2)
