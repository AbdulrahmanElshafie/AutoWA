import FreeSimpleGUI as sg

# Fixed dimensions for the icon preview box (pixels)
PREVIEW_W = 500
PREVIEW_H = 400

# ----------------------------------------------------
# Usage Icons Layout
# ----------------------------------------------------
# Logic Flow:
# 1. This tab provides a two-column view to manage existing icons.
# 2. The left column lists all discovered icon directories.
# 3. The right column lists individual image variants for the selected icon.
# 4. A preview pane at the bottom shows a 500x400 rendering of the selected image.
# 5. Buttons are provided to Delete the selected image or Refresh the directory lists.
usage_icons_layout = [
    [sg.Text('Active Icons Directory:', font='Helvetica 12 bold')],
    [
        sg.Column([
            [sg.Text('Select Icon Folder:')],
            [sg.Listbox(values=[], size=(30, 8), key='-ICON_DIR_LIST-', enable_events=True, expand_x=True)],
        ]),
        sg.Column([
            [sg.Text('Count Status:', key='-ICON_COUNT_STATUS-', text_color='yellow')],
            [sg.Listbox(values=[], size=(40, 8), key='-ICON_IMG_LIST-', enable_events=True, expand_x=True)],
        ])
    ],
    [
        # Fixed-size preview container — never resizes with image content
        sg.Column([
            [sg.Text('Preview:')],
            [sg.Frame('', [
                [sg.Image(key='-ICON_PREVIEW-', size=(PREVIEW_W, PREVIEW_H))]
            ], size=(PREVIEW_W, PREVIEW_H), pad=(0, 0), relief=sg.RELIEF_SUNKEN)]
        ], element_justification='c', expand_x=True),
        sg.Column([
            [sg.Button('Delete Image', key='-DELETE_ICON_IMG-', button_color=('white', 'red'), expand_x=True)],
            [sg.Button('Refresh Icons', key='-REFRESH_ICONS-', expand_x=True)]
        ], element_justification='c', expand_x=True)
    ]
]


# ----------------------------------------------------
# UI Recovery Queue Layout
# ----------------------------------------------------
# Logic Flow:
# 1. This tab provides an interface for resolving missing UI element snapshots.
# 2. A Listbox at the top displays pending failures (screenshots of the full screen when an element wasn't found).
# 3. An interactive Graph (600x400) acts as a canvas where the user can draw a bounding box to crop the actual element.
# 4. Action buttons at the bottom allow the user to Crop, Undo/Redo, Save the crop to a specific icon folder, or Delete the failure.
recovery_queue_layout = [
    [sg.Text('Failed Elements Waiting Review:', font='Helvetica 12 bold')],
    [
        sg.Listbox(values=[], size=(75, 5), key='-RECOVERY_LIST-', enable_events=True, expand_x=True)
    ],
    [
        sg.Text('Click and drag to draw a crop box. Release to confirm. Click and drag again to redraw.')
    ],
    [
        # The Graph will be 600x400. Real coordinates will be mapped by events.
        sg.Graph(
            canvas_size=(600, 400),
            graph_bottom_left=(0, 400),
            graph_top_right=(600, 0),
            key='-CROP_GRAPH-',
            enable_events=True,
            drag_submits=True,
            background_color='gray'
        )
    ],
    [
        sg.Text('Save to Icon:'),
        sg.Combo(values=[], key='-SAVE_TARGET_ICON-', size=(30, 1), readonly=True),
        sg.Button('Crop', key='-CROP_RECOVERY-', button_color=('white', 'steelblue')),
        sg.Button('Undo', key='-UNDO_CROP-', button_color=('white', '#7c5cbf'), disabled=True),
        sg.Button('Redo', key='-REDO_CROP-', button_color=('white', '#5c7cbf'), disabled=True),
        sg.Button('Save', key='-CROP_SAVE_RECOVERY-', button_color=('white', 'seagreen')),
        sg.Button('Delete Recovery', key='-DELETE_RECOVERY-', button_color=('white', 'red')),
        sg.Button('Reload Queue', key='-RELOAD_RECOVERY_QUEUE-')
    ]
]

# ----------------------------------------------------
# Main Exported Layout
# ----------------------------------------------------
# Logic Flow:
# This bundles the two sub-layouts (Usage Icons and Recovery Queue) into a single
# TabGroup so it can be exported and integrated seamlessly into the main app window.
icons_management_layout = [
    [sg.Text('Icons Management & Recovery', font='Helvetica 16 bold', justification='center', expand_x=True)],
    [
        sg.TabGroup([[
            sg.Tab('Usage Icons', usage_icons_layout),
            sg.Tab('UI Recovery Queue', recovery_queue_layout)
        ]], expand_x=True, expand_y=True)
    ]
]
