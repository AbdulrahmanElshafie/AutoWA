import FreeSimpleGUI as sg

# Fixed dimensions for the icon preview box (pixels)
PREVIEW_W = 500
PREVIEW_H = 400

# ----------------------------------------------------
# Usage Icons Layout
# ----------------------------------------------------
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
icons_management_layout = [
    [sg.Text('Icons Management & Recovery', font='Helvetica 16 bold', justification='center', expand_x=True)],
    [
        sg.TabGroup([[
            sg.Tab('Usage Icons', usage_icons_layout),
            sg.Tab('UI Recovery Queue', recovery_queue_layout)
        ]], expand_x=True, expand_y=True)
    ]
]
