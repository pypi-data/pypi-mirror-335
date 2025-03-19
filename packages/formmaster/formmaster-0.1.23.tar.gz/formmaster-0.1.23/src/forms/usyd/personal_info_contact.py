'''
<div class="sv-form-container">
						Please provide the applicant's contact details below. Correspondance concerning this application will be only sent to the agency details listed above. Mandatory fields are marked with an asterisk (*).<br><br>
						<div class="sv-form-horizontal">
							<div class="sv-form-group">
								<label for="IPR_HTEL" class="sv-col-md-3 sv-control-label">Applicant's telephone *</label>
								<div class="sv-col-md-4">
									<input name="IPR_HTEL" id="IPR_HTEL" class="sv-form-control" type="text" maxlength="35" value="">
									<small>Include country code and area code. This field is optional if you have provided us with the applicant's mobile telephone number below.</small>
								</div>
							</div>
							<div class="sv-form-group">
								<label for="IPR_HAT3" class="sv-col-md-3 sv-control-label">Applicant's mobile</label>
								<div class="sv-col-md-4">
									<input name="IPR_HAT3" id="IPR_HAT3" class="sv-form-control" type="text" maxlength="35" value="">
									<small>Include country code and area code. This field is optional if you have provided us with the applicant's telephone number above.</small>
								</div>
							</div>
							<div class="sv-form-group">
								<label for="IPR_HAEM" class="sv-col-md-3 sv-control-label">Applicant's email *</label>
								<div class="sv-col-md-4">
									<input name="IPR_HAEM" id="IPR_HAEM" class="sv-form-control" type="email" maxlength="255" value="jinqiu.guo@mail.mcgill.ca">
									<small>Please provide the applicant's email address. Notifications about this application will only go to the agency details listed above.</small>
								</div>
							</div>
						</div>
					</div>
'''

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from forms.utils.form_utils import set_value_by_id

class PersonalInfoContact:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        try:
            # Applicant's telephone (required unless mobile is provided)
            phone = personal_info.get("Student's Tel.", '')
            mobile = personal_info.get("Student's mobile", '')
            
            # At least one contact number is required
            if not phone and not mobile:
                # Generate default if neither phone nor mobile is provided
                country_code = self.get_country_code(personal_info.get('Country', ''))
                phone = f"{country_code} 123456789"  # Default placeholder
            
            if phone:
                set_value_by_id(driver, "IPR_HTEL", phone)
            
            # Applicant's mobile (optional if telephone provided)
            if mobile:
                set_value_by_id(driver, "IPR_HAT3", mobile)
            
            # Applicant's email (required)
            email = personal_info.get("Student's Email", '')            
            set_value_by_id(driver, "IPR_HAEM", email)
            
        except Exception as e:
            print(f"Error filling contact information: {e}")
    
    def get_country_code(self, country):
        """Get telephone country code based on country name"""
        country_codes = {
            'china': '+86',
            'australia': '+61',
            'united states': '+1',
            'usa': '+1',
            'india': '+91',
            'japan': '+81',
            'korea': '+82',
            'singapore': '+65',
            'malaysia': '+60',
            'indonesia': '+62',
            'vietnam': '+84',
            'thailand': '+66',
        }
        
        # Default to China if country not found
        for key, code in country_codes.items():
            if key.lower() in country.lower():
                return code
        
        return '+86'  # Default to China code