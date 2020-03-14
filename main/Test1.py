from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time, re

def browse():
    driver = webdriver.Chrome(r'C:\Webdrivers\chromedriver.exe')
    driver.get(r'http://portal.idc.ac.il/he/main/services/newsletter_regulations/yedion/pages/thisyearheb.aspx')
    driver.find_elements_by_link_text(u'מערכת שעות')[0].click()
    se = Select(driver.find_elements_by_name(
        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$School')[0])
    se.select_by_visible_text(se.options[10].text)
    time.sleep(0.1)
    se = Select(driver.find_elements_by_name(
        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$StudyYear')[0])
    se.select_by_visible_text(se.options[1].text)
    time.sleep(0.1)
    se = Select(driver.find_elements_by_name(
        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$Specialization'
    )[0])
    se.select_by_visible_text(se.options[1].text)
    time.sleep(0.1)
    driver.find_elements_by_name(
        u'ctl00$ctl26$g_cdf367b8_9960_4a77_9e5b_247c7c6d5387$ctl00$CurriculumPickerSchedule$CurriculumSearch')[0].click()
    time.sleep(1)
    driver.find_element_by_id(
        u'ctl00_ctl26_g_cdf367b8_9960_4a77_9e5b_247c7c6d5387_ctl00_ScheduleResults_ScheduleSemesterLinks_ctl01_ShowSchedules').click()
    #text = driver.find_element_by_tag_name('body').text
    #td[1] is for sunday, td[6] is for friday
    text = driver.find_element_by_xpath('//*[@id="ScheduleTab"]/table[2]/tbody/tr[2]/td[6]')
    find_classes_by_hours(text)
    driver.quit()

def extract_all_times_from_table(driver):

    for i in range(1,7):
        text = driver.find_element_by_xpath('//*[@id="ScheduleTab"]/table[2]/tbody/tr[2]/td[{}]'.format(i))
        find_classes_by_hours(text)

def find_classes_by_hours(text):
    reg = re.compile(r"(?P<time>\d{1,2}:\d{2} - \d{1,2}:\d{2})\n[^a-zA-Z0-9]*(?P<class>[a-zA-Z0-9]+)")
    all_times = reg.findall(text)

def gengen():
    for i in range(1,5):
        yield
browse()