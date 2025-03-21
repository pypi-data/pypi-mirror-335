
dto_file_find = {
    "description": """
        {feature}

        At the path {dto_source}
        Find the dto request file and response file for the given feature,
        the open the file and read it content

        For that you should translate the title of the feature to portuguese in order to proper look for the file
    """,
    "expected_output": "The dto response and request class code",
    "async_execution": True
}
api_url_find = {
    "description": """
        {feature}

        
        USE THE TOOL ENPOINT EXTRACTOR TOOL passing the swagger path to extract the endpoints
        the swagger path is: {swagger_path} 
        Given the following endpoints search for the api url for the given Feature;
        The api_url has the feature title all in lower case;
        You should look not only for the exact correspondence, but also for similars. For example, if the feature title in lowercase is versaomodalidade, you should also consider versaomodalidadebolsa
    """,
    "expected_output": "Only the complete url path requested and the respective methods"
}
xunit_write = {
    "description": """
        {feature}

        Based on the feature described, write xUnit.net test code that adheres to the following guidelines:
        IMPORT THE DTO GIVEN TO YOU, below is an example of how to do it
        using ConectaFapes.Application.DTOs.<DTO FOLDER>.Request;
        using ConectaFapes.Application.DTOs.<DTO FOLDER>.Response;
        using ConectaFapes.Test.Shared;
        using System.Net;
        using System.Text;
        using System.Text.Json;

        the path for the feature file should be: [FeatureFile("../../../Features/<feature title in pascal case>Feature.feature")]

        Consistency with HttpClient and WebApplicationFactory: Ensure consistent use of HttpClient and WebApplicationFactory throughout the test implementation.
        Public method on test class should be marked as a Theory. Reduce the visibility of the method, or add Theory attribute to the method
        Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await   

        Validations: Implement validations to ensure:
        Request and response class names include the DTO suffix.
        Strings must not be null or empty; validate them before making any API call.
        Clear error messages are displayed in case of type mismatches or missing attributes.

        Annotations: Use Given, When, and Then annotations for test steps with explicit parameter binding.

        Examples for Operations: Include robust examples for GET, POST, PUT, DELETE, and specific operations like activate and deactivate.
        Restrictions: Do not use Theory, InlineData, or Fact. All tests should focus on scenario-based behavior with clear steps.

        The DTO class you should use is: {dto_class}

        The api url for this feature is: {api_url}
    """,
    "output_example": "xunit_code_output",
    "expected_output": "ONLY the C# code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG. Also the justifications for what was generated."
}
xunit_review= {
    "description": """
    Based on the feature below and the given code, review and adjust the xUnit.net test code if necessary.
    Pay close attention to coding inconsistencies, syntax errors, and adherence to best practices.
    Verify that the tests cover all scenarios described in the feature and that edge cases are accounted for.
    Focus on making the tests efficient and readable, and ensure that they follow xUnit.net standards.

    Public method on test class should be marked as a Theory. Reduce the visibility of the method, or add Theory attribute to the method
    Test methods should not use blocking task operations, as they can cause deadlocks. Use an async test method and await

    Validations: Implement validations to ensure:
    Request and response class names include the DTO suffix.
    Strings must not be null or empty; validate them before making any API call.
    Clear error messages are displayed in case of type mismatches or missing attributes.

    Annotations: Use Given, When, and Then annotations for test steps with explicit parameter binding.

    Examples for Operations: Include robust examples for GET, POST, PUT, DELETE, and specific operations like activate and deactivate.
    Restrictions: Do not use Theory, InlineData, or Fact. All tests should focus on scenario-based behavior with clear steps.

    Write comments in parts that should be modified or was not fully implemented in your code but do not leave without a implementation, make something even if ends to be generic

    {feature}
    """,
    "output_example": "xunit_code_output",
    "expected_output": "ONLY the xUnit.net test code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG"
}
manager_xunit_task = {
    "description": """
        code 1:
        {}

        code 2:
        {}

        code 3:
        {}

        Read and compare all generated C# xUnit codes and develop a final version based on them.
        Write comments in parts that should be modified or was not fully implemented in your code but do not leave without a implementation, make something even if ends to be generic
    """,
    "expected_output": "ONLY the C# xUnit code generated without the code block like ```, DO NOT USE ANY MARKDOWN TAG",
    "output_example": "xunit_code_output"
}
