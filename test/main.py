# main.py
from llm import generator_instance
from dir1.test1 import some_function_in_test1
from dir1.dir2.test2 import some_function_in_test2

if __name__ == "__main__":
    # Optionally modify generator_instance if needed
    print(some_function_in_test1())
    print(some_function_in_test2())