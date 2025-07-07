"""NICOS GUI default configuration."""

main_window = docked(
    tabbed(
        ('Command line',
         vsplit(
            panel('nicos.clients.gui.panels.console.ConsolePanel', hasinput=True),
            panel('nicos.clients.gui.panels.status.ScriptStatusPanel', eta=True),
         ),
        ),
        ('Script Builder',
         vsplit(
             panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
             panel('nicos.clients.gui.panels.editor.EditorPanel',
                   tools=[
                       tool('Scan Generator',
                            'nicos.clients.gui.tools.scan.ScanTool')
                   ]),
         )),
        ('Experiment Information and Setup',
         panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
               # to configure panels to show on New/FinishExperiment
               # new_exp_panel=panel('nicos_demo.demo.some.panel'),
               # finish_exp_panel=panel('nicos_demo.demo.some.panel'),
              )
        ),
    ),

    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel',
           dockpos='right',
           param_display={'Exp': ['lastpoint', 'lastscan']},
           filters=[('Detector', 'det'),
                    ('Temperatures', '^T'),
                   ],
          )
    ),
)

windows = [
    window('Setup', 'setup',
        tabbed(
            ('Experiment',
             panel('nicos.clients.gui.panels.setup_panel.ExpPanel')),
            ('Setups',
             panel('nicos.clients.gui.panels.setup_panel.SetupsPanel')),
            ('Detectors/Environment',
             panel('nicos.clients.gui.panels.setup_panel.DetEnvPanel')),
        ),
    ),
    window('Editor', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel',
              tools = [
                  tool('Scan Generator',
                       'nicos.clients.gui.tools.scan.ScanTool')
              ]))),
    window('Scans', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
    window('Log files', 'table',
           panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
    window('Errors', 'errors',
           panel('nicos.clients.gui.panels.errors.ErrorPanel')),
    window('Live data', 'live',
           panel('nicos.clients.gui.panels.live.LiveDataPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
    tool('Emergency stop button',
         'nicos.clients.gui.tools.estop.EmergencyStopTool',
         runatstartup=False),
]
