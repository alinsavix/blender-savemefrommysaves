# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.app.handlers import persistent
import os
from pprint import pprint
import shutil
import time

bl_info = {
    "name": "savemefrommysaves",
    "author": "TDV Alinsa",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}


class SaveMeFromMySavesPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    filepath: bpy.props.StringProperty(
        name="Example File Path",
        subtype='FILE_PATH',
    )
    number: bpy.props.IntProperty(
        name="Example Number",
        default=4,
    )
    boolean: bpy.props.BoolProperty(
        name="Example Boolean",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our add-on")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")


# class SaveMeFromMySaves_OT_Preferences(bpy.types.Operator):
#     """Display example preferences"""
#     bl_idname = "object.addon_prefs_example"
#     bl_label = "Add-on Preferences Example"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         preferences = context.preferences
#         addon_prefs = preferences.addons[__name__].preferences

#         info = ("Path: %s, Number: %d, Boolean %r" %
#                 (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

#         self.report({'INFO'}, info)
#         print(info)

        # return {'FINISHED'}


def nn(name: str, number: int) -> str:
    """create a filename given a path and a generation number"""

    fn, ext = os.path.splitext(name)
    return f"{fn}__{number}{ext}"


def is_close(a, b, prec):
    return f'{a:.{prec}f}' == f'{b:.{prec}f}'


@persistent
def fixsaves(dummy1, dummy2):
    # if not bpy.context.
    sep = os.path.sep
    d_sep = sep + sep
    age_threshold = 5
    subdir = "blend.saves"
    savefiles = 20

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    f_path = bpy.data.filepath
    if not os.path.exists(f_path):
        print("no source file '%s' found, not saving file copy" % (f_path))
        return

    if f"{os.path.sep}{subdir}{os.path.sep}" in f_path:
        print(
            f"file '{f_path}'' is already in save directory '{subdir}'', not saving copy")
        return

    # Kind of arbitrary -- if older than a few seconds old, we are
    # possibly saving a copy, so don't save a useless file?
    # Not needed, while doing pre-save, but keeping in case we want
    # to switch back to post-save again

    # save_mtime = os.path.getmtime(f_path)
    # curtime = int(time.time())

    # if save_mtime < curtime - age_threshold:
    #     print("save file %s too old (age %d > %d)" %
    #           (f_path, curtime - save_mtime, age_threshold))
    # else:
    #     print("save file %s is young enough (age %d < %d)" %
    #           (f_path, curtime - save_mtime, age_threshold))

    # save file (no path)
    s_file = os.path.basename(f_path)

    # The directories stuff has to happen in (input path, output path)
    i_dir = os.path.dirname(f_path)
    o_dir = os.path.join(i_dir, subdir)

    # Output directory and filename (minus numeric suffix)
    o_dirfile = os.path.join(o_dir, s_file)

    # if we have a target file and a current file, see if they're
    # the same (w/ timestamp)
    if os.path.exists(nn(o_dirfile, 1)):
        mtime_src = os.path.getmtime(f_path)
        mtime_dest = os.path.getmtime(nn(o_dirfile, 1))

        # print("%f ? %f" % (mtime_src, mtime_dest))

        if is_close(mtime_src, mtime_dest, 3):
            print(
                "Not creating backup version for '%s', seems identical to most recent backup version" % (f_path))
            return

    # make sure we have a save directory
    if not os.path.exists(o_dir):
        os.mkdir(o_dir)

    # check to see if the max # exists, so we can clean it out
    if os.path.exists(nn(o_dirfile, savefiles)):
        print("removing oldest save file (%s)" % (nn(o_dirfile, savefiles)))
        os.remove(nn(o_dirfile, savefiles))

    # cycle through any other save filees and rename them
    for i in reversed(list(range(1, savefiles))):
        if os.path.exists(nn(o_dirfile, i)):
            # print("would rename %s" % (nn(o_dirfile, i)))
            os.rename(nn(o_dirfile, i), nn(o_dirfile, i + 1))

    # And finally, copy our save file
    print("copying %s to %s" % (f_path, nn(o_dirfile, 1)))
    shutil.copy2(f_path, nn(o_dirfile, 1), follow_symlinks=False)


# Registration
def register():
    # bpy.utils.register_class(SaveMeFromMySaves_OT_Preferences)
    bpy.utils.register_class(SaveMeFromMySavesPreferences)
    if fixsaves not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(fixsaves)


def unregister():
    # bpy.utils.unregister_class(SaveMeFromMySaves_OT_Preferences)
    bpy.utils.unregister_class(SaveMeFromMySavesPreferences)
    if fixsaves in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(fixsaves)
