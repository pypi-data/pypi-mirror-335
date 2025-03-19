# The following configuration values are environment-specific and need to be updated when switching to a new environment.
# For example, we are currently on environment "seventeen," and when transitioning to environment "eighteen,"
# these values should be updated accordingly.

API_URL = "https://ojykj5ys3rflbprrjwiyi524oy.appsync-api.us-east-1.amazonaws.com/graphql"  # GraphQL API URL
App_Client_ID = "6hmbs2hm1dbpantdbpfnokina"  # App_Client_ID is the client ID for an app in a Cognito User Pool
Identity_Pool_ID = "us-east-1:9682a196-3376-4d36-b5d8-d46862f47d7b"  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
User_Pool_ID = "us-east-1_wzrj8LRkh"  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
Bucket_Name = "mlviz1049e7ed428840c3bb9773b134209edd111800-seventeen"  # S3 bucket name storing datasets and configs
Validation_API_URL = "https://htknl8tmxi.execute-api.us-east-1.amazonaws.com/seventeen/validate"  # Validation API URL
# This is the URL for gooder ai application
Base_URL = "https://latest.gooder.ai?view="
AWS_Region_Name = "us-east-1"
