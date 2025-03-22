from helper_lib.print_helpers import slow_print, slow_print_header, slow_print_error

def test_slow_print():
    slow_print("test")
    slow_print("test", newline=True)
    slow_print("test", delay=0.5)
    slow_print_error("test")
    slow_print_error("test", delay=0.5)
    slow_print_header("test")
    slow_print_header("test", delay=0.5)
