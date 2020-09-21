_tests = ["example1.o", "example2_mod.o",
          "example3.o", "example4.o", "example5.o"]
_output_folder = "output/"
_test_folder = "tests/"


def test():
    for test in _tests:
        # open and read output and test file
        f = open(_output_folder + test, "r")
        output_string = f.read()
        f = open(_test_folder + test, "r")
        test_string = f.read()

        # check if they are equal or not
        print(f"Testing: {test}")
        if output_string == test_string:
            print("Pass\n")
        else:
            print(f"{output_string}\n!=\n{test_string}")
            print("Fail\n")


if __name__ == "__main__":
    test()
