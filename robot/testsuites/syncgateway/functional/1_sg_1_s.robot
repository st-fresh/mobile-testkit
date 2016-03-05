*** Settings ***
Resource    resources/common.robot

Library     Process
Library     OperatingSystem
Library     ${Libraries}/ClusterKeywords.py
Library     TestUsersChannels.py


Test Setup      Setup
Test Teardown   Teardown

*** Variables ***
${SERVER_VERSION}           4.1.0
${SYNC_GATEWAY_VERSION}     1.2.0-79
${CLUSTER_CONFIG}           ${CLUSTER_CONFIGS}/1sg_1s

*** Test Cases ***
# Cluster has been setup

test multiple users multiple channels (channel cache)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test multiple users multiple channels   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test muliple users single channel (channel cache)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test muliple users single channel       ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test single user multiple channels (channel cache)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test single user multiple channels      ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test single user single channel (channel cache)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test single user single channel         ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test multiple users multiple channels (distributed index)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test multiple users multiple channels   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_di.json

test muliple users single channel (distributed index)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test muliple users single channel       ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_di.json

test single user multiple channels (distributed index)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test single user multiple channels      ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_di.json

test single user single channel (distributed index)
    [Documentation]     Sync Gateway Functional Tests
    [Tags]              sync_gateway    sanity
    test single user single channel         ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_di.json

*** Keywords ***
Setup
    Log To Console      Setting up ...
    Set Environment Variable    CLUSTER_CONFIG    ${cluster_config}
    #Provision Cluster   ${SERVER_VERSION}   ${SYNC_GATEWAY_VERSION}    ${SYNC_GATEWAY_CONFIG}
    #Install Sync Gateway   ${CLUSTER_CONFIG}    ${SYNC_GATEWAY_VERSION}    ${SYNC_GATEWAY_CONFIG}

Teardown
    Log To Console      Tearing down ...