class APINames:

    # Auth
    AUTH_LOGIN_POST = "auth:login"
    AUTH_USER_RETRIEVER_GET = "auth:user-retriever"
    AUTH_RENEW_TOKEN_GET = "auth:renew-token"

    # Users
    USERS_CREATE_USER_POST = "users:create-user"
    USERS_RETRIEVE_USER_GET = "users:retrieve-user"
    USERS_UPDATE_USER_PATCH = "users:update-user"
    USERS_DELETE_USER_DELETE = "users:delete-user"

    # Templates
    TEMPLATES_CREATE_TEMPLATE_POST = "templates:create-template"
    TEMPLATES_RETRIEVE_TEMPLATE_GET = "templates:retrieve-template"
    TEMPLATES_RETRIEVE_TEMPLATES_LIST_GET = "templates:retrieve-templates-list"
    TEMPLATES_UPDATE_TEMPLATE_PATCH = "templates:update-template"
    TEMPLATES_DELETE_TEMPLATE_DELETE = "templates:delete-template"
