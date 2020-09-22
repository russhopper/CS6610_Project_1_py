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

        #split every 32
        n = 32
        output_array = [output_string[i:i+n] for i in range(0, len(output_string), n)]
        test_array = [test_string[i:i+n] for i in range(0, len(test_string), n)]

        # check if they are equal or not
        print(f"Testing: {test}")

        i = 0
        while i < len(test_array):
            is_equal = output_array[i] == test_array[i]
            print(f"Test: {test_array[i]} - Output: {output_array[i]} = {is_equal}")
            i += 1
        
        if output_string == test_string:
            print("Pass\n")
        else:
            #print(f"{output_string}\n!=\n{test_string}")
            print("Fail\n")


if __name__ == "__main__":
    test()
