import os
import subprocess
import logging
import shlex
from datetime import datetime
import shutil
from pathlib import Path
import re
from .database import log_run
from .config_parser import (
    load_config,
    get_test_config,
    get_base_command,
    get_test_names,
    process_params,
    process_environment
)
import concurrent.futures

# Base logs directory
BASE_LOG_DIR = "test_runs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)


def create_run_directory():
    """Create a timestamped directory for this test run"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_LOG_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def build_command(base_command, params):
    """
    Build a command list for subprocess execution.
    
    Args:
        base_command: The base command string
        params: List of parameters
        
    Returns:
        List of command parts suitable for subprocess.run
    """
    if not base_command:
        raise ValueError("Base command cannot be empty")
    
    cmd_parts = [base_command]
    
    # Add parameters if they exist
    if params:
        cmd_parts.extend(params)
        
    return cmd_parts


def execute_command(cmd_parts, env, timeout=None):
    """
    Execute a command and return the result.
    
    Args:
        cmd_parts: List of command parts
        env: Environment dictionary
        timeout: Maximum time in seconds to wait for the command to complete
                (None means wait indefinitely)
        
    Returns:
        CompletedProcess object with stdout, stderr, and returncode
    """
    try:
        # Use a custom approach for Python commands to prevent warning-related issues
        is_python_cmd = cmd_parts[0].endswith('python') or cmd_parts[0].endswith('python3')
        
        if is_python_cmd:
            # Create a temporary file to capture stderr
            stderr_file = None
            
            try:
                # Redirect stderr to a file and then read it back after execution
                import tempfile
                stderr_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
                stderr_path = stderr_file.name
                stderr_file.close()
                
                # Run process with stderr redirected to file
                process = subprocess.Popen(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=open(stderr_path, 'w'),
                    env=env,
                    text=True
                )
                
                # Wait for process to complete, with timeout
                try:
                    stdout, _ = process.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    return subprocess.CompletedProcess(
                        args=cmd_parts,
                        returncode=124,
                        stdout="Command timed out after {} seconds".format(timeout),
                        stderr="Process was killed due to timeout"
                    )
                
                # Read stderr from file after process completes
                with open(stderr_path, 'r') as f:
                    stderr = f.read()
                
                # Create a CompletedProcess object manually
                return subprocess.CompletedProcess(
                    args=cmd_parts,
                    returncode=process.returncode,
                    stdout=stdout,
                    stderr=stderr
                )
                
            finally:
                # Clean up temporary file
                if stderr_file:
                    import os
                    try:
                        os.unlink(stderr_path)
                    except:
                        pass
        
        # For non-Python commands, use the regular subprocess.run
        result = subprocess.run(
            cmd_parts, 
            capture_output=True, 
            text=True, 
            env=env,
            shell=False,
            timeout=timeout
        )
        return result
        
    except subprocess.TimeoutExpired as e:
        # Create a CompletedProcess-like object for timeout errors
        return subprocess.CompletedProcess(
            args=cmd_parts,
            returncode=124,
            stdout=f"Command timed out after {timeout} seconds",
            stderr=str(e)
        )


def create_log_file(run_dir, test_name, start_time, cmd_parts, env_vars, result):
    """
    Create a log file with test execution details.
    """
    success = result.returncode == 0
    status_str = "PASS" if success else "FAIL"
    start_time_formatted = start_time.strftime("%Y%m%d_%H%M%S")
    
    # Create a descriptive log filename
    log_filename = f"{start_time_formatted}_{test_name}_{status_str}.log"
    log_file = os.path.join(run_dir, log_filename)
    
    with open(log_file, "w") as log:
        log.write(f"Test: {test_name}\n")
        log.write(f"Status: {'SUCCESS' if success else 'FAILURE'}\n")
        
        # Write the actual command that was run
        cmd_str = ' '.join(cmd_parts)
        log.write(f"Command: {cmd_str}\n")
        
        # Include environment variables in the log
        if env_vars:
            log.write("Environment:\n")
            for key, value in env_vars.items():
                log.write(f"  {key}={value}\n")
        
        log.write(f"Return code: {result.returncode}\n")
        log.write(f"Start time: {start_time}\n")
        log.write(f"End time: {datetime.utcnow()}\n\n")
        log.write(f"--- STDOUT ---\n")
        log.write(result.stdout)
        if result.stderr:
            log.write("\n\n--- STDERR ---\n")
            log.write(result.stderr)
    
    return log_file


def create_exception_log(run_dir, test_name, start_time, exception):
    """
    Create a log file for an exception during test execution.
    """
    start_time_formatted = start_time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"{start_time_formatted}_{test_name}_EXCEPTION.log"
    log_file = os.path.join(run_dir, log_filename)
    
    with open(log_file, "w") as log:
        log.write(f"Test: {test_name}\n")
        log.write(f"Status: EXCEPTION\n")
        log.write(f"Start time: {start_time}\n")
        log.write(f"End time: {datetime.utcnow()}\n\n")
        log.write(f"--- ERROR ---\n")
        log.write(str(exception))
    
    return log_file


def process_test_result(result, success):
    """
    Process test result to extract error traces and failure information.
    
    A test is only considered failed if the return code is non-zero.
    Warnings that appear in stderr but don't cause a non-zero exit code
    will be logged but won't cause the test to be marked as failed.
    """
    if success:
        # If the command exited with code 0, it's a success even if stderr has content
        return None, None
    
    # If we get here, the command had a non-zero exit code (actual failure)
    stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    
    error_message = f"Command failed with return code {returncode}"
    
    # Extract the most relevant error info from stderr if available
    error_trace = stderr.split("\n")[-3:] if stderr else None
    
    if not error_trace:
        error_trace = [error_message]
        
    failure = stderr if stderr else error_message
    
    return error_trace, failure


def run_single_test(config_path, test_name, run_dir):
    """
    Run a single test from a configuration file.
    """
    # Load configuration
    config = load_config(config_path)
    test_config = get_test_config(config, test_name)
    
    # Validate test configuration
    if not test_config or not isinstance(test_config, dict):
        return {
            "config": test_name,
            "success": False,
            "error_trace": ["Test configuration not found or invalid"],
            "log_file": None
        }
    
    # Start timing
    start_time = datetime.utcnow()
    
    try:
        # Get base command and parameters
        base_command = get_base_command(config, test_config)
        if not base_command:
            raise ValueError(f"No base command specified for test: {test_name}")
        
        params = process_params(test_config)
        
        # Setup environment variables
        env = os.environ.copy()
        env_vars = process_environment(test_config)
        env.update(env_vars)
        
        # Get timeout from test config or use default
        # A default of None means wait indefinitely
        timeout = test_config.get('timeout', None)
        if timeout is not None:
            try:
                timeout = int(timeout)
            except (ValueError, TypeError):
                # If timeout is not a valid integer, use None (wait indefinitely)
                timeout = None
        
        # Build and execute command
        cmd_parts = build_command(base_command, params)
        result = execute_command(cmd_parts, env, timeout=timeout)
        
        # Special handling for timeout result
        if result.returncode == 124 and "timed out" in result.stdout:
            success = False
            error_trace = [f"Command timed out after {timeout} seconds"]
            failure = f"Timeout after {timeout} seconds"
        else:
            # Determine success/failure based on return code only
            success = result.returncode == 0
            error_trace, failure = process_test_result(result, success)
        
        # Create log file
        log_file = create_log_file(run_dir, test_name, start_time, cmd_parts, env_vars, result)
        
    except Exception as e:
        success = False
        error_trace = str(e).split("\n")
        failure = str(e)
        log_file = create_exception_log(run_dir, test_name, start_time, e)
    
    # Record end time and log the run
    end_time = datetime.utcnow()
    
    cmd_str = ' '.join(cmd_parts) if 'cmd_parts' in locals() else "Command generation failed"
    log_run(test_name, test_name, cmd_str, success, start_time, end_time, log_file, error_trace, failure)
    
    # Return result information
    result_info = {
        "config": test_name, 
        "success": success, 
        "log_file": log_file, 
        "error_trace": error_trace if not success else None
    }
    
    return result_info


def run_tests(config_path, run_dir, max_workers=4):
    """
    Run multiple tests in parallel using ThreadPoolExecutor.
    
    Ensures all tests complete before returning, with improved error handling 
    and progress tracking for long-running tests.
    """
    config = load_config(config_path)
    test_names = get_test_names(config)
    
    if not test_names:
        print("No tests found in the configuration file.")
        return []
    
    results = []
    pending_count = len(test_names)
    completed_count = 0
    
    print(f"Starting {pending_count} tests with {max_workers} parallel workers")
    
    # Use ThreadPoolExecutor to run tests in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all test jobs to the thread pool
        future_to_test = {
            executor.submit(run_single_test, config_path, test_name, run_dir): test_name 
            for test_name in test_names
        }
        
        # Track which tests are still running
        running_tests = set(test_names)
        
        try:
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_test):
                test_name = future_to_test[future]
                running_tests.remove(test_name)
                completed_count += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    status = "Succeeded" if result["success"] else "Failed"
                    print(f"Test '{test_name}' {status} [{completed_count}/{pending_count} completed]")
                    
                    # Print remaining tests every 5 completions or when only a few remain
                    if running_tests and (completed_count % 5 == 0 or len(running_tests) <= 3):
                        print(f"Still running: {', '.join(running_tests)}")
                        
                except Exception as e:
                    print(f"Error running test '{test_name}': {e}")
                    results.append({
                        "config": test_name,
                        "success": False,
                        "error_trace": [str(e)],
                        "log_file": None
                    })
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt. Cancelling pending tests...")
            
            # Attempt to cancel any pending futures
            for future in future_to_test:
                future.cancel()
            
            # Wait with a timeout to allow for cleanup
            # This is a best-effort attempt to avoid process orphaning
            executor.shutdown(wait=True, cancel_futures=True)
            
            # Include the interrupted tests in results
            for test_name in running_tests:
                results.append({
                    "config": test_name,
                    "success": False,
                    "error_trace": ["Test was interrupted"],
                    "log_file": None
                })
            
            print(f"Interrupted with {len(running_tests)} tests still running")
            
        except Exception as e:
            print(f"Unexpected error in test execution: {e}")
            # Ensure we don't lose track of running tests in case of errors
            for test_name in running_tests:
                if not any(r["config"] == test_name for r in results):
                    results.append({
                        "config": test_name,
                        "success": False,
                        "error_trace": [f"Test execution error: {str(e)}"],
                        "log_file": None
                    })
    
    # Final verification that we have a result for every test
    result_test_names = {r["config"] for r in results}
    for test_name in test_names:
        if test_name not in result_test_names:
            print(f"Warning: No result recorded for test '{test_name}', marking as failed")
            results.append({
                "config": test_name,
                "success": False,
                "error_trace": ["Test result was not properly recorded"],
                "log_file": None
            })
    
    print(f"All {len(test_names)} tests completed execution")
    return results


def calculate_summary(results):
    """
    Calculate test summary statistics.
    """
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    success_percent = (successful / total) * 100 if total > 0 else 0
    failing_tests = [r for r in results if not r["success"]]
    
    return successful, total, success_percent, failing_tests


def print_summary(successful, total, success_percent, failing_tests):
    """
    Print test summary to console.
    """
    print("\n=== TEST SUMMARY ===")
    print(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)")
    
    if failing_tests:
        print("\nFailing tests:")
        for test in failing_tests:
            print(f"- {test['config']}")
            if test.get("error_trace"):
                error = test["error_trace"] if isinstance(test["error_trace"], list) else [test["error_trace"]]
                for line in error:
                    if line:
                        print(f"  {line}")


def determine_output_path(output_path, run_dir):
    """
    Determine the final output path for the test report.
    """
    if not output_path:
        output_path = os.path.join(run_dir, "test_report.txt")
    elif os.path.dirname(output_path) == '':
        output_path = os.path.join(run_dir, output_path)
    
    return output_path


def write_report(output_path, successful, total, success_percent, results):
    """
    Write test report to file.
    """
    with open(output_path, "w") as f:
        f.write(f"Test Summary\n")
        f.write(f"============\n")
        f.write(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)\n\n")
        
        f.write("Test Results:\n")
        for result in results:
            status = "PASS" if result["success"] else "FAIL"
            f.write(f"{result['config']}: {status}\n")
            if not result["success"] and result.get("error_trace"):
                error = result["error_trace"] if isinstance(result["error_trace"], list) else [result["error_trace"]]
                for line in error:
                    if line:
                        f.write(f"  Error: {line}\n")
        
        f.write("\nLog Files:\n")
        for result in results:
            if result.get("log_file"):
                # Get the base filename only
                log_filename = os.path.basename(result["log_file"])
                f.write(f"{result['config']}: {log_filename}\n")


def create_latest_symlink(run_dir):
    """
    Create or update the 'latest' symlink to point to the most recent test run.
    """
    latest_link = os.path.join(BASE_LOG_DIR, "latest")
    
    # Remove existing link/directory
    if os.path.exists(latest_link):
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        else:
            shutil.rmtree(latest_link)
    
    try:
        # Create relative symlink on UNIX systems
        os.symlink(os.path.basename(run_dir), latest_link)
    except (OSError, AttributeError):
        # On Windows or if symlinks aren't supported, create a directory with copies
        os.makedirs(latest_link, exist_ok=True)
        for file in os.listdir(run_dir):
            src = os.path.join(run_dir, file)
            dst = os.path.join(latest_link, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)


def run_test_from_cli(config_path, output_path=None, max_workers=4):
    """
    Run tests from CLI using thread pool for parallelism.
    """
    # Create a unique directory for this test run
    run_dir = create_run_directory()
    print(f"Launching tests from {config_path}")
    print(f"Test run directory: {run_dir}")
    
    # Copy the config file to the run directory for reference
    config_filename = os.path.basename(config_path)
    shutil.copy2(config_path, os.path.join(run_dir, config_filename))
    
    # Run the tests
    results = run_tests(config_path, run_dir, max_workers=max_workers)
    
    # Calculate and print summary
    successful, total, success_percent, failing_tests = calculate_summary(results)
    print_summary(successful, total, success_percent, failing_tests)
    
    # Determine output path and write report
    final_output_path = determine_output_path(output_path, run_dir)
    write_report(final_output_path, successful, total, success_percent, results)
    print(f"Report written to {final_output_path}")
    
    # Create a symlink to the latest run for convenience
    create_latest_symlink(run_dir)
    
    return results, run_dir
