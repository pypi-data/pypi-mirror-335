import pytest
import json
from log import BaseLog
from log import LogLevel

@pytest.fixture
def base_log(tmp_path):
    log_folder = tmp_path / "logs"
    log_file = "test_log.log"
    return BaseLog(str(log_folder), log_file)

def test_start_logging(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    base_log.start("Test Start")
    mock_logger.assert_called_with("*** Test Start ***")

def test_finish_logging(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    base_log.start_time = 0  # Simulate a start time
    base_log.finish("Test Finish")
    mock_logger.assert_called()
    assert "Finish" in mock_logger.call_args[0][0]

def test_info_logging(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    base_log.info("Test Info", LogLevel.LEVEL_1)
    mock_logger.assert_called_with("\t- test Info")

def test_error_logging_with_exception(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "error")
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        base_log.error("Error occurred", exc_info=e)
    
    assert "- error occurred" in mock_logger.call_args[0][0]
    assert "Exception: Test exception" in mock_logger.call_args[0][0]

def test_config_logging_yaml(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    yaml_config = "key: value\nnumber: 123"
    base_log.config(yaml_config)
    
    mock_logger.assert_called()
    logged_config = json.loads(mock_logger.call_args[0][0].split("\n", 1)[1])
    assert logged_config["key"] == "value"
    assert logged_config["number"] == 123

def test_config_logging_dict(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    dict_config = {"key": "value", "number": 123}
    base_log.config(dict_config)
    
    mock_logger.assert_called()
    logged_config = json.loads(mock_logger.call_args[0][0].split("\n", 1)[1])
    assert logged_config == dict_config

def test_line_logging(mocker, base_log):
    mock_logger = mocker.patch.object(base_log.logger, "info")
    base_log.line()
    mock_logger.assert_called_with("-" * 150)
