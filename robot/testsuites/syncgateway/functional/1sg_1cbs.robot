*** Settings ***
Resource    resources/common.robot

Library     Process
Library     OperatingSystem
Library     ${Libraries}/ClusterKeywords.py
Library     TestUsersChannels.py
Library     TestSync.py
Library     TestBulkGetCompression.py
Library     TestContinuous.py


Test Setup      Setup
Test Teardown   Teardown

*** Variables ***
${SERVER_VERSION}           4.1.0
${SYNC_GATEWAY_VERSION}     1.2.0-79
${CLUSTER_CONFIG}           ${CLUSTER_CONFIGS}/1sg_1cbs
${SYNC_GATEWAY_CONFIG}      ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

*** Test Cases ***
# Cluster has been setup

# TestBucketShadow
test bucket shadow propagates to source bucket
    test bucket shadow propagates to source bucket

# TestBulkGetCompression
test bulk get compression no compression
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}

test bulk get compression no compression 1.1 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  user_agent=CouchbaseLite/1.1

test bulk get compression accept encoding gzip
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip

test bulk get compression accept encoding gzip 1.1 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip  user_agent=CouchbaseLite/1.1

test bulk get compression x accept part encoding gzip
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  x_accept_part_encoding=gzip

test bulk get compression x accept part encoding gzip 1.1 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  x_accept_part_encoding=gzip  user_agent=CouchbaseLite/1.1

test bulk get compression accept encoding gzip x accept part encoding gzip
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip  x_accept_part_encoding=gzip

test bulk get compression accept encoding gzip x accept part encoding gzip 1.1 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip  x_accept_part_encoding=gzip  user_agent=CouchbaseLite/1.1

test bulk get compression no compression 1.2 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  user_agent=CouchbaseLite/1.2

test bulk get compression accept encoding gzip 1.2 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip  user_agent=CouchbaseLite/1.2

test bulk get compression x accept part encoding gzip 1.2 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  x_accept_part_encoding=gzip  user_agent=CouchbaseLite/1.2

test bulk get compression accept encoding gzip x accept part encoding gzip 1.2 user agent
    test bulk get compression   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_cc.json    ${300}  accept_encoding=gzip  x_accept_part_encoding=gzip  user_agent=CouchbaseLite/1.2

# TestContinuous
test continuous changes parametrized 1 user 5000 docs 1 revision
    test continuous changes parametrized    ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json  ${1}  ${5000}  ${1}

test continuous changes parametrized 50 users 5000 docs 1 revision
    test continuous changes parametrized    ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json  ${50}  ${5000}  ${1}

test continuous changes parametrized 50 users 5000 10 docs 10 revisions
    test continuous changes parametrized    ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json  ${50}  ${10}  ${10}

test continuous changes parametrized 50 user 50 docs 1000 revisions
    test continuous changes parametrized    ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json  ${50}  ${50}  ${1000}

test continuous changes sanity
    test_continuous_changes_sanity          ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json  ${10}  ${10}

# TestSync (channel cache mode)
test issue 1524
     test issue 1524            ${SYNC_GATEWAY_CONFIGS}/custom_sync/grant_access_one_cc.json   ${10}

test sync access sanity
    test sync access sanity     ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_access_sanity_cc.json

test sync channel sanity
    test sync channel sanity    ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_channel_sanity_cc.json

test sync role sanity
    test sync role sanity       ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_role_sanity_cc.json

test sync sanity
    test sync sanity            ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_one_cc.json

test sync sanity backfill
    test sync sanity backfill   ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_one_cc.json

test sync require roles
    test sync require roles     ${SYNC_GATEWAY_CONFIGS}/custom_sync/sync_gateway_custom_sync_require_roles_cc.json


# TestUsersChannels (channel cache mode)
test multiple users multiple channels
    test multiple users multiple channels   ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test muliple users single channel
    test muliple users single channel       ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test single user multiple channels
    test single user multiple channels      ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json

test single user single channel
    test single user single channel         ${SYNC_GATEWAY_CONFIGS}/sync_gateway_default_functional_tests_cc.json


*** Keywords ***
Setup
    Log To Console      Setting up ...
    Set Environment Variable    CLUSTER_CONFIG    ${cluster_config}
    #Provision Cluster   ${SERVER_VERSION}   ${SYNC_GATEWAY_VERSION}    ${SYNC_GATEWAY_CONFIG}

Teardown
    Log To Console      Tearing down ...