from junitparser import JUnitXml, Attr, Element


class FailureElement(Element):
    _tag = "failure"
    message = Attr()


def get_TestSuite_error_result(test_suite_name, name, error_msg):
    return {
        "suite": test_suite_name,
        "errors": 1,
        "failures": 0,
        "tests": 1,
        "details": [
            {
                "name": name,
                "failure_message": error_msg,
                "result": "failure",
            }
        ],
    }


def parse_tests_results(file):
    def parse_suite(suite):
        nonlocal success, results
        suite_results = {
            "suite": suite.name,
            "errors": suite.errors,
            "failures": suite.failures,
            "tests": suite.tests,
        }
        details = []
        for case in suite:
            case_details = {
                "name": case.name,
            }
            try:
                case_details["failure_message"] = case.child(FailureElement).message
                case_details["result"] = "failure"
                success = False
            except AttributeError:
                case_details["result"] = "success"
            details.append(case_details)
        suite_results["details"] = details
        results.append(suite_results)

    try:
        xml = JUnitXml.fromfile(file)

        results = []
        success = True
        # some xml files do not have the <testsuites> tag, just a single <tessuite>
        if xml._tag == "testsuite":
            # handle single suite
            suite = xml
            parse_suite(suite)
        elif xml._tag == "testsuites":
            # handle suites
            for suite in xml:
                parse_suite(suite)
        # else: TODO
        return results, success

    except Exception as e:
        print(f"[Exception in parse_tests_results] {e}")
        print("Test result xml could not be loaded, marking success as False")
        results = get_TestSuite_error_result(
            "unittest.suite.TestSuite",
            "Error parsing XML test results",
            f"The test may have timed out. Exception: {e}",
        )
        return results, None
