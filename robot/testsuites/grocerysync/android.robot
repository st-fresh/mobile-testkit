*** Settings ***

Library         OperatingSystem
Library         AppiumLibrary
Library         ../../utilities/android.py

Test Setup      Launch Application
Test Teardown   Close Application

*** Test Cases ***

Pull Docs from sync_gateway
    [Documentation]     Preseed a sync gateway with documents an make sure documents get pulled to client
    [Tags]              sync_gateway    grocery_sync    android
    Tap                 id=com.couchbase.grocerysync:id/addItemEditText
    Input Text          id=com.couchbase.grocerysync:id/addItemEditText     Item 1
    Press Enter
    Tap                 id=com.couchbase.grocerysync:id/addItemEditText
    Input Text          id=com.couchbase.grocerysync:id/addItemEditText     Item 2
    Press Enter
    Tap                 id=com.couchbase.grocerysync:id/addItemEditText
    Input Text          id=com.couchbase.grocerysync:id/addItemEditText     Item 3
    Press Enter

*** Keywords ***

Launch Application
    Open Application    http://localhost:4723/wd/hub    platformName=Android    deviceName=emulator-5554    app=%{GROCERY_SYNC_APK}

Press Enter
    Press Keycode       66