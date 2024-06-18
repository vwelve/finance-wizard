class ToolFunctionError(Exception):
    """Exception raised for errors in the tool function execution.

    Attributes:
        function_name -- name of the tool function that caused the error
        message -- explanation of the error
    """

    def __init__(self, function_name, message="Error occurred while executing the tool function"):
        self.function_name = function_name
        self.message = f"{message}: {function_name}"
        super().__init__(self.message)