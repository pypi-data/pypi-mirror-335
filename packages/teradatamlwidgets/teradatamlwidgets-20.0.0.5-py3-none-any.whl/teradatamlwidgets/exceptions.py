
# -*- coding: utf-8 -*-
'''
Copyright © 2024-2025 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


class TeradataNotebookException(Exception):
    """
    Teradata Notebook Exception class.
    All public functions and methods should only raise TeradataNotebookException so that
    application code need only catch TeradataNotebookException.
    Public functions and methods should use the following form

        try:
            # do something useful
        except TeradataNotebookError:
            # re-raise a TeradataNotebookException that was raised by one of our internal functions.
            raise
        exception Exception as err:
            # all other exceptions (like driver exceptions) are wrapped in a TeradataNotebookException
            raise TeradataNotebookException(msg) from err

    Both public and internal functions should raise TeradataNotebookException for any
    application errors like invalid argument.

    For example:
        if key is not in columnnames:
            raise TeradataNotebookException(msg)


    Internal functions should let other exceptions from the driver bubble up.
    If internal functions would like to do something in a try: except: block like logging,
    then it should use the form

        try:
            # do something useful
        except:
            logger.log ("log something useful")
            # re-raise the error so that it is caught by the calling public function.
            # the calling public function will take care of wrapping the exception in TeradataNotebookError
            # this will avoid a lot of unnecessary exception handling code.
            raise

    If TeradataNotebookException was the result of another exception, then the
    attribute __cause__ will be set with the root cause exception.

    """
    def __init__(self, msg):
        """
        Initializer for TeradataNotebookException. Call the parent class initializer.
        PARAMETERS:
            msg - The error message.

        RETURNS:
            A TeradataNotebookException with the error message.

        RAISES:

        EXAMPLES:
            if key is not in columnnames:
                raise TeradataNotebookException(msg)
        """
        super(TeradataNotebookException, self).__init__(msg)
