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
from asyncio import get_event_loop, as_completed
from os import environ
from requests import get

app_version_number = "v4.23.0"

config_scheme = {"production": {
                    "url_mapping": {
                        "cms_config": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json",
                        "watch_cms_config": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json",
                        "app_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(app_version_number),
                        "analytics_config": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json",
                        "ab_test_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json"}
                                },
                 "qa": {
                     "url_mapping": {
                         "cms_config": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json",
                         "watch_cms_config": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json",
                         "app_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(app_version_number),
                         "analytics_config": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json",
                         "ab_test_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json"}
                        }
                 }


def get_absolute_local_path(config_name):
    relative_local_paths = {"cms_config": "/MyEE/Resources/CMSConfiguration.json",
                            "watch_cms_config": "/WatchAppExtension/WatchCMS.json",
                            "app_config": "/MyEE/Resources/MyeeConfig.json",
                            "analytics_config": "/MyEE/Resources/AnalyticsContextData.json",
                            "ab_test_config": "/MyEE/Resources/abtestconfig.json"}
    if not project_dir:
        return ".." + relative_local_paths[config_name]
    else:
        return project_dir + relative_local_paths[config_name]


async def get_latest(config_name):
    _loop = get_event_loop()
    local_path = get_absolute_local_path(config_name)
    url = url_mapping[config_name]
    print("Downloading {} via url:\n{}".format(config_name, url))
    # Run a blocking GET request in a separate executor
    request = _loop.run_in_executor(None, get, url)
    # Take back a control to the calling coroutine until response received
    response = await request
    if response.status_code == 200:
        print("Remote for {} file successfully downloaded.".format(config_name))
        temp_file = response.json()
        if temp_file:
            try:
                with open(local_path, "w", encoding="utf-8") as config_file:
                    config_file.write(response.text)
                return "{} successfully saved to:\n{}".format(config_name, local_path)
            except FileNotFoundError:
                return "Failed to open local file via {}. Check that directory exists.".format(local_path)
        else:
            return "Failed to load from:\n{}".format(url)
    else:
        return "Failed, status code {}. Service can be temporary unavailable or check your connection".format(response.status_code)


async def print_when_done(tasks):
    """Top level coroutine, which execute tasks. Receives list of tasks, returns"""
    for result in as_completed(tasks):
        print(await result)

if __name__ == "__main__":
    print("\"app_version_number\" should be changed for each release manually.\n"
          "It means that each release branch which is in parallel should have its own related \"app_version_number\"")
    # Find PROJECT_DIR variable. If it does not exist, returns None
    try:
        project_dir = environ.get("PROJECT_DIR")
    except KeyError:
        project_dir = None
    # Retrieve  TEMP_VAR123 (this name is not final), which is going to be set if the app is being created with
    # production schema, but QA config should be used.
    try:
        temp_var = environ.get("TEMP_VAR123", None)
    except KeyError:
        temp_var = None
    # Retrieve  GCC_PREPROCESSOR_DEFINITIONS variable in order to define what scheme used
    # If QA isnin GCC_PREPROCESSOR_DEFINITIONS or TEMP_VAR123 is present among global env variables,
    # then QA URLs will be used in order to download config files. If PRODUCTION is set only,
    # then a production scheme with the corresponding URLs will be used.
    try:
        preprocessor_definition = environ.get("GCC_PREPROCESSOR_DEFINITIONS")
        if "QA=1" in preprocessor_definition or temp_var is not None:
            url_mapping = config_scheme["qa"]["url_mapping"]
        elif "PRODUCTION=1" in preprocessor_definition:
            url_mapping = config_scheme["production"]["url_mapping"]
    except KeyError:
        print("Failed in retieving GCC_PREPROCESSOR_DEFINITIONS variable. It must be set in order to define a schema")
        exit()
    # names of config files to be updated
    names = ("cms_config", "watch_cms_config", "app_config", "analytics_config", "ab_test_config")
    # Create an event loop for scheduling coroutines
    loop = get_event_loop()
    # Run a top level coroutine print_when_done.
    loop.run_until_complete(print_when_done([get_latest(config_name) for config_name in names]))
    # Close the loop when job is done
    loop.close()
