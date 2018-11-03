"""
This shell script updates the CMS and config file bundled in the app with the latets content from stubs.
Stubs should always contains the most up-to-date content.
CMS:
File bundled in app:CMSConfiguration.json
Remote location to update from: http://stubreena.co.uk/digital/cms/common/fallback-cms.json
WATCH CMS:
File bundled in app:WatchCMS.json
Remote location to update from: http://stubreena.co.uk/digital/cms/common/WatchCMS.json

App Config:
File bundled in app:MyeeConfig.json
Remote location to update from: https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/$APP_VERSION_NUMBER/myee-config-ios.json"
NOTE!!!! The DEFAULT_APP_VERSION_NUMBER should be set for each branch depending on which version the release branch is targetted at
"""

app_version_number = "v4.23.0"
print("\"app_version_number\" should be changed for each release manually.\n"
      "It means that each release branch which is in parallel should have its own related \"app_version_number\"")

cms_config_path = "../MyEE/Resources/CMSConfiguration.json"
watch_cms_config_path = "../WatchAppExtension/WatchCMS.json"
app_config_file_path= "../MyEE/Resources/MyeeConfig.json"
analytics_config_file_path= "../MyEE/Resources/AnalyticsContextData.json"
ab_test_config_file_path= "../MyEE/Resources/abtestconfig.json"

config_mapping = {"CMS_config": ("http://stubreena.co.uk/digital/cms/common/fallback-cms.json", "../MyEE/Resources/CMSConfiguration.json"),
                  "watch_CMS_config": ("http://stubreena.co.uk/digital/cms/common/WatchCMS.json", "../WatchAppExtension/WatchCMS.json"),
                  "app_config": ("https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(app_version_number), "../MyEE/Resources/MyeeConfig.json"),
                  "analytics_config": ("http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json", "../MyEE/Resources/MyeeConfig.json"),
                  "ab_test_config": ("https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json", "../MyEE/Resources/abtestconfig.json")}

def get_latest(config_name: str):
    url, path = config_mapping[config_name]
    print("Downloading {} via url:\n{}".format(config_name, url))
    from requests import get
    response = get(url=url)
    if response.status_code == 200:
        temp_file = response.json()
        return temp_file if temp_file else "Failed to load from:\n{}".format(url)
    else:
        return "Failed, status code {}. Service can be temporary unavailable or check your connection". format(response.status_code)

print(get_latest("app_config"))