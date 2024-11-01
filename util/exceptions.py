class ToolFunctionError(Exception):
    """Exception raised for errors in the tool function execution.

    Attributes:
        function_name -- name of the tool function that caused the error
        message -- explanation of the error
    """

    def __init__(self, function_name, message="ToolFunctionError"):
        self.function_name = function_name
        self.message = f"Error occurred running {function_name}: \n{message}"
        super().__init__(self.message)