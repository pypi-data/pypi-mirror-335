dict_source = {
    "app_review": {
        "string_cols": ["Subject", "Body"],
        "select_cols": ["Date"],
        "api_endpoint": 'https://datasuite.shopee.io/datahub/api/v1/usertoken/upload/csv/csv-d354da83-bfe7-437c-b1ca-4fd8546c3256',
        "ingestion_token": '507878de-8603-448f-b2bc-d1113b158655',
    },
    "kompa": {
        "string_cols": ["Title", "Content"],
        "select_cols": [
            "Id",
            "Topic",
            "UrlComment",
            "UrlTopic",
            "SiteName",
            "AuthorId",
            "PublishedDate",
        ],
        "api_endpoint": 'https://datasuite.shopee.io/datahub/api/v1/usertoken/upload/csv/csv-b57ff7d2-31ac-42bd-bb0a-6c429fe3840c',
        "ingestion_token": '507878de-8603-448f-b2bc-d1113b158655',
    },
    "nps": {
        "string_cols": ["user_fill_text"],
        "select_cols": ["date_submitted", "userid"],
        "api_endpoint": 'https://datasuite.shopee.io/datahub/api/v1/usertoken/upload/csv/csv-f0f8d554-5677-41ac-bcd3-546de55c72cf',
        "ingestion_token": '507878de-8603-448f-b2bc-d1113b158655',
    }
}