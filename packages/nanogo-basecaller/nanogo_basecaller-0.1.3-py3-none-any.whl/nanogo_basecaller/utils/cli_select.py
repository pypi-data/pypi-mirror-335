"""
Command-line option selection utilities for the NanoGO bioinformatics pipeline.

This module provides functions for interactive selection from lists of options
via command-line interfaces.
"""

from typing import List, Any, TypeVar, Optional, Union

T = TypeVar("T")


def select_option(
    options: List[T],
    prompt: str,
    include_all: bool = False,
    default_index: Optional[int] = None,
    numbered: bool = True,
    color: bool = True,
) -> Union[T, str]:
    """
    Present a list of options to the user and get their selection.

    Args:
        options: List of options to present
        prompt: Prompt text to display
        include_all: Whether to include an "All" option
        default_index: Index of the default option (1-based)
        numbered: Whether to number the options
        color: Whether to use colored output

    Returns:
        Selected option or "All" if that option was selected

    Raises:
        IndexError: If the default_index is out of range
    """
    if not options:
        raise ValueError("No options provided for selection")

    if default_index is not None and not (
        1 <= default_index <= len(options) + (1 if include_all else 0)
    ):
        raise IndexError(f"Default index {default_index} is out of range")

    # Text formatting helpers
    red = "\033[1;31m" if color else ""
    reset = "\033[0m" if color else ""

    while True:
        print(prompt)

        # Display options
        for idx, item in enumerate(options, start=1):
            default_marker = " [default]" if default_index == idx else ""
            if numbered:
                print(f"{red}{idx}.{reset} {item}{default_marker}")
            else:
                print(f"{red}-{reset} {item}{default_marker}")

        # Display "All" option if requested
        if include_all:
            all_idx = len(options) + 1
            default_marker = " [default]" if default_index == all_idx else ""
            if numbered:
                print(f"{red}{all_idx}.{reset} All{default_marker}")
            else:
                print(f"{red}-{reset} All{default_marker}")

        # Get and validate user input
        max_option = len(options) + (1 if include_all else 0)
        selection_prompt = f"{red}Choose an option (1-{max_option}): {reset}"

        choice = input(selection_prompt).strip()

        # Handle empty input with default
        if not choice and default_index is not None:
            choice_num = default_index
            break

        # Handle empty input without default
        if not choice:
            print("Invalid entry. Please provide an option.")
            continue

        # Process numeric input
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                break
            elif include_all and choice_num == len(options) + 1:
                return "All"
            else:
                print(f"{red}Invalid choice. Please select a valid option.{reset}")
        except ValueError:
            print(f"{red}Invalid input. Please enter a valid number.{reset}")

    return options[choice_num - 1]


def multi_select_options(
    options: List[T],
    prompt: str,
    include_all: bool = False,
    default_indices: Optional[List[int]] = None,
    color: bool = True,
) -> List[T]:
    """
    Present a list of options to the user and get multiple selections.

    Args:
        options: List of options to present
        prompt: Prompt text to display
        include_all: Whether to include an "All" option
        default_indices: Indices of default selections (1-based)
        color: Whether to use colored output

    Returns:
        List of selected options, or all options if "All" was selected
    """
    if not options:
        raise ValueError("No options provided for selection")

    if default_indices and not all(1 <= idx <= len(options) for idx in default_indices):
        raise IndexError("One or more default indices are out of range")

    # Text formatting helpers
    red = "\033[1;31m" if color else ""
    reset = "\033[0m" if color else ""

    while True:
        print(prompt)

        # Display options
        for idx, item in enumerate(options, start=1):
            default_marker = (
                " [default]" if default_indices and idx in default_indices else ""
            )
            print(f"{red}{idx}.{reset} {item}{default_marker}")

        # Display "All" option if requested
        if include_all:
            all_idx = len(options) + 1
            print(f"{red}{all_idx}.{reset} All")

        # Get and validate user input
        max_option = len(options) + (1 if include_all else 0)
        selection_prompt = (
            f"{red}Choose options (comma-separated, 1-{max_option}): {reset}"
        )

        choice = input(selection_prompt).strip()

        # Handle empty input with default
        if not choice and default_indices:
            return [options[idx - 1] for idx in default_indices]

        # Handle empty input without default
        if not choice:
            print("Invalid entry. Please provide at least one option.")
            continue

        # Process comma-separated input
        try:
            # Handle "All" as a special case
            if choice == str(len(options) + 1) and include_all:
                return list(options)

            # Parse comma-separated list
            choice_nums = [int(x.strip()) for x in choice.split(",")]

            # Validate all choices
            if all(1 <= num <= len(options) for num in choice_nums):
                return [options[num - 1] for num in choice_nums]
            elif include_all and len(options) + 1 in choice_nums:
                return list(options)
            else:
                print(f"{red}Invalid choice(s). Please select valid options.{reset}")
        except ValueError:
            print(f"{red}Invalid input. Please enter comma-separated numbers.{reset}")


def confirm_action(prompt: str, default: bool = True, color: bool = True) -> bool:
    """
    Prompt the user for confirmation of an action.

    Args:
        prompt: Prompt text to display
        default: Default response (True for yes, False for no)
        color: Whether to use colored output

    Returns:
        True if confirmed, False otherwise
    """
    # Text formatting helpers
    red = "\033[1;31m" if color else ""
    reset = "\033[0m" if color else ""

    default_prompt = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{red}{prompt} {default_prompt}: {reset}").strip().lower()

        if not response:
            return default

        if response in ("y", "yes"):
            return True

        if response in ("n", "no"):
            return False

        print(f"{red}Please answer 'y' or 'n'.{reset}")
