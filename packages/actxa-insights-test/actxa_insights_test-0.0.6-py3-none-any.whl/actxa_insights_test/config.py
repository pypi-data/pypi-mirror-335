def get_url(env: str):
    urls = {
        "dev": "https://insights-dev.actxa.com",
        "uat": "https://insights-uat.actxa.com",
        "staging": "https://insights-staging.actxa.com",
        "prod": "https://insights.actxa.com",
    }

    return urls.get(env, "https://insights.actxa.com")
