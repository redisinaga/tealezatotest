"""Unit tests for the legacy billing wrapper; no real shell is invoked."""

import subprocess
import unittest
from unittest.mock import call, patch

from legacy_billing import charge


class ChargeTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("legacy_billing.subprocess.check_output", autospec=True)
        self.addCleanup(patcher.stop)
        self.check_output = patcher.start()

    def test_forwards_customer_input_without_trimming_or_normalizing(self):
        for customer_input in ("customer-123", "", "  customer  ", "客户 café"):
            with self.subTest(customer_input=customer_input):
                self.check_output.reset_mock()

                charge(customer_input)

                self.check_output.assert_called_once_with(
                    "echo " + customer_input, shell=True
                )

    def test_returns_subprocess_bytes_without_decoding_or_stripping(self):
        for output in (b"customer-123\n", b"", b"\n", b"  customer  \n", b"\xff\x00\n"):
            with self.subTest(output=output):
                self.check_output.return_value = output

                result = charge("customer-123")

                self.assertIsInstance(result, bytes)
                self.assertEqual(result, output)

    def test_propagates_nonzero_exit_with_output_and_error_details(self):
        error = subprocess.CalledProcessError(
            7, "echo customer-123", output=b"partial output\n", stderr=b"failure\n"
        )
        self.check_output.side_effect = error

        with self.assertRaises(subprocess.CalledProcessError) as raised:
            charge("customer-123")

        self.assertIs(raised.exception, error)
        self.check_output.assert_called_once()

    def test_propagates_process_start_failures_without_retrying(self):
        for error in (FileNotFoundError("shell unavailable"), PermissionError("denied")):
            with self.subTest(error=type(error).__name__):
                self.check_output.reset_mock()
                self.check_output.side_effect = error

                with self.assertRaises(OSError) as raised:
                    charge("customer-123")

                self.assertIs(raised.exception, error)
                self.check_output.assert_called_once()

    def test_rejects_non_string_input_before_starting_a_process(self):
        for customer_input in (None, 0, False, b"customer-123", [], {}):
            with self.subTest(input_type=type(customer_input).__name__):
                with self.assertRaises(TypeError):
                    charge(customer_input)

                self.check_output.assert_not_called()

    def test_each_call_uses_its_own_input_and_subprocess_result(self):
        self.check_output.side_effect = [b"first\n", b"second\n"]

        self.assertEqual(charge("first"), b"first\n")
        self.assertEqual(charge("second"), b"second\n")

        self.assertEqual(
            self.check_output.call_args_list,
            [call("echo first", shell=True), call("echo second", shell=True)],
        )

    def test_a_failed_call_does_not_prevent_a_later_success(self):
        error = subprocess.CalledProcessError(1, "echo customer-123")
        self.check_output.side_effect = [error, b"customer-123\n"]

        with self.assertRaises(subprocess.CalledProcessError):
            charge("customer-123")

        self.assertEqual(charge("customer-123"), b"customer-123\n")
        self.assertEqual(self.check_output.call_count, 2)


if __name__ == "__main__":
    unittest.main()
