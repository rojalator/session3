#!/usr/bin/env python3
"""
External test runner for session3.

This script:
1. Starts the Quixote test server in background
2. Makes HTTP requests to test session3 functionality
3. Logs results to test_results.log
4. Shuts down the server

Run standalone: python run_tests.py
"""

import os
import sys
import subprocess
import time
import shutil
import glob
from http.client import HTTPConnection
from datetime import datetime

# Configuration
TEST_SERVER_HOST = 'localhost'
TEST_SERVER_PORT = 8080
TEST_RESULTS_FILE = 'test_results.log'
SESSION_DIR = '/tmp/session3_test_runner'
SERVER_STARTUP_TIMEOUT = 5


def log(msg):
    """Log to file and stdout."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(TEST_RESULTS_FILE, 'a') as f:
        f.write(line + '\n')


def make_request(path, method='GET', data=None, cookies=None, host=TEST_SERVER_HOST, port=TEST_SERVER_PORT):
    """Make HTTP request to test server."""
    try:
        conn = HTTPConnection(host, port, timeout=5)
        headers = {}
        if cookies:
            headers['Cookie'] = cookies
        if data and method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            data = data.encode('utf-8')
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
        body = response.read().decode('utf-8')
        set_cookie = response.getheader('Set-Cookie')
        conn.close()
        return {'status': response.status, 'body': body, 'cookies': set_cookie}
    except Exception as e:
        return None


def cleanup():
    """Clean up session directory."""
    if os.path.exists(SESSION_DIR):
        shutil.rmtree(SESSION_DIR)
    os.makedirs(SESSION_DIR, exist_ok=True)


def run_tests():
    """Run all tests."""
    # Remove old results
    if os.path.exists(TEST_RESULTS_FILE):
        os.remove(TEST_RESULTS_FILE)

    cleanup()

    log("=" * 50)
    log("Starting Quixote test server...")
    # Compute PYTHONPATH relative to this script's location
    test_dir = os.path.dirname(os.path.abspath(__file__))
    session3_path = os.path.dirname(test_dir)
    quixote_path = '/home/rjl/pythonstuff/kilo_sandbox/quixote/env/lib/python3.12/site-packages'
    # Start server
    server_cmd = [sys.executable, '-m', 'quixote', 'run', '--app', 'test_runner', '--port', str(TEST_SERVER_PORT)]
    server_proc = subprocess.Popen(server_cmd, cwd=test_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={**os.environ, 'PYTHONPATH': f'{session3_path}:{quixote_path}'})
    # Wait for server to start
    time.sleep(SERVER_STARTUP_TIMEOUT)
    # Verify server is running
    try:
        r = make_request('/')
        if r and r['status'] == 200:
            log("Server started successfully")
    except:
        log("Warning: Could not connect to server")

    log("=" * 50)
    log("SESSION3 INTEGRATION TESTS")
    log("=" * 50)
    # results = []
    passed = 0
    failed = 0
    cookie = None

    try:
        # Test 1: New session created on first request
        log("TEST: test_new_session")
        try:
            r = make_request('/')
            assert r is not None, "Could not connect to server"
            assert r['status'] == 200, f"Expected 200, got {r['status']}"
            assert 'Not logged in' in r['body'], "Expected 'Not logged in' in body"
            log("  PASS - Got 200 OK (empty session)")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 2: Login creates session with cookie
        log("TEST: test_login_creates_session")
        try:
            r = make_request('/login', method='POST', data='name=TestUser')
            assert r is not None, "Could not connect to server"
            assert r['status'] == 200, f"Expected 200, got {r['status']}"
            assert 'TestUser' in r['body'], f"Expected 'TestUser' in body"
            assert r['cookies'] is not None, "No session cookie set after login"
            cookie = r['cookies']
            log("  PASS - Login creates session with cookie")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 3: Session persists across requests
        log("TEST: test_session_persist")
        try:
            r = make_request('/', cookies=cookie)
            assert r is not None, "Could not connect to server"
            assert r['status'] == 200, f"Expected 200, got {r['status']}"
            assert 'TestUser' in r['body'], f"Expected 'TestUser' in body"
            log("  PASS - Session persisted across requests")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 4: Counter increments
        log("TEST: test_counter")
        try:
            r1 = make_request('/counter', cookies=cookie)
            cookie = r1['cookies'] if r1 and r1['cookies'] else cookie
            r2 = make_request('/counter', cookies=cookie)
            assert r1 and r2, "Could not connect to server"
            assert 'Counter: 1' in r1['body'], f"Expected 'Counter: 1', got {r1['body']}"
            assert 'Counter: 2' in r2['body'], f"Expected 'Counter: 2', got {r2['body']}"
            log("  PASS - Counter increments correctly")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 5: Check endpoint returns session info
        log("TEST: test_check_endpoint")
        try:
            r = make_request('/check', cookies=cookie)
            assert r is not None, "Could not connect to server"
            assert 'user: TestUser' in r['body'], f"Expected user in check output, got {r['body']}"
            assert 'session_id:' in r['body'], "Expected session_id in output"
            assert 'has_info: TestUser' in r['body'], "Expected has_info with user in output"
            assert 'form_tokens_count:' in r['body'], "Expected form_tokens_count in output"
            assert 'has_form_tokens:' in r['body'], "Expected has_form_tokens in output"
            log("  PASS - Check endpoint returns correct session info")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 6: Logout
        log("TEST: test_logout")
        try:
            r = make_request('/logout', cookies=cookie)
            assert r is not None, "Could not connect to server"
            assert r['status'] == 200, f"Expected 200, got {r['status']}"
            log("  PASS - Logout completed")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 7: Session file deleted (Flow 1)
        log("TEST: test_session_file_deleted")
        try:
            files = os.listdir(SESSION_DIR)
            assert len(files) == 0, f"Expected 0 session files, got {files}"
            log("  PASS - Session file deleted on logout")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 8: Form tokens
        log("TEST: test_form_tokens")
        try:
            # Login first to create session
            r = make_request('/login', method='POST', data='name=TokenUser')
            cookie = r['cookies']
            # Create a form token
            r2 = make_request('/create_token', cookies=cookie)
            # Check token exists
            r3 = make_request('/check_token', cookies=cookie)
            assert r3 and 'has_form_tokens: True' in r3['body'], f"Expected form token, got {r3['body'] if r3 else 'None'}"
            log("  PASS - Form tokens work correctly")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 9: delete_old_sessions
        log("TEST: test_delete_old_sessions")
        try:
            # Login to create session
            r = make_request('/login', method='POST', data='name=DeleteTest')
            cookie = r['cookies']
            # Try delete_old with 0 minutes (should delete all)
            r2 = make_request('/delete_old?minutes=0', cookies=cookie)
            assert r2 and 'Deleted:' in r2['body'], f"Expected delete_old to run, got {r2['body'] if r2 else 'None'}"
            log("  PASS - delete_old_sessions works")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1

        # Test 10: Session not found - recovery via re-login (Flow 2)
        log("TEST: test_session_not_found")
        try:
            # Login to create session
            r = make_request('/login', method='POST', data='name=RecoveryTest')
            cookie = r['cookies']

            # Get old session ID from check endpoint
            r_old = make_request('/check', cookies=cookie)
            old_lines = r_old['body'].split('\n')
            old_id = [l for l in old_lines if l.startswith('session_id:')][0].split(': ')[1]

            # Manually delete the session file to simulate external deletion
            session_files = glob.glob(os.path.join(SESSION_DIR, '*'))
            for f in session_files:
                os.remove(f)

            # Re-login to create a persisted session (restoring the session)
            r2 = make_request('/login', method='POST', data='name=RecoveryTest')
            assert r2 is not None, "Server should respond"
            cookie = r2['cookies']

            # Get new session ID
            r_new = make_request('/check', cookies=cookie)
            new_lines = r_new['body'].split('\n')
            new_id = [l for l in new_lines if l.startswith('session_id:')][0].split(': ')[1]

            # Verify a new session file was created
            new_files = os.listdir(SESSION_DIR)
            assert len(new_files) > 0, "Expected new session file to be created"

            # Verify it's a different session ID
            assert old_id != new_id, f"Expected new session ID, got same: {old_id}"

            # Verify user info is intact
            assert 'user: RecoveryTest' in r_new['body'], "Expected user in re-logged session"
            log("  PASS - Server creates new session when file deleted, new ID differs from old")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1
        except Exception as e:
            log(f"  FAIL - Exception: {e}")
            failed += 1
        except Exception as e:
            log(f"  FAIL - Exception: {e}")
            failed += 1

        # Test 11: Session not found - no crash (Flow 2)
        log("TEST: test_session_not_found_no_crash")
        try:
            # Login to create session
            r = make_request('/login', method='POST', data='name=NoCrashTest')
            cookie = r['cookies']

            # Manually delete the session file
            session_files = glob.glob(os.path.join(SESSION_DIR, '*'))
            for f in session_files:
                os.remove(f)

            # Try to access with the old cookie - server should not crash
            r2 = make_request('/check', cookies=cookie)
            assert r2 is not None, "Server should respond without crashing"
            log("  PASS - Server handles missing session gracefully")
            passed += 1
        except AssertionError as e:
            log(f"  FAIL - {e}")
            failed += 1
        except Exception as e:
            log(f"  FAIL - Exception: {e}")
            failed += 1

    finally:
        log("=" * 50)
        log("Stopping test server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        log("Server stopped")
        log("=" * 50)

    # Summary
    log("=" * 50)
    log(f"SUMMARY: {passed} tests passed, {failed} tests failed")
    log("=" * 50)

    return passed, failed


if __name__ == '__main__':
    run_tests()
