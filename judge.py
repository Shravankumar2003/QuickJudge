import subprocess
import tempfile
import os
import time

# NOTE: This judge is a simplified evaluator for Python code only.
# It is NOT production-safe. For production, run each submission in an isolated container (Docker) or sandbox.

class JudgeResult:
    def __init__(self, status, time_ms=None, memory_kb=None, output=None, error=None):
        self.status = status
        self.time_ms = time_ms
        self.memory_kb = memory_kb
        self.output = output
        self.error = error

def run_python_code(code: str, input_data: str, time_limit_ms=1000):
    """Run python code with input_data. Returns JudgeResult.

    Security: This runs untrusted code on the host. Use containers or heavy sandboxing in real deployments.
    """
    with tempfile.TemporaryDirectory() as td:
        file_path = os.path.join(td, 'submission.py')
        with open(file_path, 'w') as f:
            f.write(code)

        cmd = ['python3', file_path]
        start = time.time()
        try:
            proc = subprocess.run(cmd, input=input_data.encode('utf-8'), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=time_limit_ms/1000)
            end = time.time()
            elapsed_ms = (end - start) * 1000
            stdout = proc.stdout.decode('utf-8')
            stderr = proc.stderr.decode('utf-8')
            if proc.returncode != 0:
                return JudgeResult('RUNTIME_ERROR', time_ms=elapsed_ms, output=stdout, error=stderr)
            return JudgeResult('OK', time_ms=elapsed_ms, output=stdout.strip())
        except subprocess.TimeoutExpired as e:
            return JudgeResult('TIME_LIMIT_EXCEEDED', time_ms=time_limit_ms, output='', error=str(e))
        except Exception as e:
            return JudgeResult('ERROR', time_ms=None, output='', error=str(e))

def evaluate_submission(code: str, test_cases: list, time_limit_ms=1000):
    """Evaluate code against multiple test_cases.

    test_cases: list of dicts with keys {input_text, expected_output}
    Returns aggregated status and details per test case.
    """
    results = []
    all_passed = True
    max_time = 0
    for tc in test_cases:
        res = run_python_code(code, tc['input_text'], time_limit_ms=time_limit_ms)
        passed = False
        if res.status == 'OK' and res.output is not None:
            expected = tc['expected_output'].strip()
            if res.output.strip() == expected:
                passed = True
        if not passed:
            all_passed = False
        if res.time_ms:
            max_time = max(max_time, res.time_ms)
        results.append({'status': res.status, 'time_ms': res.time_ms, 'output': res.output, 'error': res.error, 'passed': passed})

    final_status = 'ACCEPTED' if all_passed else 'WRONG_ANSWER'
    return {'final_status': final_status, 'max_time_ms': max_time, 'results': results}
