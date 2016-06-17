*** Settings ***
Resource    resources/common.robot

Library     Process
Library     OperatingSystem
Library     ${Libraries}/NetworkUtils.py
Library     ${KEYWORDS}/Logging.py

Library     ../test_bucket_shadow.py
Library     ../test_sg_replicate.py

Test Setup  Setup Test
Test Teardown   Test Teardown

Test Timeout    10 minutes

*** Variables ***


*** Test Cases ***

Offline Changes Feed Closed Multiple Sync Gateway
    [Documentation]  Tests that changes feed is closed while processing changes
    ...  from server.
    ...  1. Open a continuous changes feed on sg-1 pointed at server bucket 'db'
    ...  2. Push docs to sg-2 targeting the same server bucket 'db'
    ...  3. While, docs are getting pushed, issue _offline request to sg-1
    ...  4. Verify that the the continous changes feed is close and gets a 200 OK


*** Keywords ***
Setup Test
    Start Packet Capture

Test Teardown
    Log  Tearing down test ...  console=True
    List Connections
    Stop Packet Capture
    Collect Packet Capture  ${TEST_NAME}
    Run Keyword If Test Failed      Fetch And Analyze Logs  ${TEST_NAME}
