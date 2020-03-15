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
import time, re

CHROME_DRIVER = r'C:\Webdrivers\chromedriver.exe'

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

                specs_num = DriverUtils.get_option_num(self.driver, YEAR_XPATH)
                for current_spec in range(1, specs_num):
                    DriverUtils.select_option(self.driver, SPEC_XPATH, current_spec)

                    self.driver.find_elements_by_xpath(SEARCH_XPATH)[0].click()
                    time.sleep(0.5)
                    try:
                        sem_id = FIRST_SEMESTER_LINK_ID if semester == 1 else SECOND_SEMESTER_LINK_ID
                        self.driver.find_element_by_id(sem_id).click()
                        yield
                    except selenium.common.exceptions.NoSuchElementException:
                        pass

    def tear_down(self):
        """
        Quits the web driver.
        """
        self.driver.quit()

    def main(self, semester=1):
        """
        Currently a main flow of the ScheduleMaker
        :param semester: which semester to create
        :return:
        """
        # self.driver = self.init_driver()
        class_dict = defaultdict(lambda: defaultdict(list))  # maybe consider working with regular dict?
        for _ in self.table_generator(semester):
            self._extract_all_times_from_table(class_dict)
        self.create_json()  # dict(class_dict))
        self.tear_down()

    def create_json(self):
        # TODO: write
        pass

    def _extract_all_times_from_table(self, class_dict):
        """
        Iterates through all tables and extracting the class dict (containing schedule for each class)
        :param class_dict:
        :return: the class_dict
        """
        # goes through days 1 (sunday) to 6 (friday)
        for i in range(1, 7):
            text = self.driver.find_element_by_xpath(
                r'//*[@id="ScheduleTab"]/table[2]/tbody/tr[2]/td[' + str(i) + ']').text
            self._find_classes_by_hours(text, class_dict, i)
        return class_dict

    def _find_classes_by_hours(self, text: str, class_dict: defaultdict, day: int):
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
            if time_frame not in class_dict[class_room][day]:
                class_dict[class_room][day].append(time_frame)
        return class_dict


class DriverUtils:
    @staticmethod
    def get_option_num(driver, xpath):
        se = Select(driver.find_element_by_xpath(xpath))
        return len(se.options)

    @staticmethod
    def select_option(driver, xpath: str, option: int):
        se = Select(driver.find_element_by_xpath(xpath))
        se.select_by_visible_text(se.options[option].text)


if __name__ == '__main__':
    sm = ScheduleMaker()
    sm.main(semester=2)
