*** Settings ***
Documentation     A test suite containing functional tests of the Listener's
...               REST APIs for Design Documents.
...
...               These tests require JavaScript code to be passed in as arguments.
...               For cases where no code is required, like map-only views, just
...               pass in the ${EMPTY} specifier.
...
...               Note also the the use of the pipe-delimiter is not required,
...               but it is recommended on lines where JavaScript is being passed
...               in as using 4 spaces is less readable.
Resource          resources/common.robot
Resource          ./defines.robot
Library           Listener
Suite Setup       Start Listener     ${HOSTNAME}
Test Setup        Create Database    ${DBNAME}
Suite Teardown    Shutdown Listener
Test Timeout      30 seconds     The default test timeout elapsed before the test completed.

*** Test Cases ***
Test Public REST API access through nginx single sg instance
    Documentation    Configure a single nginx instance as a reverse proxy in front of a single Sync Gateway instance
    ...              Run a set of functional tests against the nginx service and see if the behaviour is as expected
    ...              for a non proxied Sync Gateway.
    ...              Q: Does this test SG or nginx configuration?

Test Public REST API access through nginx multiple sg instances
    Documentation    Configure a single nginx instance as a reverse proxy and load balancer in front of multiple Sync 
    ...              Gateway instances. Configure nginx for round-robin distribution of requests to all Sync Gateway instances.
    ...              Run a set of functional tests against the nginx service and see if the behaviour
    ...              is as expected.  
    ...              Look for issues caused by inconsistencies in state between SG instances. 

Test Public REST API access through nginx multiple sg instances turning at least one instance off
    Documentation    Configure a single nginx instance as a reverse proxy and load balancer in front of multiple Sync 
    ...              Gateway instances. Configure nginx for round-robin distribution of requests to all Sync Gateway instances.
    ...              Run a set of functional tests against the nginx service, during the test run turn off one of the Sync Gateway 
    ...              instances and see if the behaviour is as expected.  
    ...              Look for issues caused by inconsistencies in state between SG instances. 
    ...              Note: Plugins are required for nginx to detect that an SG instance is down and to stop sending 
    ...              requests to it. Errors may be related to this for standard nginx installations.

Test SG server memory utilization when accessed via nginx with terminating clients
    Documentation    Configure a single nginx instance as a reverse proxy in front of a single Sync Gateway instance
    ...              Run tests against Sync Gateway where the client request is terminated (to emulate lost network)
    ...              Monitor SG memory usage and open TCP connections. Memory and CPU should reach a steady state.
    ...              Compare resource useage compared to the same test sun directly against a Sync Gateway instance. 
    ...             
    ...              

Test Public REST API access through nginx configured for SSL termination
    Documentation   Enable SSL termination and test REST API access to a singulr Sync Gateway instance
    ...             Test document CRUD, _changes one-shot, long-poll, continuous and WebSocket
    ...             Validate that heartbeats are received by the client when requested in the _changes parameters


*** Keywords ***
Create Design Doc
    Documentation    Creates a new design doc via the REST API.
    [Arguments]      ${DESIGNDOC_NAME}    ${VIEW_NAME}    ${VIEW1_NAME}    ${MAP_FUNCTION}    ${REDUCE_FUNCTION}
    ${request} =     Create Request For Design Doc Named    ${DESIGNDOC_NAME}
    Add View         ${request}    ${VIEW1_NAME}    ${MAP_FUNCTION}    ${REDUCE_FUNCTION}
    Post             ${request}
    Status Equals    ${request}    201
