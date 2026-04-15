*** Settings ***
Library    SeleniumLibrary

***Settings***
Library    SeleniumLibrary

***Variables***
${ENSITE_URL}    https://ensite.wattmonk.com/home/survey/overview
${WELCOME_SECTION_XPATH}    xpath=/html/body/app-root/layout/empty-layout/div/div/auth-sign-in/div/div[2]
${EMAIL_FIELD}    css=#input_email
${PASSWORD_FIELD}    css=#password
${SIGNIN_BUTTON}    css=#btn_signin_form_submit
${NAVIGATION_ICON_XPATH}    xpath=/html/body/app-root/layout/compact-layout/fuse-vertical-navigation/div/div[2]/fuse-vertical-navigation-basic-item[2]/div/div/img
${ADD_WORKORDER_BUTTON}    css=#survey_add_form
${SURVEY_TYPE_DROPDOWN_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/div[1]/div/mat-form-field/div/div[1]/div/mat-select/div/div[2]
${BLANK_AREA_XPATH}    xpath=/html/body/div[5]/div[3]
${SURVEY_DROPDOWN_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/div[2]/mat-form-field/div/div[1]/div/mat-select/div/div[2]
${SURVEY_OPTION_XPATH}    xpath=//mat-option//span[normalize-space(text())="Survey"]
${NAME_LABEL_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/mat-form-field[1]/div/div[1]/div
${SURVEY_NAME_FIELD}    css=#survey_name
${PROFILE_EMAIL_FIELD_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/div[4]/app-email-profile/form/div/mat-form-field/div/div[1]/div
${EMAIL_INPUT_FIELD}    css=[placeholder='Enter email']
${TEAM_MEMBER_DROPDOWN_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/mat-form-field[2]/div/div[1]/div/div/mat-select/div/div[2]
${BLANK_TEAM_MMEBER_XPATH}    xpath=//*[@id='mat-option-278']
${PHONE_FIELD}    css=#input_teamadd_form_phone
${ADDRESS_FIELD_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/div[5]/div/app-google-map-autocomplete/mat-form-field/div/div[1]/div
${ADDRESS_INPUT}    css=#input_address
${START_DATE_CALENDAR_BUTTON}    css=[aria-label='Open calendar']
${APRIL_16_2026}    css=[aria-label='April 16, 2026']
${APRIL_17_2026}    css=[aria-label='April 17, 2026']
${TIME_SLOT_BUTTON}    css=#survey_slots
${FILE_ATTACHMENT_DIV_XPATH}    xpath=/html/body/div[5]/div[2]/div/mat-dialog-container/app-addsurveydialog/form/div/div/div[12]/app-dropzone/div/ngx-dropzone/ngx-dropzone-label/div
${FILE_UPLOAD_INPUT}    css=#undefined
${COMMENTS_TEXTAREA}    css=#survey_comments
${SUBMIT_REQUEST_BUTTON_TEXT_XPATH}    xpath=//button[contains(normalize-space(text()), 'Submit Request')]
${CANCEL_BUTTON}    css=#_itCancel

***Test Cases***
Create New Survey
    Open Browser    ${ENSITE_URL}    chrome
    Maximize Browser Window
    Wait Until Keyword Succeeds    15x    2s    Go To    ${ENSITE_URL}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${WELCOME_SECTION_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${WELCOME_SECTION_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${EMAIL_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${EMAIL_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${EMAIL_FIELD}    khatter@gmail.com
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${PASSWORD_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${PASSWORD_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${PASSWORD_FIELD}    test123
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SIGNIN_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SIGNIN_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${EMAIL_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${EMAIL_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${EMAIL_FIELD}    khattar@gmail.com
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SIGNIN_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SIGNIN_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${NAVIGATION_ICON_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${NAVIGATION_ICON_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${ADD_WORKORDER_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${ADD_WORKORDER_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SURVEY_TYPE_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SURVEY_TYPE_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${BLANK_AREA_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${BLANK_AREA_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SURVEY_TYPE_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SURVEY_TYPE_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SURVEY_OPTION_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SURVEY_OPTION_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${NAME_LABEL_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${NAME_LABEL_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${SURVEY_NAME_FIELD}    t@gmail.com
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SURVEY_NAME_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SURVEY_NAME_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${SURVEY_NAME_FIELD}    
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${PROFILE_EMAIL_FIELD_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${PROFILE_EMAIL_FIELD_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${EMAIL_INPUT_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${EMAIL_INPUT_FIELD}    t@gmail.com
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SURVEY_NAME_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SURVEY_NAME_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${SURVEY_NAME_FIELD}    Test
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${TEAM_MEMBER_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${TEAM_MEMBER_DROPDOWN_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${BLANK_TEAM_MMEBER_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${BLANK_TEAM_MMEBER_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${PHONE_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${PHONE_FIELD}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${PHONE_FIELD}   987-673-55353
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${ADDRESS_FIELD_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${ADDRESS_FIELD_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${ADDRESS_INPUT}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${ADDRESS_INPUT}    123
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${START_DATE_CALENDAR_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${START_DATE_CALENDAR_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${APRIL_16_2026}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${APRIL_16_2026}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${START_DATE_CALENDAR_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${START_DATE_CALENDAR_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${APRIL_17_2026}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${APRIL_17_2026}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${TIME_SLOT_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${TIME_SLOT_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${FILE_ATTACHMENT_DIV_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${FILE_ATTACHMENT_DIV_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${FILE_UPLOAD_INPUT}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${FILE_UPLOAD_INPUT}    C:\fakepath\image (5).png
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${COMMENTS_TEXTAREA}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${COMMENTS_TEXTAREA}
    Wait Until Keyword Succeeds    15x    2s    Input Text    ${COMMENTS_TEXTAREA}    Test
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${SUBMIT_REQUEST_BUTTON_TEXT_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${SUBMIT_REQUEST_BUTTON_TEXT_XPATH}
    Wait Until Keyword Succeeds    15x    2s    Wait Until Element Is Visible    ${CANCEL_BUTTON}
    Wait Until Keyword Succeeds    15x    2s    Click Element    ${CANCEL_BUTTON}