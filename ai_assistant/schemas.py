expense_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "get_expense_record",
                    "description": "summarize expenses filtering by a start and end date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "The start date to begin with, format allowed is YYYY-MM-DD",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date to end with, format allowed is YYYY-MM-DD",
                            }
                        },
                        "required": ["start_date", "end_date"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_diesel_record",
                    "description": "summarize diesel filtering by a start and end date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "The start date to begin with, format allowed is YYYY-MM-DD",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date to end with, format allowed is YYYY-MM-DD",
                            }
                        },
                        "required": ["start_date", "end_date"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_ekedc_record",
                    "description": "summarize ekedc (prepaid meter) filtering by a start and end date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "The start date to begin with, format allowed is YYYY-MM-DD",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date to end with, format allowed is YYYY-MM-DD",
                            }
                        },
                        "required": ["start_date", "end_date"],
                    },
                },
            }
    ]