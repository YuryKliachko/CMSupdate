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
from os import environ
from git import Repo
from requests import get

app_version_number = "v4.23.0"
project_dir = environ.get("PROJECT_DIR", None)
repo = Repo()
current_branch = repo.active_branch.name

print("\"app_version_number\" should be changed for each release manually.\n"
      "It means that each release branch which is in parallel should have its own related \"app_version_number\"")

def get_absolute_local_path(config_name):
    relative_local_pathes = {"cms_config": "/MyEE/Resources/CMSConfiguration.json",
                           "watch_cms_config": "/WatchAppExtension/WatchCMS.json",
                           "app_config": "/MyEE/Resources/MyeeConfig.json",
                           "analytics_config": "/MyEE/Resources/AnalyticsContextData.json",
                           "ab_test_config": "/MyEE/Resources/abtestconfig.json"}
    if not project_dir:
        return ".." + relative_local_pathes[config_name]
    else:
        return project_dir + relative_local_pathes[config_name]

url_mapping = {"cms_config": {"development": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json",
                              "release": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json"},
               "watch_cms_config": {"devolopment": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json",
                                    "release": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json"},
               "app_config": {"development": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(app_version_number),
                              "release": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(app_version_number)},
               "analytics_config": {"development": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json",
                                    "release": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json"},
               "ab_test_config": {"development": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json",
                                  "release": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json"}
               }

def get_url(config_name):
    if current_branch == "release":
        return url_mapping[config_name][current_branch]
    else:
        return url_mapping[config_name]["development"]

def get_latest(config_name: str):
    local_path = get_absolute_local_path(config_name)
    url = get_url(config_name)
    print("Current branch is \"{}\"".format(current_branch))
    print("Downloading {} via url:\n{}".format(config_name, url))
    response = get(url=url)
    if response.status_code == 200:
        print("Remote file successfuly dowloaded.")
        temp_file = response.json()
        if temp_file:
            try:
                with open(local_path, "w") as config_file:
                    config_file.write(response.text)
                return "{} successfuly saved to {}".format(config_name, local_path)
            except FileNotFoundError:
                return "Failed to open local file via {}. Check that directory exists.".format(local_path)
        else:
            return "Failed to load from:\n{}".format(url)
    else:
        return "Failed, status code {}. Service can be temporary unavailable or check your connection". format(response.status_code)


print(get_latest("cms_config"))