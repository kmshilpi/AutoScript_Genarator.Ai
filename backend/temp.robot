*** Settings ***
Library  SeleniumLibrary

*** Variables ***
${BROWSER}  chrome
${URL}  https://www.google.com

*** Test Cases ***
End To End Flow
  Open Browser  ${URL}  ${BROWSER}    options=add_argument("--disable-notifications"); add_argument("--disable-infobars"); add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2, "credentials_enable_service": False, "profile.password_manager_enabled": False})
  Maximize Browser Window