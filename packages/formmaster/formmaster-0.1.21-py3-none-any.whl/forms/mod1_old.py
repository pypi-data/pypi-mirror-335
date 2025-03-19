from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from .base import form_base
from getpass import getpass

import sys
import os
import re

class mod1(form_base):
    
    def __init__(self, _driver, _data, _mode):
        super(mod1, self).__init__(_driver, _data, _mode)
        self.manage_applications_url = None
        self.main_application_handle = None
        self.entry_url = 'https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_lgn'

    def create_profile(self):
        students = self.data
        driver = self.driver

        personal_info = students[-1][0]

        #print('Now processing: ', personal_info)
        given_name =  '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[1]/div/input'
        self.set_value(given_name, personal_info['Given Name'])

        family_name = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[2]/div/input'
        self.set_value(family_name, personal_info['Family Name'])

        dob = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[3]/div/div/input'
        self.set_value(dob, personal_info['DOB (dd/mm/yyyy)'])

        email = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[4]/div/input'
        self.set_value(email, personal_info["Student's Email"])

        confirmed_email = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[5]/div/input'
        self.set_value(confirmed_email, personal_info["Student's Email"])

        username = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[6]/div/input'
        str_username = f'{personal_info["Family Name"].upper()}{personal_info["Given Name"].lower()}{personal_info["DOB (dd/mm/yyyy)"].split("/")[-1]}'
        str_username = str_username.replace(' ', '')
        if personal_info["Number"] > 0:
            str_username = f"{str_username}{personal_info['Number'] + 1}"
        self.set_value(username, str_username)

        password = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[7]/div/input'
        password_val = f"{personal_info['DOB (dd/mm/yyyy)'].split('/')[-1]}{personal_info['Family Name'].upper()}{personal_info['Given Name'].lower()}"
        password_val = password_val.replace(' ', '')
        self.set_value(password, password_val) # default use email as username

        confirmed_password = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[8]/div/input'
        self.set_value(confirmed_password, password_val)

        tnc = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[9]/div/label/input[2]'
        self.check_button(tnc)

        acknowledge = '/html/body/div[1]/form/div/div/div/div[2]/div/div/div[10]/div/label/input[2]'
        self.check_button(acknowledge)

    def login_session(self):
        students = self.data
        driver = self.driver

        if not re.search('https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_portal.url.*', driver.current_url):
            
            username = os.getenv('SYD_USER', '')
            password = os.getenv('SYD_PASS', '')
            if not username:
                username = input('Username: ')
                password = getpass()

            driver.get(self.entry_url)

            wait = WebDriverWait(driver, 100)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # username/password
            username_input = '//*[@id="MUA_CODE.DUMMY.MENSYS"]'
            password_input = '//*[@id="PASSWORD.DUMMY.MENSYS"]'
            login_submit = '/html/body/div/form/div[4]/div/div/div[2]/div/fieldset/div[3]/div[1]/div/input'
            self.set_value(username_input, username)
            self.set_value(password_input, password)
            self.check_button(login_submit)
            
            wait = WebDriverWait(driver, 100)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            applications = '/html/body/header/nav/div[2]/ul/li[2]/a/b'
            self.check_button(applications)
            manage_applications = '//*[@id="APAGN01"]'
            self.check_button(manage_applications)

        self.manage_applications_url = driver.current_url
        self.main_application_handle = driver.current_window_handle
        
        if not self.collect_mode:
            print('\n\n ================ personal info ================= \n', students[-1][3])
            print('\n\n ================= edu info: ================= \n', students[-1][1])
            print('\n\n ================= application info: ================= \n', students[-1][2])

        return self.main_application_handle

    def fill_personal_info(self):
        students = self.data
        driver = self.driver

        personal_info = students[-1][0]
        title = '/html/body/div[1]/form/div[4]/div[2]/div/div/div[1]/div/div/div/div/input'
        givenname1='/html/body/div[1]/form/div[4]/div[2]/div/div/div[2]/div/div/div[1]/input'
        givenname2='/html/body/div[1]/form/div[4]/div[2]/div/div/div[2]/div/div/div[2]/input'
        givenname3='/html/body/div[1]/form/div[4]/div[2]/div/div/div[2]/div/div/div[3]/input'
        familyname='/html/body/div[1]/form/div[4]/div[2]/div/div/div[3]/div/input'
        akaname=   '/html/body/div[1]/form/div[4]/div[2]/div/div/div[4]/div/input'
        prevname=  '/html/body/div[1]/form/div[4]/div[2]/div/div/div[5]/div/input'
        officialname='/html/body/div[1]/form/div[4]/div[2]/div/div/div[6]/div/input'
        gender = '/html/body/div[1]/form/div[4]/div[2]/div/div/div[7]/div/div/div/div/input'
        dob = '/html/body/div[1]/form/div[4]/div[2]/div/div/div[8]/div/div/input'

        self.set_value_list(title, 'Mr' if personal_info['Gender'] == 'Male' else 'Miss')
        self.set_value(givenname1, personal_info['Given Name'])
        self.set_value(familyname, personal_info['Family Name'])
        self.set_value(akaname, personal_info['Given Name'])
        self.set_value(officialname, f"{personal_info['Given Name']} {personal_info['Family Name']}")
        self.set_value_list(gender, personal_info['Gender'])
        self.set_value(dob, personal_info['DOB (dd/mm/yyyy)'])

        country =            '/html/body/div[1]/form/div[7]/div[2]/div/div/div[1]/div/div/div/div/input'
        addressline1 =       '/html/body/div[1]/form/div[7]/div[2]/div/div/div[3]/div/input'
        addressline2 =       '/html/body/div[1]/form/div[7]/div[2]/div/div/div[4]/div/input'
        addressline3 =       '/html/body/div[1]/form/div[7]/div[2]/div/div/div[5]/div/input'
        city =               '/html/body/div[1]/form/div[7]/div[2]/div/div/div[6]/div/input'
        province =           '/html/body/div[1]/form/div[7]/div[2]/div/div/div[7]/div/input'
        postcode =           '/html/body/div[1]/form/div[7]/div[2]/div/div/div[8]/div/input'
        check_address_same = '/html/body/div[1]/form/div[7]/div[2]/div/div/div[9]/div[2]/div/label/input'

        self.set_value_list(country, 'China (Excludes SARS and Taiwan)')
        self.set_value(addressline1, personal_info['line1'])
        self.set_value(addressline2, personal_info['line2'])
        self.set_value(addressline3, personal_info['line3'])
        self.set_value(city, personal_info['city'])
        self.set_value(province, personal_info['province'])

        post = personal_info['Post Code'] if re.search('\d+', personal_info['Post Code']) else '0000'
        self.set_value(postcode, post)
        self.check_button(check_address_same)

        parent_country = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[1]/div/div/div/div/input'
        parent_address1 = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[3]/div/input'
        parent_address2 = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[4]/div/input'
        parent_address3 = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[5]/div/input'
        parent_town = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[6]/div/input'
        parent_state = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[7]/div/input'
        parent_postcode = '/html/body/div[1]/form/div[8]/div[2]/div/div/div[8]/div/input'
        
        self.set_value_list(parent_country, 'China (Excludes SARS and Taiwan)')
        self.set_value(parent_address1, personal_info['line1'])
        self.set_value(parent_address2, personal_info['line2'])
        self.set_value(parent_address3, personal_info['line3'])
        self.set_value(parent_town, personal_info['city'])
        self.set_value(parent_state, personal_info['province'])
        self.set_value(parent_postcode, post)

        phone = '/html/body/div[1]/form/div[9]/div[2]/div/div/div[1]/div/input'
        mobile = '/html/body/div[1]/form/div[9]/div[2]/div/div/div[2]/div/input'
        email = '/html/body/div[1]/form/div[9]/div[2]/div/div/div[3]/div/input'
        self.set_value(phone, personal_info["Student's Tel."])
        self.set_value(email, personal_info["Student's Email"])

        born_country = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[1]/div/div/div/div/input'
        au_citizenship = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[2]/div/div/div/div/input'
        nationality = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[4]/div/div/div/div/input'
        is_aboriginal = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[7]/div/div/div/div/input'
        hometongue = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[8]/div/div/div/div/input'
        
        self.set_value_list(born_country, 'China (Excludes SARS and Taiwan)')
        self.set_value_list(au_citizenship, 'Other (non resident)')
        self.set_value_list(nationality, 'China (Excludes SARS and Taiwan)')
        self.set_value_list(is_aboriginal, 'Neither Aboriginal nor Torres Strait Islander')
        self.set_value_list(hometongue, 'Mandarin')

        current_at_usyd = '//*[@id="IPQ_APONPAPB"]'
        current_student_usyd = '//*[@id="IPQ_APONLCES1B"]'
        current_enrolled_usyd = '//*[@id="IPQ_APONLCES3B"]'
        fee_waiver = '/html/body/div[1]/form/div[15]/div[2]/div/div/div/div/div[1]/label/input'
        no_fee_waiver = '/html/body/div[1]/form/div[15]/div[2]/div/div/div/div/div[2]/label/input'

        self.check_button(current_at_usyd)
        self.check_button(current_student_usyd)
        self.check_button(current_enrolled_usyd)
        self.check_button(no_fee_waiver)

    def fill_scholarships(self):
        driver = self.driver

        print('>>> scholarship info: ')
        has_scholarship = '//*[@id="IPQ_APONSH13A"]'
        scholarship_name = '//*[@id="IPQ_APONSH14"]'
        no_scholarship = '//*[@id="IPQ_APONSH13B"]'
        driver.find_element("xpath", no_scholarship).click()

        applied_scholarship = '//*[@id="IPQ_APONSH15A"]'
        applied_scholarship_name = '//*[@id="IPQ_APONSH16"]'
        no_applied_scholarship = '//*[@id="IPQ_APONSH15B"]'
        driver.find_element("xpath", no_applied_scholarship).click()
    
    def fill_your_qualifications(self):
        
        driver = self.driver
        students = self.data

        qualification = students[-1][1]
        print('>>> qualification info: ', qualification)
        not_first_language = '//*[@id="IPQ_APONEL1B"]'
        self.check_button(not_first_language)

        english_test = False
        taken_english_test = '//*[@id="IPQ_APONEL2A"]'
        no_english_test = '//*[@id="IPQ_APONEL2B"]'
        if english_test:
            self.check_button(taken_english_test)

            test_type = '/html/body/div[1]/form/div[4]/div[2]/div/div/div[3]/div/div/div/div/input'
            self.set_value_list(test_type, 'IELTS')

            test_date = '//*[@id="IPQ_APONEL4"]'
            self.set_value(test_date, '01/Mar/2020')

            overall_score = '//*[@id="IPQ_APONEL5"]'
            self.set_value_list(overall_score, '7')
            #upload english test result
        else:
            self.check_button(no_english_test)

            scheduled_test = '//*[@id="IPQ_APONEL10A"]'
            not_scheduled_test = '//*[@id="IPQ_APONEL10B"]'
            self.check_button(not_scheduled_test)

            tertiary_edu_accessed_in_english = '//*[@id="IPQ_APONEL12A1"]'
            not_tertiary_edu_accessed_in_english = '//*[@id="IPQ_APONEL12A2"]'
            self.check_button(not_tertiary_edu_accessed_in_english)

            scheduled_test1 = '//*[@id="IPQ_APONEL16A"]'
            not_scheduled_test1 = '//*[@id="IPQ_APONEL16B"]'
            self.check_button(not_scheduled_test1)

        #record of exclusion
        suspended_course = '//*[@id="IPQ_APONRE1A"]'
        no_suspended_course = '//*[@id="IPQ_APONRE1B"]'
        self.check_button(no_suspended_course)

        asked_cause = '//*[@id="IPQ_APONRE2A"]'
        no_asked_cause = '//*[@id="IPQ_APONRE2B"]'
        self.check_button(no_asked_cause)

        asked_explain = '//*[@id="IPQ_APONRE3A"]'
        no_asked_explain = '//*[@id="IPQ_APONRE3B"]'
        self.check_button(no_asked_explain)

        #upload docs for cause exclusion

        #high qualification
        edu_level = '/html/body/div[1]/form/div[8]/div[2]/div/div/div/div/div/div/div/input'
        self.set_value_list(edu_level, 'Secondary Qualification')

        #upload you docs

        # Secondary school studies
        secondary_edu = qualification.loc[0].values.flatten().tolist()
        secondary_qual_name = '//*[@id="IPQ_APONSS1"]'
        self.set_value(secondary_qual_name, secondary_edu[1])
        secondary_qual_state = '//*[@id="IPQ_APONSS2"]'
        self.set_value(secondary_qual_state, secondary_edu[3])

        year = re.search('20\d\d', secondary_edu[0])
        if year:
            secondary_qual_year = '/html/body/div[1]/form/div[9]/div[2]/div/div/div[3]/div/div/div/div/input'
            self.set_value_list(secondary_qual_year, year.group())

        secondary_qual_score = '//*[@id="IPQ_APMOTHRS"]'
        self.set_value(secondary_qual_score, secondary_edu[4])

        # Academic school studies
        if (qualification.shape[0] > 1) and qualification['School'].tolist()[1]:
            tertiary_edu = qualification.loc[1].values.flatten().tolist()

            academic_qual_name = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[1]/div/div/div/div/input'
            self.set_value_list(academic_qual_name, 'Bachelors degree')

            academic_qual_course = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[2]/div/input'
            self.set_value(academic_qual_course, tertiary_edu[2])

            academic_qual_institution = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[3]/div/input'
            self.set_value(academic_qual_institution, tertiary_edu[1])

            academic_qual_country = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[4]/div/div/div/div/input'
            self.set_value_list(academic_qual_country, self.get_country_code(tertiary_edu[3]))

            d1,d2 = self.get_date_range(tertiary_edu[0])
            academic_qual_start_date = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[5]/div/div/input'
            self.set_value(academic_qual_start_date, d1)

            academic_qual_end_date = '/html/body/div[1]/form/div[10]qualification/div[2]/div/div/div[6]/div/div/input'
            self.set_value(academic_qual_end_date, d2)

            academic_qual_length = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[7]/div/input'
            self.set_value(academic_qual_length, '')

            academic_qual_grade = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[8]/div/input'
            self.set_value(academic_qual_grade, tertiary_edu[4])

            academic_qual_completed = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[9]/div/div[1]/label/input'
            self.check_button(academic_qual_completed)

            academic_qual_parttime = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[10]/div/div[1]/label/input'
            self.check_button(academic_qual_parttime)

            if (qualification.shape[0] > 2) and qualification['School'].tolist()[2]:
                print('Add another qualification')
                another_qual = '/html/body/div[1]/form/div[10]/div[2]/div/div/div[11]/div/div/label/input'
                self.check_button(another_qual)

                tertiary_edu = qualification.loc[2].values.flatten().tolist()

                academic_qual_name = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[1]/div/div/div/div/input'
                self.set_value_list(academic_qual_name, 'Bachelors degree')

                academic_qual_course = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[2]/div/input'
                self.set_value(academic_qual_course, tertiary_edu[2])

                academic_qual_institution = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[3]/div/input'
                self.set_value(academic_qual_institution, tertiary_edu[1])

                academic_qual_country = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[4]/div/div/div/div/input'
                self.set_value_list(academic_qual_country, self.get_country_code(tertiary_edu[3]))


                d1,d2 = self.get_date_range(tertiary_edu[0])
                academic_qual_start_date = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[5]/div/div/input'
                self.set_value(academic_qual_start_date, d1)

                academic_qual_end_date = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[6]/div/div/input'
                self.set_value(academic_qual_end_date, d2)

                academic_qual_length = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[7]/div/input'
                self.set_value(academic_qual_length, '')

                academic_qual_grade = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[8]/div/input'
                self.set_value(academic_qual_grade, tertiary_edu[4])

                academic_qual_completed = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[9]/div/div[1]/label/input'
                self.check_button(academic_qual_completed)

                academic_qual_parttime = '/html/body/div[1]/form/div[11]/div[2]/div/div/div[10]/div/div[1]/label/input'
                self.check_button(academic_qual_parttime)


        app_for_cred = '//*[@id="applyForCredit"]'
        no_app_for_cred = '//*[@id="doNotApplyForCredit"]'
        driver.find_element("xpath", no_app_for_cred).click()

    def fill_further_references(self):
        print('>>> reference info: ')
        pass

    def fill_form(self):
        driver = self.driver

        app_form = '/html/body/div[1]/form/div[2]/h1'
        title = driver.find_element("xpath", app_form).text
        if title == 'Your personal information':
            self.fill_personal_info()
        elif title == 'Scholarships':
            self.fill_scholarships()
        elif title == 'Your qualifications':
            self.fill_your_qualifications()
        elif title == 'Further references':
            self.fill_further_references()
        elif title == 'Declaration':
            print('Please confirm.')
            #return self.new_application()
        elif title == 'Manage your application fee':
            pass
        else:
            pass
        
        return True

    def new_application(self):
        driver = self.driver
        students = self.data

        driver.close()
        driver.switch_to.window(self.main_application_handle)
        driver.get(self.manage_applications_url)
        students.pop()
        if not len(students):
            print('Congrats, you finished processing. ')
            return False

        print('Now processing: ', students[-1][0])
        return True

    def search_course(self):
        students = self.data

        df_application = students[-1][2]
        df_application = df_application[df_application['Proposed School'] == 'USYD']
        course_applied = df_application['Proposed Course with Corresponding Links'].tolist()[0]
        if df_application.shape[0] > 1:
            df_application = df_application.drop(index=[0])
            new_item = students[-1].copy()
            new_item[0]['Number'] += 1
            new_item[2] = df_application
            students.insert(0, new_item)
            
        course = '//*[contains(@id,"POP_UDEF") and contains(@id,"POP.MENSYS.1-1")]'
        self.set_value(course, course_applied)

        #view_report = '/html/body/div[1]/form/div[3]/div/div/div[2]/div[3]/div/input[2]'
        #driver.find_element("xpath", view_report).click()

        return

    def payment_email(self):
        email = '//*[@id="UDS_EMAIL"]'
        self.set_value(email, 'au.info@shinyway.com')

    def payment_method(self):
        #cardnumber = '//*[@id="UDS_CARDNUMBER"]'
        cardnumber = '/html/body/form/fieldset/ul/li[1]/div[2]/input'
        month = '/html/body/form/fieldset/ul/li[2]/div[2]/input[1]'
        year = '/html/body/form/fieldset/ul/li[2]/div[2]/input[2]'
        self.set_value(cardnumber, '123456789')
        self.set_value(month, '09')
        self.set_value(year, '25')

    def run(self):
        if self.collect_mode:
            print('collect page information.')
            return

        students = self.data
        if not len(students):
            print('no more studnets to process.')
            sys.exit()
        
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        url = self.driver.current_url

        if re.search('https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_ipp_cgi.start?', url):
            if not self.fill_form():
                sys.exit()

        elif re.search('https://sydneystudent.sydney.edu.au/sitsvision/wrd/SIW_POD.start_url?.+', url):
            self.search_course()

        # create profile
        elif re.search('https://sydneystudent.sydney.edu.au/sitsvision/wrd/siw_ipp_lgn.login?.+', url):
            self.create_profile()

        # email payment
        elif re.search('https://pay.sydney.edu.au/ePays/paymentemail\?UDS_ACTION=PMPBPN', url):
            self.payment_email()
            
        elif re.search('https://pay.sydney.edu.au/ePays/paymentemail$', url):
            self.payment_method()

        else:
            print('no actions for: ', url)
            pass

    