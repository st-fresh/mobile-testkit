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
# Cluster has been setup

# test bucket shadow
test bucket shadow low_revs limit repeated_deletes
    [Tags]   sanity
    test bucket shadow low_revs limit repeated_deletes

test bucket shadow low_revs limit
    [Tags]   sanity
    test bucket shadow low_revs limit

test bucket shadow multiple sync gateways
    [Tags]   sanity
    test bucket shadow multiple sync gateways

Test Sg Replicate Basic Test
    [Tags]   sanity
    Test Sg Replicate Basic Test

Test Sg Replicate Non Existent Db
    [Tags]   sanity
    Test Sg Replicate Non Existent Db

Test Sg Replicate Continuous Replication
    [Tags]   sanity
    Test Sg Replicate Continuous Replication

Test Sg Replicate Delete Db Replication In Progress
    [Tags]   sanity
    Test Sg Replicate Delete Db Replication In Progress

Test Sg Replicate Basic Test Channels
    [Tags]   sanity
    Test Sg Replicate Basic Test Channels

Test Sg Replicate Push Async 100 docs
    [Tags]   sanity
    Test Sg Replicate Push Async    num_docs=${100}

Test Sg Replicate Push Async 250 docs
    [Tags]   sanity
    Test Sg Replicate Push Async    num_docs=${250}

Test Stop Replication Via Replication Id
    [Tags]   sanity
    Test Stop Replication Via Replication Id

Test Replication Config
    [Tags]   sanity
    Test Replication Config


*** Keywords ***
Setup Test
    Start Packet Capture

Test Teardown
    Log  Tearing down test ...  console=True
    List Connections
    Stop Packet Capture
    Collect Packet Capture  ${TEST_NAME}
    Run Keyword If Test Failed      Fetch And Analyze Logs  ${TEST_NAME}
