cypress_write = {
    "description": """
        {vue_code}

        Based on the code above generate a End to End black box test.
        You don't need to put an value and check if the input value in sequence it's not good practice.
        Return only the cypress code. Do not use any other special formating like markdown tags. Do not use ``` code block tag
        write coments in parts of the code that are not fully implemented guiding the user how to continue, but always make an implementation even if partial or generic""",
        "expected_output": """Only the cypress code. Do not use any other special formating like markdown tags. Do not use ``` code block tag""",
    "output_example": "cypress_example"
}


cypress_review = {
    "description": """
        Review the code generated and look for possible improvements or errors. Only change the code if you find that is necessary, otherwise leave as it is.
        The objective is to generate an End to End black box test.
        Below is the Vue code which the test was based on:
        {vue_code}

        You don't need to put a value and check if the input value in sequence; it's not good practice.
        Return only the cypress code. Do not use any other special formating like markdown tags. Do not use ``` code block tag""",
    "expected_output": """Only the cypress code. Do not use any other special formating like markdown tags. Do not use ``` code block tag""",
    "output_example": "cypress_example"
}

final_task = {
    "description": """
        {}

        {}

        {}

        Read the 3 Cypress codes above then generate a final version of it, assimilating the best parts of each code into one unique code.
        Return only the Cypress code. Do not use any other special formatting like markdown tags. Do not use ``` code block tag""",
    "expected_output": """Only the Cypress code. Do not use any other special formatting like markdown tags. Do not use ``` code block tag""",
    "output_example": "cypress_example"
}
