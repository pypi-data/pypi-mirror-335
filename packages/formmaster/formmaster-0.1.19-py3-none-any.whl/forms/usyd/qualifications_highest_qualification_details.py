'''
<div class="sv-form-group">
    <label for="IPQ_APONLHQL" class="sv-col-md-3 sv-control-label">What is your highest level of educational achievement successfully completed prior to this application? *</label>
    <div class="sv-col-md-4">
        <select name="IPQ_APONLHQL" id="IPQ_APONLHQL" class="" style="display: none;">
            <option value="">-- Select --</option>
            <option value="600">Secondary Qualification</option><option value="524">Certificate I</option><option value="521">Certificate II</option><option value="514">Certificate III</option><option value="511">Certificate IV</option><option value="420">Diploma</option><option value="410">Advanced Diploma and Associate Degree</option><option value="300">Bachelor Degree</option><option value="200">Graduate Diploma or Graduate Certificate</option><option value="120">Master Degree</option><option value="110">Doctoral Degree</option><option value="000">None of the above</option>
        </select>
        <!-- ... rest of HTML ... -->
    </div>
</div>
'''

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from forms.utils.form_utils import select_chosen_option_by_id, is_element_visible

class QualificationsHighestQualificationDetails:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Get highest qualification details from data
        highest_qualification = personal_info.get('highest_qualification', {})
        
        # If no highest qualification provided, use sensible defaults
        if not highest_qualification:
            if 'academic_qualifications' in personal_info and personal_info['academic_qualifications']:
                highest_qualification = personal_info['academic_qualifications'][0]
            else:
                highest_qualification = {
                    'qualification_type': 'Bachelors degree',
                    'education_level': 'Bachelor Degree'
                }
        
        # Map qualification types to education levels
        education_level_map = {
            'bachelor': 'Bachelor Degree',
            'master': 'Master Degree',
            'doctor': 'Doctoral Degree',
            'phd': 'Doctoral Degree',
            'diploma': 'Diploma',
            'advanced diploma': 'Advanced Diploma and Associate Degree',
            'certificate iv': 'Certificate IV',
            'certificate 4': 'Certificate IV',
            'certificate iii': 'Certificate III',
            'certificate 3': 'Certificate III',
            'certificate ii': 'Certificate II',
            'certificate 2': 'Certificate II',
            'certificate i': 'Certificate I',
            'certificate 1': 'Certificate I',
            'secondary': 'Secondary Qualification',
            'high school': 'Secondary Qualification',
            'graduate diploma': 'Graduate Diploma or Graduate Certificate',
            'graduate certificate': 'Graduate Diploma or Graduate Certificate'
        }
        
        # Determine education level
        education_level = highest_qualification.get('education_level', '')
        
        if not education_level:
            qual_type = highest_qualification.get('qualification_type', '').lower()
            
            # Try to match qualification type to education level
            for key, value in education_level_map.items():
                if key in qual_type:
                    education_level = value
                    break
                    
            # Default if no match found
            if not education_level:
                education_level = 'Secondary Qualification'
        
        # Select the highest level of education
        select_chosen_option_by_id(driver, "IPQ_APONLHQL", education_level)