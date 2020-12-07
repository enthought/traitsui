import os
import runpy
import unittest

#: Filename of the demo script
FILENAME = "Image_editor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestImageEditorDemo(unittest.TestCase):

    def test_image_path_exists(self):
        search_path, = runpy.run_path(DEMO_PATH)["search_path"]
        self.assertTrue(os.path.exists(search_path))


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestImageEditorDemo)
)
