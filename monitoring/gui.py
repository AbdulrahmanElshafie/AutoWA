import FreeSimpleGUI as sg

monitoring_layout = [
    [sg.Text('System Health Monitor', font='Helvetica 16 bold', justification='center', expand_x=True)],
    [
        sg.Column([
            [sg.Frame('Current Status', [[sg.Text('UNKNOWN', key='-HEALTH_STATUS-', font='Helvetica 20 bold', justification='c', expand_x=True)]], size=(200, 80), element_justification='c', expand_x=True)],
            [sg.Frame('Health Score', [[sg.Text('100', key='-HEALTH_SCORE-', font='Helvetica 24 bold', justification='c', expand_x=True)]], size=(200, 80), element_justification='c', expand_x=True)],
            [sg.Button('Check Health', key='-CHECK_HEALTH-', size=(20, 2), expand_x=True)]
        ], element_justification='c', expand_x=True),
        sg.Column([
            [sg.Frame('Recent Alerts', [[sg.Listbox(values=[], size=(40, 10), key='-ALERTS-', expand_x=True, expand_y=True)]], expand_x=True, expand_y=True)]
        ], expand_x=True, expand_y=True)
    ]
]
