from config.translations import translate

APP_NAME = "ZonePaq Toolkit"
APP_VERSION = "2.0-rc.1"
# APP_VERSION = "0.1"  # for testing update notification
APP_AUTHOR = "63OR63"
APP_LICENSE = "MIT"
APP_DESCRIPTION = translate("meta_description")
APP_DESCRIPTION_EN = translate("meta_description", "English")
APP_REPO = "63OR63/zonepaq"
APP_URL = "https://github.com/" + APP_REPO

APP_ICONS = {
    "ico": r"zonepaq\assets\icons\main.ico",
    "icns": r"zonepaq\assets\icons\main.icns",
    "png": r"zonepaq\assets\icons\main.png",
    "mdi-cog": r"zonepaq\assets\icons\mdi-cog.png",
    "mdi-help": r"zonepaq\assets\icons\mdi-help.png",
}

COPYRIGHT = "\xa9 2024 Георгий Минулин (a.k.a. 63OR63). All rights reserved"
LEGAL_NOTICE = """
Copyright \xa9 2024 Георгий Минулин (a.k.a. 63OR63)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
