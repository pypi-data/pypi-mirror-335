#!/usr/bin/env python3
"""
SafeRun: A highly secure sandbox for executing Python code in an isolated environment.

This library can be imported in your projects:
    from SafeRun import UltraSecureSandbox

It can also be executed as a module:
    python -m SafeRun <file.py> [--time TIME] [--memory MEMORY] [--chroot CHROOT_DIR]
"""

import ast
import os
import sys
import multiprocessing
import traceback
import time
import platform

# Attempt to import resource and seccomp (only available on Unix)
if platform.system() != "Windows":
    import resource
else:
    resource = None

try:
    import seccomp
    HAS_SECCOMP = True
except ImportError:
    HAS_SECCOMP = False


class SandboxException(Exception):
    """Exception for errors in the SafeRun sandbox."""
    pass


def check_ast(node):
    """
    Perform a comprehensive AST check on the provided code node.
    
    Disallowed:
      - Any import or import-from statements.
      - Calls to dangerous functions: eval, exec, __import__, open, compile, input, globals, locals, vars, dir.
      - Access to attributes that start and end with '__' (e.g., __globals__).
      - Lambda expressions.
    """
    dangerous_calls = {'eval', 'exec', '__import__', 'open', 'compile', 'input', 'globals', 'locals', 'vars', 'dir'}
    for child in ast.walk(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            raise SandboxException("Import statements are not allowed.")
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id in dangerous_calls:
                raise SandboxException(f"Call to {child.func.id} is not allowed.")
        if isinstance(child, ast.Attribute):
            attr = child.attr
            if attr.startswith("__") and attr.endswith("__"):
                raise SandboxException(f"Access to {attr} is not allowed.")
        if isinstance(child, ast.Lambda):
            raise SandboxException("Lambda expressions are not allowed.")
    return True


def drop_privileges(uid=65534, gid=65534):
    """
    Drop privileges by setting the UID and GID.
    
    Default values (65534) usually correspond to the 'nobody' user on Unix systems.
    This function is only used on Unix-like systems.
    """
    if platform.system() != "Windows":
        os.setgid(gid)
        os.setuid(uid)
    else:
        # On Windows, dropping privileges is not applicable.
        pass


def setup_seccomp_filter():
    """
    Set up a seccomp filter if the seccomp library is available and the OS supports it.
    Only applicable on Unix-like systems.
    """
    if platform.system() == "Windows" or not HAS_SECCOMP:
        return
    try:
        filt = seccomp.SyscallFilter(defaction=seccomp.SCMP_ACT_KILL)
        safe_syscalls = [
            "read", "write", "exit", "exit_group", "sigreturn",
            "rt_sigreturn", "rt_sigprocmask", "brk", "mmap", "munmap",
            "close", "futex", "nanosleep", "getpid"
        ]
        for syscall in safe_syscalls:
            try:
                filt.add_rule(seccomp.SCMP_ACT_ALLOW, syscall)
            except Exception:
                pass
        filt.load()
    except Exception as e:
        raise SandboxException(f"Seccomp setup error: {e}")


def sandbox_target(queue, code, safe_globals, time_limit, memory_limit, chroot_dir):
    """
    Target function for the sandboxed process.
    This function is defined at the top-level so that it can be pickled by multiprocessing (especially on Windows).
    """
    try:
        # Apply resource limits only on Unix-like systems
        if platform.system() != "Windows" and resource is not None:
            resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
        
        # On Unix, apply chroot and privilege dropping
        if platform.system() != "Windows":
            os.chroot(chroot_dir)
            os.chdir("/")
            drop_privileges()
            setup_seccomp_filter()
        else:
            # On Windows, you might add alternative isolation methods if needed.
            pass

        compiled_code = compile(code, "<sandbox>", "exec")
        exec(compiled_code, safe_globals)
        queue.put("Execution finished successfully.")
    except Exception:
        queue.put(traceback.format_exc())


def run_in_sandbox(code, safe_globals, time_limit, memory_limit, chroot_dir):
    """
    Execute the given code in a sandboxed environment using different techniques
    based on the operating system.
    """
    queue = multiprocessing.Queue()
    # Pass the target function as a top-level function (sandbox_target)
    p = multiprocessing.Process(target=sandbox_target, args=(queue, code, safe_globals, time_limit, memory_limit, chroot_dir))
    p.start()
    p.join(time_limit + 2)
    if p.is_alive():
        p.terminate()
        return "Error: Timeout reached."
    if not queue.empty():
        return queue.get()
    return "Error: No response from sandbox."


class UltraSecureSandbox:
    """
    UltraSecureSandbox provides a highly secure environment for executing Python code.

    Features:
      - Comprehensive AST checking to prevent dangerous code patterns.
      - CPU and memory usage restrictions (Unix only).
      - Execution in a separate process.
      - Filesystem isolation using chroot (Unix only).
      - Privilege dropping (Unix only).
      - Optional seccomp syscall filtering (Unix only).
      
    Usage:
        sandbox = UltraSecureSandbox(time_limit=2, memory_limit_mb=50, chroot_dir="/tmp/sandbox_chroot")
        sandbox.execute_file("example.py")
    """
    def __init__(self, allowed_builtins=None, time_limit=2, memory_limit_mb=50, chroot_dir="/tmp/sandbox_chroot"):
        if allowed_builtins is None:
            allowed_builtins = {
                'print': print,
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                'range': range,
                'len': len,
            }
        self.safe_globals = {"__builtins__": allowed_builtins}
        self.time_limit = time_limit
        self.memory_limit = memory_limit_mb * 1024 * 1024  # Convert MB to bytes
        self.chroot_dir = chroot_dir

    def execute_code(self, code):
        try:
            tree = ast.parse(code, mode='exec')
            check_ast(tree)
        except SandboxException as se:
            print(f"Sandbox AST error: {se}")
            return
        except Exception as e:
            print(f"AST parse error: {e}")
            return

        result = run_in_sandbox(code, self.safe_globals, self.time_limit, self.memory_limit, self.chroot_dir)
        print(result)

    def execute_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            self.execute_code(code)
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"File read error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="SafeRun: Execute Python code securely in an isolated environment."
    )
    parser.add_argument("file", help="Path to the Python file to execute securely.")
    parser.add_argument("--time", type=int, default=2, help="CPU time limit in seconds (Unix only).")
    parser.add_argument("--memory", type=int, default=50, help="Memory limit in MB (Unix only).")
    parser.add_argument("--chroot", type=str, default="/tmp/sandbox_chroot",
                        help="Chroot directory (Unix only; must be pre-configured and secured).")
    args = parser.parse_args()
    sandbox = UltraSecureSandbox(time_limit=args.time, memory_limit_mb=args.memory, chroot_dir=args.chroot)
    sandbox.execute_file(args.file)


# Allow both import and command-line execution.
if __name__ == "__main__":
    main()
