*** Settings ***
Documentation   Test Multiworker Dummy Run
...
...             Exercises the fully dummy run, using multiple workers,
...             checking for all sorts of details of the run execution.
...             It does not check for results
...             storage explicitly, but will make sure that all log outputs
...             indicate a safe, successful and complete execution of the
...             dummy experiment run.

Library         String
Library         Process
Library         OperatingSystem
Library         ${CURDIR}${/}ConfigFileModifier.py
Test Teardown   Clean Files
Test Setup      Create Config Files

*** Variables ***
${stdout_file} =            ${TEMPDIR}${/}dummy_experiment_mw.stdout
${stderr_file} =            ${TEMPDIR}${/}dummy_experiment_mw.stderr

*** Keywords ***
Create Config Files
    ${result} =                     Run Process  palaestrai  runtime-config-show-default  stdout=runtime_config_file-dummyrun.yml
    ${queueidx} =                   Get Variable Value  ${PABOTQUEUEINDEX}  0
    ${LOGPORT}                      Evaluate  str(24243 + random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${EXECUTORPORT}                 Evaluate  str(24242 - random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${conf} =                       Replace String  ${result.stdout}  4242  ${EXECUTORPORT}
    ${conf} =                       Replace String  ${conf}  4243  ${LOGPORT}
    Set Suite Variable              $runtime_config_file  ${TEMPDIR}${/}dummyrun-multiworker-test-${LOGPORT}${EXECUTORPORT}.conf.yml
    Create File                     ${runtime_config_file}.orig  ${conf}
    ${db_file_path} =               prepare_for_sqlite_store_test  ${runtime_config_file}.orig  ${runtime_config_file}  ${TEMPDIR}
    Set Suite Variable              $db_file_path
    Log File                        ${runtime_config_file}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  runtime-config-show-effective
    Log Many                        ${result.stdout}  ${result.stderr}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  database-create  stdout=${stdout_file}  stderr=${stderr_file}
    Should Be Equal As Integers     ${result.rc}   0

Clean Files
    Remove File                     ${stdout_file}
    Remove File                     ${stderr_file}
    Remove File                     ${runtime_config_file}
    Remove File                     ${db_file_path}

*** Test Cases ***
# Debug:
#   Robot stacktrace: https://github.com/MarketSquare/robotframework-stacktrace
#   Cmd:
#     pabot --command robot --listener RobotStackTracer -t "Run dummy experiment multiworker" --end-command --outputdir ./test_reports/system tests/system/test_multiworker_dummy_run.robot
Run dummy experiment multiworker
    [Timeout]                       15min
    ${process} =                    Start Process  palaestrai  -vc  ${runtime_config_file}  experiment-start  ${CURDIR}${/}..${/}fixtures${/}dummy_run_tt_multiworker.yml    stdout=${stdout_file}  stderr=${stderr_file}
    ${result} =                     Wait For Process  ${process}  timeout=5min  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    ${brain_dir}                    Set Variable  ${EXECDIR}${/}_outputs${/}brains/Multi-worker, multi-episode TT dummy run
    File Should Exist               ${brain_dir}${/}0${/}mighty_defender.bin
    File Should Exist               ${brain_dir}${/}0${/}evil_attacker.bin
    File Should Exist               ${brain_dir}${/}1${/}mighty_defender.bin
    File Should Exist               ${brain_dir}${/}1${/}evil_attacker.bin
    ${result} =                     Run Process  sqlite3  -csv  ${db_file_path}  stdin=SELECT erp.id, COUNT(ma.id) FROM muscle_actions ma JOIN main.agents a on a.id = ma.agent_id JOIN main.experiment_run_phases erp on erp.id = a.experiment_run_phase_id JOIN main.experiment_run_instances eri on erp.experiment_run_instance_id = eri.id JOIN main.experiment_runs er on eri.experiment_run_id = er.id WHERE er.uid = 'Multi-worker, multi-episode TT dummy run' GROUP BY erp.id ORDER BY ma.id DESC;
    Log many                        ${result.stderr}    ${result.stdout}
    Should be equal as strings      ${result.stdout}    2,10\n1,220
