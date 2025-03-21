gherkin_code = {
    "description": """
        Transform the following use case into BDD files with outline scenarios for success and error cases.
        For each attribute, generate a custom error message when it is not provided.
        Focus on generalizing the scenarios and covering more possibilities with examples
        
        Return the response in portuguese
        Return the response in portuguese
        Return the response in portuguese
            
        {user_case}
        Example output format:
        Scenario Outline: Successfully add a modality
                Given the server provides the modality data <sigla>, <name>, <description>, <percentage>, <start_date>, <scholarships>
                And the server selects the resolution <resolution>
                When the system validates and saves the modality
                Then the system should save the modality with the status "In editing"
                
            Examples:
                | sigla | name | description | percentage | start_date | scholarships | resolution |
                | ABC   | Name | Desc       | 10         | 2024-01-01 | Scholarship1 | Res1       |

            Scenario Outline: Add modality with error
                Given the server provides the modality data <sigla>, <name>, <description>, <percentage>, <start_date>, <scholarships>
                And the server selects the resolution <resolution>
                When the system validates and cannot save the modality
                Then the system should return an error message "<error_message>"
                
            Examples:
                | sigla | name | description | percentage | start_date | scholarships | resolution | error_message                     |
                | ABC   | Name | Desc       | -10        | 2024-01-01 | Scholarship1 | Res1      | Percentage cannot be negative     |
    """,
    "expected_output": "ONLY the gherkin code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG. Return the response in portuguese"
}

gherkin_review = {
    "description": """
        Based on the user case below, review and adjust the generated Gherkin code if necessary.
        Pay attention to writing inconsistencies and syntax errors. Verify that the scenarios cover all possibilities.
        Focus on generalizing the scenarios to cover more possibilities with examples.

        {user_case}
    """,
    "expected_output": "ONLY the gherkin code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG"
}

manager_gherkin_task = {
    "description": """
        {}

        {}

        {}

        Read and compare all generated Gherkin codes above and develop a final version based on them.
        Return the response in portuguese
        Return the response in portuguese
        Return the response in portuguese

    """,
    "expected_output": "ONLY the gherkin code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG.",
}