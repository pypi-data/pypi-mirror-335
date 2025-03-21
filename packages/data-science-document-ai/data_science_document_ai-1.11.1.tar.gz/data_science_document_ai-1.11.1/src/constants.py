"""Config constant params for data science project(s)."""

project_parameters = {
    # Project constants
    "project_name": "document-ai",
    "project_hash": "ceb0ac54",
    # Google related parameters
    "bq_project_id": "data-pipeline-276214",
    "g_ai_project_name": "forto-data-science-production",
    "g_ai_project_id": "738250249861",
    "g_api_endpoint": "eu-documentai.googleapis.com",
    "g_location": "eu",
    "g_region": "europe-west1",
    # Google Cloud Storage
    "doc_ai_bucket_name": "ds-document-capture",
    "doc_ai_bucket_batch_input": "ds-batch-process-docs",
    "doc_ai_bucket_batch_output": "ds-batch-process-output",
    # Paths
    "folder_data": "data",
    # Big Query
    "g_ai_gbq_db_schema": "document_ai",
    "g_ai_gbq_db_table_out": "document_ai_api_calls_v1",
    # document types
    "document_types": [
        "arrivalNotice",
        "bookingConfirmation",
        "packingList",
        "commercialInvoice",
        "vgmOnlyExports",
        "finalMbL",
        "draftMbL",
        "finalHbL",
        "partnerInvoice",
        "customsAssessment",
    ],
    "excluded_endpoints": ["/healthz", "/", "/metrics", "/healthz/"],
    # models metadata (confidence),
    "g_model_data_folder": "models",
    "local_model_data_folder": "data",
    "model_selector": {
        "stable": {
            "bookingConfirmation": 1,
            "packingList": 0,
            "commercialInvoice": 0,
            "finalMbL": 0,
            "arrivalNotice": 0,
            "shippingInstruction": 0,
            "customsAssessment": 0,
            "deliveryOrder": 0,
            "partnerInvoice": 0,
        },
        "beta": {
            "bookingConfirmation": 0,
            "packingList": 0,
            "finalMbL": 0,
            "arrivalNotice": 0,
            "shippingInstruction": 0,
            "customsAssessment": 0,
            "deliveryOrder": 0,
            "partnerInvoice": 0,
        },
    },
    # this is the model selector for the model to be used from the model_config.yaml
    # file based on the environment, 0 mean the first model in the list
    # LLM model parameters
    "gemini_params": {
        "temperature": 0,
        "maxOutputTokens": 8000,
        "top_p": 0.8,
        "top_k": 40,
        "seed": 42,
        "model_id": "gemini-2.0-flash",
    },
    # Key to combine the LLM results with the Doc Ai results
    "key_to_combine": {
        "bookingConfirmation": ["transportLegs"],
        "finalMbL": ["containers"],
        "customsAssessment": ["containers"],
        "packingList": ["skuData"],
        "commercialInvoice": ["skus"],
        "shippingInstruction": ["containers"],
        "partnerInvoice": ["lineItem"],
    },
    "beta_version_percentage": {
        "bookingConfirmation": 0,
        "packingList": 1,
    },
}

# Hardcoded rules for data points formatting that can't be based on label name alone
formatting_rules = {
    "bookingConfirmation": {"pickUpTerminal": "depot", "gateInTerminal": "terminal"},
    "deliveryOrder": {"pickUpTerminal": "terminal", "EmptyContainerDepot": "depot"},
}
