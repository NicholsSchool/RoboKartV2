import json
import paho.mqtt.client as mqtt
import sys
from nicegui import app, ui
import UIUtil
import logging
from zenoh import Sample
import MQTTSessionManager

UIUtil.injectCSS()
LOG_TAG = "FMS UI"

with ui.dialog() as dialog, ui.card().classes('w-6xl'):
    ui.label('FMS Logs')
    UIUtil.registerLog()
    ui.button('Close', on_click=dialog.close)

with ui.header(elevated=True).classes('items-center justify-between bg-neutral-800'):
        with ui.row().classes("items-center"):
            ui.image("Logo.svg").classes("w-72")
            ui.label('Field Management System').classes('text-2xl font-bold')
        with ui.row():
            async def shutdown():
                UIUtil.log(logging.INFO, LOG_TAG, "Received shutdown command from client, shutting down...")
                await ui.run_javascript('window.close()').wait_for_result()
                MQTTSessionManager.close()
                app.shutdown()
            
            ui.button("Logs", on_click=dialog.open).props('outline square')
            ui.button("Shutdown FMS", on_click=shutdown, color='negative').props('outline square')

with ui.grid(columns=2).classes("w-full *:flex *:grow"):
    # Connections Card
    with ui.card():
        ui.label("Active Connections")
        with ui.table(rows=[], columns=[]).classes('w-full') as connTable:
        
            connTable.columns = [
                {'name': 'type', 'label': 'Type', 'field': 'type', 'required': True, 'align': 'left'},
                {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
                {'name': 'battery', 'label': 'Battery', 'field': 'battery', 'sortable': True},
            ]
            connTable.rows = []
            connTable.row_key = 'id'

            def updateTable(client, userdata, msg):
                
                tableRows = []
                
                for row in MQTTSessionManager.sessionPeers:
                    heartbeatInfo = row['heartbeatInfo']
                    tableRows.append({
                        'type': row['type'],
                        'id': row['id'],
                        'battery': heartbeatInfo['battery'],
                    })

                connTable.rows = tableRows

            # ZenohSessionManager.registerSessionPeerUpdateCallback("Connections Table", updateTable)
            MQTTSessionManager.subscriptions["HEARTBEAT"].addCallback("Connections Table", updateTable)
            
    with ui.card():
        ui.label("Controller Inputs")
        with ui.table(rows=[], columns=[]).classes('w-full') as inpTable:
            inpTable.columns = [
                {'name': 'id', 'label': 'Controller', 'field': 'id', 'required': True, 'align': 'left'},
                {'name': 'turn', 'label': 'Turn Input', 'field': 'turn'},
                {'name': 'strafe', 'label': 'Strafe Input', 'field': 'strafe'},
                {'name': 'forward', 'label': 'Forward Input', 'field': 'forward'},
                {'name': 'backward', 'label': 'Backward Input', 'field': 'backward'},
            ]
            inpTable.rows = []
            inpTable.row_key = 'id'

            def updateTableWithInput(client, userdata, msg: mqtt.MQTTMessage):
                for row in inpTable.rows:
                    if row["id"] == str(msg.topic).split("/")[1]:
                        sampleData = json.loads(str(msg.payload))
                        row.update({
                            'id': row["id"],
                            'turn': sampleData["turn"],
                            'strafe': sampleData["strafe"],
                            'forward': sampleData["forward"],
                            'backward': sampleData["backward"],
                        })

            def updateTableWithPeerUpdate(client, userdata, msg):
                
                sessionPeers = MQTTSessionManager.sessionPeers
                
                peerIDList = [peer["id"] for peer in sessionPeers if peer["type"] == "Controller"]
                tableIDList = [row["id"] for row in inpTable.rows]
                
                for i in range(len(peerIDList)):
                    if (tableIDList.count(peerIDList[i]) < 1):
                        inpTable.rows.append({
                            'id': peerIDList[i],
                            'turn': 0,
                            'strafe': 0,
                            'forward': False,
                            'backward': False,
                        })
                for i in range(len(tableIDList)):
                    if (peerIDList.count(tableIDList[i]) < 1):
                        inpTable.rows.pop(i)

            # ZenohSessionManager.registerControllerUpdateCallback("Inputs Table", updateTableWithInput)
            # ZenohSessionManager.registerSessionPeerUpdateCallback("Inputs Table", updateTableWithPeerUpdate)
            MQTTSessionManager.subscriptions["CONTROLLER_INPUT"].addCallback("Inputs Table", updateTableWithInput)
            MQTTSessionManager.subscriptions["HEARTBEAT"].addCallback("Inputs Table", updateTableWithPeerUpdate)

MQTTSessionManager.init()
UIUtil.log(logging.INFO, LOG_TAG, "FMS Initialization Finished.")
ui.dark_mode().enable()
ui.run(reload=False)