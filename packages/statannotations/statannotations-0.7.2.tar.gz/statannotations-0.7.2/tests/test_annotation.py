import unittest

from statannotations.Annotation import Annotation
from statannotations.stats.StatResult import StatResult


class TestAnnotation(unittest.TestCase):
    def test_text_string(self):
        annotation_text = "p=0.05"
        annotation = Annotation(("group1", "group2"),
                                annotation_text)
        self.assertEqual(annotation.text, annotation_text)
        self.assertEqual(annotation.formatted_output, annotation_text)

    def test_missing_formatter(self):
        res = StatResult("Custom test", None, pval=0.05, stat=None,
                         stat_str=None)
        with self.assertRaisesRegex(ValueError, "PValueFormat"):
            annotation = Annotation(("group1", "group2"),
                                    res)
            print(annotation.text)

    def test_check_data_stat_result(self):
        annotation = Annotation(("group1", "group2"), "p=0.05")

        res = StatResult("Custom test", None, pval=0.05, stat=None,
                         stat_str=None)
        annotation_stat_result = Annotation(("group1", "group2"), res)

        self.assertFalse(annotation.check_data_stat_result())
        self.assertTrue(annotation_stat_result.check_data_stat_result())
