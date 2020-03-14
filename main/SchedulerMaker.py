"""
@creator: Idan Kringel
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
        driver.get(r'http://portal.idc.ac.il/he/main/services/newsletter_regulations/yedion/pages/thisyearheb.aspx')
        driver.find_elements_by_link_text(u'מערכת שעות')[0].click()
        return driver

    def table_generator(self, semester: int):
        """
        A generator, in each iteration makes driver goto next table and then yields
        :param semester: 1 for first Semester else 2
        TODO: Make less ugly :)
        """
        school_num = 2  # temp value
        current_school = 1
        while current_school < school_num:
            se = Select(self.driver.find_elements_by_name(
                u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$School')[0])
            school_num = len(se.options)
            se.select_by_visible_text(se.options[current_school].text)
            # time.sleep(0.1)

            current_year = 1
            year_num = 2  # temp value
            while current_year < year_num:
                se = Select(self.driver.find_elements_by_name(
                    u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$StudyYear')[0])
                year_num = len(se.options)
                se.select_by_visible_text(se.options[current_year].text)
                # time.sleep(0.1)

                current_spec = 1
                specs_num = 2  # temp value
                while current_spec < specs_num:
                    se = Select(self.driver.find_elements_by_name(
                        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$Specialization'
                    )[0])
                    specs_num = len(se.options)
                    se.select_by_visible_text(se.options[current_spec].text)
                    time.sleep(0.1)
                    self.driver.find_elements_by_name(
                        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$CurriculumSearch')[
                        0].click()
                    time.sleep(1)
                    try:
                        table_ext_id = u'1' if semester == 1 else u'3'
                        table_id_str = u'ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_ScheduleResults_ScheduleSemesterLinks_ctl0' + table_ext_id + u'_ShowSchedules'
                        self.driver.find_element_by_id(table_id_str).click()
                        yield
                    except selenium.common.exceptions.NoSuchElementException:
                        pass
                    current_spec += 1
                current_year += 1
            current_school += 1

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
        reg = re.compile(r"(?P<time>\d{1,2}:\d{2} - \d{1,2}:\d{2})\n[^a-zA-Z0-9]*(?P<class>[a-zA-Z0-9\.]+)")
        all_times = reg.findall(text)
        for value, key in all_times:
            if value not in class_dict[key][day]:
                class_dict[key][day].append(value)
        return class_dict


if __name__ == '__main__':
    sm = ScheduleMaker()
    sm.main(semester=2)
