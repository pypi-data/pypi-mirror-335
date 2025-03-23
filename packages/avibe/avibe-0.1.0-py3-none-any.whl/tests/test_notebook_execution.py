import os
import unittest
from nbconvert import NotebookExporter, exporters
from nbconvert.preprocessors import ExecutePreprocessor
from io import StringIO
import nbformat


class TestNotebookExecution(unittest.TestCase):
    def test_run_notebook(self):
        # Get the directory of the current test file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the absolute path to the notebook file
        notebook_path = os.path.join(current_dir, "test_notebook.ipynb")

        # Load the notebook file
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook_content = f.read()

        # Parse the notebook
        notebook = nbformat.reads(notebook_content, as_version=4)

        # Set up the Execute Preprocessor (runs the notebook)
        execute_preprocessor = ExecutePreprocessor(timeout=600, kernel_name="python3")

        # Execute the notebook
        execute_preprocessor.preprocess(notebook, {'metadata': {'path': '.'}})

        # Check whether the notebook ran successfully
        cells = notebook["cells"]
        for cell in cells:
            if "outputs" in cell:
                for output in cell["outputs"]:
                    if output.get("output_type") == "stream" and "traceback" in output:
                        # If there is an error in the notebook, fail the test
                        self.fail(f"Error in notebook execution: {output['text']}")

        # Optionally: Check the result
        results_cell = cells[-1]  # Assuming the result is in the last cell
        self.assertIn('result', results_cell["source"])
