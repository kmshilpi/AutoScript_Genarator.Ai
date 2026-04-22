*** Settings ***
Library    SeleniumLibrary

*** Variables ***
$${BROWSER}                        chrome
${URL}                            https://ensite.wattmonk.com/
${INPUT_EMAIL_FIELD}              css=#input_email
${PASSWORD_FIELD}                 css=#password
${SIGN_IN_BUTTON}                 xpath=//button[normalize-space()='Sign in']
${ELEM_5_ELEMENT}                 xpath=/html/body/app-root/layout/compact-layout/fuse-vertical-navigation/div/div[2]/fuse-vertical-navigation-basic-item[2]/div/div/img
${__WORK_ORDER_BUTTON}            xpath=//button[normalize-space()='+ Work Order']
${SALES_CLOSE_BUTTON}             css=#sales_close
${PROFILE_BUTTON}                 css=#profile
${SIGN_OUT_BUTTON}                xpath=//button[normalize-space()='Sign out']

*** Test Cases ***
End To End Flow
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${options}    add_argument    --disable-notifications
    Call Method    ${options}    add_argument    --disable-infobars
    ${prefs}=    Create Dictionary    profile.default_content_setting_values.notifications=2    credentials_enable_service=${False}    profile.password_manager_enabled=${False}
    Call Method    ${options}    add_experimental_option    prefs    ${prefs}
    Create Webdriver    Chrome    options=${options}
    Go To    ${URL}
    Maximize Browser Window
    Wait And Input    id=input_email    Shilpi_prepaid@gmail.com
    Wait And Input    id=password    Shubham@123
    Wait And Click    id=btn_signin_form_submit
    Wait And Click    ${ELEM_5_ELEMENT}
    Wait And Click    id=survey_add_form
    Wait And Click    id=sales_close
    Wait And Click    id=profile
    Wait And Click    id=btn_profile_onSignout

*** Keywords ***
Wait And Click
    [Arguments]    ${locator}
    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${locator}    15s
    Wait Until Keyword Succeeds    10x    2s    Click Element    ${locator}

Wait And Input
    [Arguments]    ${locator}    ${text}
    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${locator}    15s
    Wait Until Keyword Succeeds    10x    2s    Input Text    ${locator}    ${text}