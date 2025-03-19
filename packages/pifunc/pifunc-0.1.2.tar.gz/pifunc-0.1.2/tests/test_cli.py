import json
import pytest
from click.testing import CliRunner
from pifunc.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_help(runner):
    """Test CLI help command"""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'pifunc CLI tool' in result.output

def test_call_command_help(runner):
    """Test call command help"""
    result = runner.invoke(cli, ['call', '--help'])
    assert result.exit_code == 0
    assert 'Call a service with the specified arguments' in result.output

def test_call_with_http_protocol(runner, requests_mock):
    """Test calling a service with HTTP protocol"""
    mock_response = {'result': 8}
    requests_mock.post(
        'http://localhost:8080/api/add',
        json=mock_response
    )
    
    result = runner.invoke(cli, [
        'call',
        'add',
        '--protocol', 'http',
        '--args', '{"a": 5, "b": 3}'
    ])
    
    assert result.exit_code == 0
    assert json.loads(result.output.strip()) == mock_response

def test_call_with_invalid_json(runner):
    """Test calling with invalid JSON arguments"""
    result = runner.invoke(cli, [
        'call',
        'add',
        '--args', 'invalid json'
    ])
    
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_call_with_unsupported_protocol(runner):
    """Test calling with unsupported protocol"""
    result = runner.invoke(cli, [
        'call',
        'add',
        '--protocol', 'unsupported',
        '--args', '{}'
    ])
    
    assert result.exit_code == 0
    assert 'Protocol unsupported not yet implemented' in result.output

def test_call_http_service_failure(runner, requests_mock):
    """Test handling HTTP service failure"""
    requests_mock.post(
        'http://localhost:8080/api/add',
        status_code=500
    )
    
    result = runner.invoke(cli, [
        'call',
        'add',
        '--protocol', 'http',
        '--args', '{"a": 5, "b": 3}'
    ])
    
    assert result.exit_code != 0
    assert 'Error' in result.output
