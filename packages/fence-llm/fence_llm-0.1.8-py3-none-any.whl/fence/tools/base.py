"""
Tools for agents
"""

import inspect
import logging
from abc import ABC, abstractmethod
from typing import Callable

logger = logging.getLogger(__name__)

##############
# Base class #
##############


class BaseTool(ABC):

    def __init__(self, description: str = None):
        """
        Initialize the BaseTool object.

        :param description: A description of the tool (if not provided, the docstring will be used)
        """
        self.description = description
        self.environment = {}

    def run(self, environment: dict = None, **kwargs):
        """
        Base method that is called when the tool is used.
        This method will always accept 'environment' as a parameter.
        """

        # Initialize environment if not provided
        self.environment = environment or self.environment

        # Preprocess environment if needed
        # self.preprocess_environment(environment)

        # Pass the environment to the execute_tool method
        kwargs["environment"] = environment

        # Call the subclass-specific implementation
        return self.execute_tool(**kwargs)

    @abstractmethod
    def execute_tool(self, environment: dict = None, **kwargs):
        """
        The method that should be implemented in the derived class.
        This will handle the actual tool-specific logic.

        :param environment: A dictionary of environment variables to pass to the tool
        :param kwargs: Additional keyword arguments for the tool
        """
        raise NotImplementedError

    # def preprocess_environment(self, environment: dict):
    #     """
    #     Optional method to preprocess the environment, can be overridden by subclasses.
    #     """
    #     pass

    def format_toml(self):
        """
        Returns a TOML-formatted key-value pair of the tool name,
        the description (docstring) of the tool, and the arguments
        of the `run` method.
        """
        # Get the arguments of the run method
        run_args = inspect.signature(self.execute_tool).parameters

        # Add all arguments, and ensure that the argument
        # is annotated with str if no type is provided
        run_args = {
            arg_name: (
                arg_type.annotation
                if arg_type.annotation != inspect.Parameter.empty
                else str
            )
            for arg_name, arg_type in run_args.items()
        }
        run_args.pop("environment", None)
        run_args.pop("kwargs", None)

        # Preformat the arguments
        argument_string = ""
        if run_args:
            for arg_name, arg_type in run_args.items():
                argument_string += (
                    f"[[tools.tool_params]]\n"
                    f'name = "{arg_name}"\n'
                    f'type = "{arg_type.__name__ or str}"\n'
                )
        else:
            argument_string = "# No arguments"

        # Get the description of the tool, if not provided, use the docstring
        tool_description = self.description or self.__doc__

        if not tool_description:
            logger.warning(
                f"Tool {self.__class__.__name__} has no description or docstring."
            )

        # Format the TOML representation of the tool for the agent
        toml_string = f"""[[tools]]
tool_name = "{self.__class__.__name__}"
tool_description = "{tool_description}"
{argument_string}"""

        return toml_string


##############
# Decorators #
##############


def tool(description: str = None):
    """
    A decorator to turn a function into a tool that can be executed with the BaseTool interface.

    :param description: A description of the tool.
    """

    def decorator(func: Callable):
        # Dynamically create the class with the capitalized function name
        class_name = "".join(
            [element.capitalize() for element in func.__name__.split("_")]
        )
        class_name = (
            f"{class_name}Tool" if not class_name.endswith("Tool") else class_name
        )

        # Define the class dynamically
        ToolClass = type(
            class_name,
            (BaseTool,),
            {
                "__init__": lambda self: BaseTool.__init__(
                    self, description=description or func.__doc__
                ),
                "execute_tool": lambda self, **kwargs: func(**kwargs),
            },
        )

        return ToolClass()

    return decorator


if __name__ == "__main__":

    class Tool(BaseTool):
        def execute_tool(self, arg1, arg2: str, **kwargs):
            return "Tool executed"

    a = Tool()

    sig = inspect.signature(a.execute_tool)
    print(sig)
    print(sig.parameters)
