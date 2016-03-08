*** Settings ***
Resource    resources/common.robot

Library     Process
Library     OperatingSystem
Library     ${Libraries}/ClusterKeywords.py
Library     TestCbgtPIndex.py


Test Setup      Setup
Test Teardown   Teardown

*** Variables ***
${SERVER_VERSION}           4.1.0
${SYNC_GATEWAY_VERSION}     1.2.0-79
${CLUSTER_CONFIG}           ${CLUSTER_CONFIGS}/1sg_1ac_1cbs

*** Test Cases ***
# Cluster has been setup

# Test TestCbgtPIndex
test_pindex_distribution
    test_pindex_distribution    ${SYNC_GATEWAY_CONFIGS}/performance/sync_gateway_default_performance.json

*** Keywords ***
Setup
    Log To Console      Setting up ...
    Set Environment Variable    CLUSTER_CONFIG    ${cluster_config}
    #Provision Cluster   ${SERVER_VERSION}   ${SYNC_GATEWAY_VERSION}    ${SYNC_GATEWAY_CONFIG}
    #Install Sync Gateway   ${CLUSTER_CONFIG}    ${SYNC_GATEWAY_VERSION}    ${SYNC_GATEWAY_CONFIG}

Teardown
    Log To Console      Tearing down ...