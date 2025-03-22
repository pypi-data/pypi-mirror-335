from package_publishing_example import revcomp


def test_revcomp():
    test_cases = [["AT", "AT"], ["ACG", "CGT"], ["N", "N"], ["WS", "SW"]]
    for input, output in test_cases:
        assert revcomp(input) == output
