'''
<div class="sv-panel sv-panel-primary">
				<div class="sv-panel-heading">
					<h2 class="sv-panel-title">Record of exclusion</h2>
				</div>
				<div class="sv-panel-body">
					If you answer 'yes' to any of the following questions you will have <!--the opportunity--> to upload supporting documents. <!--later in the application.--> Please complete the section below.<br><br>
					<div class="sv-form-container">
						<div class="sv-form-horizontal">
							<div class="sv-form-group">
								<label class="sv-col-md-3 sv-control-label">Have you ever been excluded or suspended from a course at a tertiary education institution? *</label>
								<div class="sv-col-md-4">
									
									<div class="sv-radio"><label><input name="IPQ_APONRE1" id="IPQ_APONRE1A" type="radio" value="Y">&nbsp;Yes</label></div>
									
									
									<div class="sv-radio"><label><input name="IPQ_APONRE1" id="IPQ_APONRE1B" type="radio" value="N">&nbsp;No</label></div>
									
								</div>
							</div>
							<div class="sv-form-group">
								<label class="sv-col-md-3 sv-control-label">Have you ever been asked to show cause why your enrolment in any course should not be suspended/terminated? *</label>
								<div class="sv-col-md-4">
									
									<div class="sv-radio"><label><input name="IPQ_APONRE2" id="IPQ_APONRE2A" type="radio" value="Y">&nbsp;Yes</label></div>
									
									
									<div class="sv-radio"><label><input name="IPQ_APONRE2" id="IPQ_APONRE2B" type="radio" value="N">&nbsp;No</label></div>
									
								</div>
							</div>
							<div class="sv-form-group">
								<label class="sv-col-md-3 sv-control-label">Have you ever been asked to explain unsatisfactory progress in any course? *</label>
								<div class="sv-col-md-4">
									
									<div class="sv-radio"><label><input name="IPQ_APONRE3" id="IPQ_APONRE3A" type="radio" value="Y">&nbsp;Yes</label></div>
									
									
									<div class="sv-radio"><label><input name="IPQ_APONRE3" id="IPQ_APONRE3B" type="radio" value="N">&nbsp;No</label></div>
									
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
'''

import re
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from forms.utils.form_utils import set_value_by_id, select_option_by_id, ensure_radio_selected

class QualificationsRecordOfExclusions:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Question 1: Ever been excluded or suspended
        excluded_or_suspended = personal_info.get('excluded_or_suspended', False)
        if excluded_or_suspended:
            ensure_radio_selected(driver, "IPQ_APONRE1A")  # Yes
        else:
            ensure_radio_selected(driver, "IPQ_APONRE1B")  # No
        
        # Question 2: Ever been asked to show cause
        asked_to_show_cause = personal_info.get('asked_to_show_cause', False)
        if asked_to_show_cause:
            ensure_radio_selected(driver, "IPQ_APONRE2A")  # Yes
        else:
            ensure_radio_selected(driver, "IPQ_APONRE2B")  # No
        
        # Question 3: Ever been asked to explain unsatisfactory progress
        unsatisfactory_progress = personal_info.get('unsatisfactory_progress', False)
        if unsatisfactory_progress:
            ensure_radio_selected(driver, "IPQ_APONRE3A")  # Yes
        else:
            ensure_radio_selected(driver, "IPQ_APONRE3B")  # No
