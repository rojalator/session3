# Testing Session3

Session3 includes automated integration tests that verify session management functionality with a real Quixote server.

## Running the Tests

To run the automated test suite:

```bash
cd test/
python3 run_tests.py
```

This will:

1. Start a Quixote test server with session3
2. Run automated HTTP-based tests
3. Log results to `test_results.log`
4. Shut down the server

**Test coverage includes:**

- Session creation and cookie handling
- Login/logout functionality
- Session persistence across requests
- Counter and custom session data
- Form token generation
- Session file deletion on logout
- Handling of missing session files
- `delete_old_sessions` functionality

## Manual Testing

For interactive manual testing, start the test server:

```bash
cd test/
python -m quixote run --app test_runner
```

Then visit http://localhost:8080/ in your browser to:

- See session status
- Login/logout
- Increment a counter
- Create form tokens
- Check session details

Use `--port` to change the port if needed:

```bash
python -m quixote run --app test_runner --port 9000
```

## Files

| File               | Description                                              |
|--------------------|----------------------------------------------------------|
| `run_tests.py`     | Main test runner (starts server, runs tests, shuts down) |
| `test_runner.py`   | Quixote app with session test endpoints                  |
| `test_results.log` | Test output log (generated after running tests)          |
