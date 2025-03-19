"""

"""
import platform
import os
import glob
import sys
import errno
import json
# /users/me/Conductor/ciohoudini
PKG_DIR = os.path.dirname(os.path.abspath(__file__))

# /users/me/Conductor/
CIO_DIR = os.path.dirname(PKG_DIR).replace("\\","/")
# ciohoudini
PKGNAME = os.path.basename(PKG_DIR)

PLATFORM = sys.platform
with open(os.path.join(PKG_DIR, 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

WIN_MY_DOCUMENTS = 5
WIN_TYPE_CURRENT = 0

# In development, we want to refer to the HDA in the dev location (under env var CIO).
# In production, we want to move the HDA to the user's Conductor directory.
# The python package is always pip installed in the user's Conductor directory. 
if os.environ.get("CIO_FEATURE_DEV"):
    houdini_path = os.path.join(os.environ.get("CIO"), "ciohoudini","ciohoudini")
else:
    houdini_path = "$CIODIR/ciohoudini"

PACKAGE_FILE_CONTENT = {
    "env": [
        {
            "CIODIR": CIO_DIR
        },
         {
            "var": "HOUDINI_PATH",
            "value": [
               houdini_path
            ]
        },
        {
            "PYTHONPATH": {
                "method": "prepend",
                "value": [
                    "$CIODIR"
                ]
            }
        }
    ]
}

def main():
    if not PLATFORM in ["darwin", "win32", "linux"]:
        sys.stderr.write("Unsupported platform: {}".format(PLATFORM))
        sys.exit(1)
    package_files = get_package_files()
    if not package_files:
        sys.stderr.write("***************************.\n")
        sys.stderr.write("Could not find your Houdini packages folder.\n")
        sys.stderr.write("You will need to copy over the Conductor package JSON manually, like so:\n")
        sys.stderr.write("Go to your houdini prefs folder and create a folder there called packages.\n")
        pkg_file = os.path.join(CIO_DIR, "conductor.json")
        sys.stderr.write("Copy this file there {}.\n".format(pkg_file))
        with open(pkg_file, 'w') as f:
            json.dump(PACKAGE_FILE_CONTENT, f, indent=4)
        sys.stderr.write("***************************.\n")
        sys.stderr.write("\n")
        sys.exit(1)

    for pkg_file in package_files:
        pkg_file = pkg_file.replace("\\","/")
        folder = os.path.dirname(pkg_file)
        try:
            print("Ensure directory exists: {}".format(folder))
            ensure_directory(folder)
        except BaseException:
            sys.stderr.write("Could not create directory: {}. Skipping\n".format(folder))
            continue

        with open(pkg_file, 'w') as f:
            json.dump(PACKAGE_FILE_CONTENT, f, indent=4)

        sys.stdout.write("Added Conductor Houdini package file: {}".format(pkg_file))


def get_package_files():

    if PLATFORM == "darwin":
        pattern = os.path.expanduser("~/Library/Preferences/houdini/[0-9][0-9]*")
    elif PLATFORM == "linux":
        pattern = os.path.expanduser("~/houdini[0-9][0-9]*")
    else:  # windows
        import ctypes.wintypes
        buff = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW( None, WIN_MY_DOCUMENTS, None, WIN_TYPE_CURRENT, buff)
        documents = buff.value
        pattern = "{}/houdini[0-9][0-9]*".format(documents)

    return [os.path.join(p, "packages", "conductor.json") for p in glob.glob(pattern)]


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            sys.stderr.write("All good! Directory exists: {}\n".format(directory))
            pass
        else:
            raise


if __name__ == '__main__':
    main()
