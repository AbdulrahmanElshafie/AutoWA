import FreeSimpleGUI as sg

analytics_layout = [
    [sg.Text('Analytics Dashboard', font='Helvetica 16 bold', justification='center', expand_x=True)],
    [
        sg.Frame('Total Logs', [[sg.Column([[sg.Text('0', key='-TOTAL_ACTIONS-', font='Helvetica 32 bold', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True),
        sg.Frame('Failures', [[sg.Column([[sg.Text('0', key='-FAILURES-', font='Helvetica 32 bold', text_color='#FFA07A', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True),
        sg.Frame('Total Messages', [[sg.Column([[sg.Text('0', key='-TOTAL_MESSAGES-', font='Helvetica 32 bold', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True)
    ],
    [
        sg.Frame('Success Rate', [[sg.Column([[sg.Text('0.0%', key='-SUCCESS_RATE-', font='Helvetica 32 bold', text_color='#90EE90', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True),
        sg.Frame('Error Rate', [[sg.Column([[sg.Text('0.0%', key='-ERROR_RATE-', font='Helvetica 32 bold', text_color='#FF6666', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True),
    ],
    [
        sg.Frame('Avg Duration', [[sg.Column([[sg.Text('0.0s', key='-AVG_DURATION-', font='Helvetica 32 bold', justification='c')]], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True),
        sg.Frame('Throughput', [[sg.Column([
            [sg.Text('All Time: 0.0 msg/m', key='-THROUGHPUT_ALL-', font='Helvetica 16 bold', justification='c')],
            [sg.Text('Current Session: 0.0 msg/m', key='-THROUGHPUT_CUR-', font='Helvetica 16 bold', justification='c')],
            [sg.Text('Last Session: 0.0 msg/m', key='-THROUGHPUT_LAST-', font='Helvetica 16 bold', justification='c')]
        ], expand_x=True, expand_y=True, element_justification='c')]], element_justification='c', expand_x=True, expand_y=True)
    ],
    [sg.Button('Refresh Analytics', key='-REFRESH_ANALYTICS-', expand_x=True, size=(20, 2))]
]
