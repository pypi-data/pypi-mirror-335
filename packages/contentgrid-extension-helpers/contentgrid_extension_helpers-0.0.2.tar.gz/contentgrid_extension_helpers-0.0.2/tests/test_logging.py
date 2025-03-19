import json
import logging
import pytest

from contentgrid_extension_helpers.logging.json_logging import (
    XenitJsonFormatter, 
    setup_json_logging
)

# Modify the logging setup to be more compatible with caplog
def test_caplog_compatibility(caplog : pytest.LogCaptureFixture):
    # Set the logging level for caplog
    caplog.set_level(logging.DEBUG)

    # Create a logger with a standard handler alongside the JSON formatter
    logger = logging.getLogger()
    # Add JSON formatter handler
    json_handler = logging.StreamHandler()
    json_handler.setLevel(logging.DEBUG)
    json_formatter = XenitJsonFormatter(component='test-component')
    json_handler.setFormatter(json_formatter)
    logger.addHandler(json_handler)
    logger.addHandler(caplog.handler)

    # Log some messages
    logging.debug('Debug message')
    logging.info('Info message')
    logging.warning('Warning message')
    logging.error('Error message')

    # Check caplog records
    assert len(caplog.records) == 4
    
    # Verify log messages
    log_messages = [record.getMessage() for record in caplog.records]
    assert log_messages == [
        'Debug message', 
        'Info message', 
        'Warning message', 
        'Error message'
    ]

def test_json_formatter():
    # Create a log record
    logger = logging.getLogger('test')
    record = logger.makeRecord(
        name='test', 
        level=logging.INFO, 
        fn='test_file.py', 
        lno=10, 
        msg='Test message', 
        args=(), 
        exc_info=None
    )

    # Create formatter
    formatter = XenitJsonFormatter(component='test-component')
    
    # Format the record
    log_output = formatter.format(record)
    
    # Parse JSON output
    log_data = json.loads(log_output)
    
    # Assertions
    assert log_data['component'] == 'test-component'
    assert log_data['shortMessage'] == 'Test message'
    assert log_data['severity'] == 'INFO'
    assert 'timestamp' in log_data
    assert 'time' in log_data

def test_setup_json_logging(caplog : pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO)
    setup_json_logging(
        component='test-additional', 
        additional_keys={'correlation_id': 'correlation_id'}
    )
    logging.getLogger().addHandler(caplog.handler)

    # Log a message
    logging.info('Test logging setup')
    # Check captured logs
    assert len(caplog.get_records(when="call")) > 0
    log_record = caplog.records[0]
    
    # Verify log record attributes
    assert log_record.getMessage() == 'Test logging setup'

def test_logger_with_additional_keys():
    # Create logger with additional keys
    setup_json_logging(
        component='test-additional', 
        additional_keys={'corr_id': 'correlation_id'}
    )
    
    # Log with extra data
    logging.info('Test message', extra={'correlation_id': '123'})
    
    # Capture log output
    log_handler = logging.getLogger().handlers[0]
    log_output = log_handler.format(logging.getLogger().makeRecord(
        name='test-additional', 
        level=logging.INFO, 
        fn='test_file.py', 
        lno=10, 
        msg='Test message', 
        args=(), 
        exc_info=None,
        extra={'correlation_id': '123'}
    ))
    
    # Parse JSON output
    log_data = json.loads(log_output)
    
    # Verify additional key
    assert log_data.get('corr_id') == '123'

def test_error_logging(caplog):
    # Set caplog level to capture all logs
    caplog.set_level(logging.DEBUG)
    
    # Setup JSON logging
    setup_json_logging(component='test-error')

    logger = logging.getLogger()
    logger.addHandler(caplog.handler)
    
    # Log an error with exception
    try:
        raise ValueError("Test error")
    except ValueError:
        # Use logging.exception to ensure proper record creation
        logging.exception("An error occurred")
    
    # Check captured logs
    assert len(caplog.records) > 0
    
    # Get the last record (which should be the error)
    error_record = caplog.records[-1]
    
    # Verify error record attributes
    assert error_record.levelno == logging.ERROR
    assert "Test error" in str(error_record.exc_info[1])
    
    # Optionally, verify the JSON formatting
    formatter = XenitJsonFormatter(component='test-error')
    log_output = formatter.format(error_record)
    log_data = json.loads(log_output)
    
    assert log_data['severity'] == 'ERROR'
    assert 'fullMessage' in log_data
    assert "Test error" in log_data['fullMessage']
    assert "Traceback" in log_data['fullMessage']
