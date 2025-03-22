API Reference
=============

Main Functions
-------------

.. code-block:: python

   from diffscope import analyze_commit

analyze_commit
~~~~~~~~~~~~~

.. code-block:: python

   def analyze_commit(commit_url: str) -> CommitAnalysisResult:
       """
       Analyze a Git commit and extract both file-level and function-level changes.
       
       Args:
           commit_url: URL to a Git commit (currently only GitHub is supported)
           
       Returns:
           CommitAnalysisResult object containing file and function level changes
       
       Example:
           >>> result = analyze_commit("https://github.com/owner/repo/commit/abc123")
           >>> for file in result.modified_files:
           >>>     print(f"File: {file.filename}, Changes: {file.changes}")
       """

Data Models
-----------

CommitAnalysisResult
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class CommitAnalysisResult:
       """
       Contains the results of analyzing a git commit.
       
       Attributes:
           repository (str): Repository name in owner/repo format
           commit_sha (str): Commit SHA
           commit_message (str): Commit message
           commit_author (str): Author of the commit
           commit_date (datetime): Date and time of the commit
           modified_files (List[ModifiedFile]): List of modified files
           modified_functions (List[ModifiedFunction]): List of modified functions
       """

ModifiedFile
~~~~~~~~~~~

.. code-block:: python

   class ModifiedFile:
       """
       Represents a file that was modified in a commit.
       
       Attributes:
           filename (str): Filename
           status (str): File status (added, modified, removed, renamed)
           additions (int): Number of lines added
           deletions (int): Number of lines deleted
           changes (int): Total number of changes (additions + deletions)
           patch (Optional[str]): Unified diff patch
       """

ModifiedFunction
~~~~~~~~~~~~~~~

.. code-block:: python

   class ModifiedFunction:
       """
       Represents a function that was modified in a commit.
       
       Attributes:
           name (str): Function name
           file (str): File containing the function
           change_type (FunctionChangeType): Type of change
           old_start_line (Optional[int]): Start line in the old version
           old_end_line (Optional[int]): End line in the old version
           new_start_line (Optional[int]): Start line in the new version
           new_end_line (Optional[int]): End line in the new version
           old_content (Optional[str]): Function content in the old version
           new_content (Optional[str]): Function content in the new version
       """

FunctionChangeType
~~~~~~~~~~~~~~~~

.. code-block:: python

   class FunctionChangeType(Enum):
       """
       Enum representing types of function changes.
       
       Values:
           ADDED: Function was added
           DELETED: Function was deleted
           MODIFIED: Function was modified (body changes)
           SIGNATURE_CHANGED: Function signature was changed
           RENAMED: Function was renamed
           MOVED: Function was moved to a different location
           DOCSTRING_CHANGED: Only the function's docstring was changed
       """ 