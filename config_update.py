"""
This script updates the CMS and config file bundled in the app with the latest content from stubs.
Stubs should always contains the most up-to-date content.
CMS:
File bundled in app:CMSConfiguration.json
Remote location to update from: http://stubreena.co.uk/digital/cms/common/fallback-cms.json
WATCH CMS:
File bundled in app:WatchCMS.json
Remote location to update from: http://stubreena.co.uk/digital/cms/common/WatchCMS.json
App Config:
File bundled in app: MyeeConfig.json
Remote location to update from: https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/$APP_VERSION_NUMBER/myee-config-ios.json"
NOTE!!!! The DEFAULT_APP_VERSION_NUMBER should be set for each branch depending on which version the release branch
is targeted at
"""
from asyncio import get_event_loop, as_completed
from os import environ
from requests import get
from jsonschema import validate, ValidationError as JSONValidationError

# A version of the app, which script is going to update config for. Not sure about how can I  use
# the DEFAULT_APP_VERSION_NUMBER variable mentioned above ^. I did not see it while running the script
# on my work station.
app_version_number = "v4.23.0"

# The dictionary storing URLs for downloading remote config files
# NOTE!!! Production URLs are not final. Require updating!
config_mapping = {"production": {
    "url_mapping": {
        "cms_config": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json",
        "watch_cms_config": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json",
        "app_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(
            app_version_number),
        "analytics_config": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json",
        "ab_test_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json"}
},
    "qa": {
        "url_mapping": {
            "cms_config": "http://stubreena.co.uk/digital/cms/common/fallback-cms.json",
            "watch_cms_config": "http://stubreena.co.uk/digital/cms/common/WatchCMS.json",
            "app_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/{}/v4app_config-ios.json".format(
                app_version_number),
            "analytics_config": "http://stubreena.co.uk/digital/analytics/AnalyticsContextData.json",
            "ab_test_config": "https://s3-eu-west-1.amazonaws.com/ee-dtp-static-s3-test/prod/myeeapp/abtestconfig/abtestconfig.json"}
    }
}

# JSON Config schemas to be used for validating remote config files
config_scheme = {
    "cms_config": {
        "type": "object",
        "properties": {
            "cmsVersion": {"type": "string"},
            "appleWatch": {"type": "object"},
            "global": {"type": "object"},
        },
        "required": ["cmsVersion", "help", "global"]
    },
    "watch_cms_config": {
        "type": "object",
        "properties": {
            "global": {"type": "object"},
            "appleWatch": {"type": "object"},
        },
        "required": ["global", "appleWatch"]
    },
    "app_config": {
        "type": "object",
        "properties": {
            "configVersion": {"type": "string",
                              "enum": [app_version_number]},
            "clickToCallHelpHub": {"type": "object"},
        },
        "required": ["configVersion", "clickToCallHelpHub"]
    },
    "analytics_config": {
        "type": "object",
        "properties": {
            "login": {"type": "object"},
            "help": {"type": "object"},
        },
        "required": ["login", "help"]
    },
    "ab_test_config": {
        "type": "object",
        "properties": {
            "earlyUpgadePrice": {"type": "object"},
            "offersYellowDot": {"type": "object"},
        },
        "required": ["earlyUpgadePrice", "offersYellowDot"]
    },
}


def get_local_path(config_name: str):
    """ Returns a relative or an absolute local path for saving a config file depending on whether PROJECT_DIR
    variable set or not"""
    local_paths = {"cms_config": "/MyEE/Resources/CMSConfiguration.json",
                   "watch_cms_config": "/WatchAppExtension/WatchCMS.json",
                   "app_config": "/MyEE/Resources/MyeeConfig.json",
                   "analytics_config": "/MyEE/Resources/AnalyticsContextData.json",
                   "ab_test_config": "/MyEE/Resources/abtestconfig.json"}
    if not project_dir:
        return ".." + local_paths[config_name]
    else:
        return project_dir + local_paths[config_name]


async def get_latest(config_name: str):
    _loop = get_event_loop()
    local_path = get_local_path(config_name)
    url = url_mapping[config_name]
    print("Downloading {} via url:\n{}".format(config_name, url))
    # Run a blocking GET request in a separate executor
    request = _loop.run_in_executor(None, get, url)
    # Take back control to the calling coroutine until response received
    response = await request
    if response.status_code == 200:
        print("Remote for {} file successfully downloaded.".format(config_name))
        try:
            temp_file = response.json()
        except ValueError:
            print("error: Failed to decode JSON in {}.".format(config_name))
            exit(1)
        else:
            try:
                # Validate JSON file prior to saving
                validate(temp_file, config_scheme[config_name])
            except JSONValidationError as error:
                # If some fields are missed in the JSON instance, the scripts interrupt building
                if error.validator == "required":
                    print("error: There is an issue while validating {}. {}.".format(config_name, error.message))
                    exit(1)
                # In case of other kind of errors, raise a warning message and save a file as it is
                else:
                    print("warning: There is an issue while validating {}: {}.".format(config_name, error.message))
            try:
                # Write a response to a local config json file
                with open(local_path, "w", encoding="utf-8") as config_file:
                    config_file.write(response.text)
                return "{} successfully saved to:\n{}".format(config_name, local_path)
            # Return a fail message in case of error while writing file
            except FileNotFoundError:
                print("error: Failed to open local file via {}. Check that directory exists.".format(local_path))
                exit(1)
    # Inform about failed response
    else:
        print("error: Failed to download {} with status code {}. Service can be temporary unavailable or check your" \
              " connection.".format(config_name, response.status_code))
        exit(1)


async def print_when_done(tasks: list):
    """Top level coroutine, which executes tasks in the loop concurrently."""
    for result in as_completed(tasks):
        print(await result)


if __name__ == "__main__":
    print("\"app_version_number\" should be changed for each release manually.\n"
          "It means that each release branch which is in parallel should have its own related \"app_version_number\"\n"
          "Config files for the app version {} are going to be updated".format(app_version_number))
    # Find PROJECT_DIR variable. If it does not exist, returns None
    project_dir = environ.get("PROJECT_DIR")
    # Retrieve  TEMP_VAR123 variable (this name is not final), which is going to be set if the app is being created with
    # a production schema, but QA config files should be used.
    temp_var = environ.get("TEMP_VAR123")
    # Retrieve  GCC_PREPROCESSOR_DEFINITIONS variable in order to define what scheme used
    # If QA is in GCC_PREPROCESSOR_DEFINITIONS or TEMP_VAR123 is present among global env variables,
    # then QA URLs will be used in order to download config files. If PRODUCTION is set only,
    # then a production scheme with the corresponding URLs will be used.
    preprocessor_definition = environ.get("GCC_PREPROCESSOR_DEFINITIONS")
    if preprocessor_definition:
        if "QA=1" in preprocessor_definition or temp_var is not None:
            url_mapping = config_mapping["qa"]["url_mapping"]
        elif "PRODUCTION=1" in preprocessor_definition:
            url_mapping = config_mapping["production"]["url_mapping"]
    else:
        print("error: Failed to retrieve GCC_PREPROCESSOR_DEFINITIONS variable."
              " It must be set in order to define a schema.")
        exit(1)
    # names of config files to be updated
    config_names = ("cms_config", "watch_cms_config", "app_config", "analytics_config", "ab_test_config")
    # Create an event loop for scheduling coroutines
    loop = get_event_loop()
    # Run a top level coroutine print_when_done.
    loop.run_until_complete(print_when_done([get_latest(config_name) for config_name in config_names]))
    # Close the loop when job is done
    loop.close()
