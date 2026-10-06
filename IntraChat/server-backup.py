# Copyright 2026 cHamster24

from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketDisconnect
import json
from datetime import datetime, timezone
import re

app = FastAPI()

# Basic Room Hosting
connections = [] #temp connections list
rooms = {}
@app.websocket("/ws/{room}")



#---
# Chat slash (/) commands TODO
slashcmds = {
	"/help": {
		"id": 0,
		"syntax": "/help",
		"desc": "Displays the help information"
	},
	"/who": {
		"id": 1,
		"syntax": "/who",
		"desc": "Shows who is currently online in your room"
	},
	"/report": {
		"id": 2,
		"syntax": "/report [user] [reason]",
		"desc": "Report a user"
	},
	"/em": {
		"id": 3,
		"syntax": "/em \"[action]\"",
		"desc": "Emote to do an action. E.g. '/em \"eats a pizza!\"' results in '[User] eats a pizza!'"
	},
	"/room": {
		"id": 4,
		"syntax": "/room [new room code]",
		"desc": "Attempts to join a different room"
	},
	"/quit": {
		"id": 5,
		"syntax": "/quit",
		"desc": "Leaves the room"
	},
	"/name": {
		"id": 6,
		"syntax": "/name [new name]",
		"desc": "Changes your current username", # TODO: MAKE SURE WHEN CODING THIS ONE TO STOP USERS FROM NAMING THEMSELVES AS ANOTHER PERSON IN THE SAME ROOM
	},
	"/md": {
		"id": 7,
		"syntax": "/md \"[message]\"",
		"desc": "Sends a message in markdown"
	},
	"/kick": {
		"id": 8, 
		"syntax": "/kick [user]",
		"desc": "[ADMIN ONLY] Kicks a user"
		"secure": True
	},
	"/whisper": {
		"id": 9, 
		"syntax": "/whisper [user] \"[message]\"",
		"desc": "ends a private message to a specific user"
	}
}

def act_slashcmd(msg): #TODO: MAKE SURE TO PARSE THE FIRST "WORD" AND DELETE ANYTHING AFTER THE FIRST SPACE WHEN MATCHING TO LIST
	pass # Should check against list slashcmds, then see if it is else return message f"{msg} is not a valid slash command. Type \"/help\" for more info."





#---------------
# MAIN SCRIPT
#---------------

async def websocket_endpoint(websocket: WebSocket, room: str):
	await websocket.accept()
	connections.append(websocket)
	SAFE_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
	SAFE_ROOMCODE_PATTERN = re.compile(r'^[a-zA-Z0-9]+$')
	try:
		while True:
			jsonMsg = await websocket.receive_text()
			msg = json.loads(jsonMsg)
			
			if msg["type"] == "join": #actual join message
				#Username XSS check
				try:
					if not SAFE_USERNAME_PATTERN.match(msg["username"]):
						print(f"SECURITY ALERT: Rejected unsafe username attempt: {msg["username"]}")
						await websocket.send_text(json.dumps({
							"type": "message",
							"username": "*system",
							"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
							"message": "Something went wrong with your username! We're disconnecting you...",
							"room": str(msg["room"])
						}))
						return
				except Exception:
					print(f"SECURITY ALERT: Rejected username attempt (raised EXCEPTION): {msg["username"]}")
					return

				#Safe room code check
				try:
					if not SAFE_ROOMCODE_PATTERN.match(msg["room"]):
						print(f"SECURITY ALERT: Rejected unsafe roomcode attempt: {msg["room"]}")
						await websocket.send_text(json.dumps({
							"type": "message",
							"username": "*system",
							"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
							"message": "Something went wrong with your roomcode! We're disconnecting you...",
							"room": str(msg["room"])
						}))
						return
				except Exception:
					print(f"SECURITY ALERT: Rejected roomcode attempt (raised EXCEPTION): {msg["username"]}")
					return

				room_code = msg["room"].lower()
				if room_code in rooms: #checks for dupe username SCRIPT
					existing_usernames_lower = {name.lower() for name in rooms[room_code].values()}
					if msg["username"].lower() in existing_usernames_lower: #checks for username in a EXISTING room
						try:
							await websocket.send_text(json.dumps({
								"type": "message", 
								"username": "*system", 
								"message": "It seems like someone with the same username as you is in this room as well. As such, we are disconnecting you from this room to avoid identification errors.", 
								"room": room_code,
								"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
							}))
						except:
							pass
						if websocket in connections:
							connections.remove(websocket)
						print(f"Removing {websocket} from {room_code} for dupe username.")
						return
						
					else:
						pass #room dosnt contain user
				if not room_code in rooms: #create a new room
					rooms[room_code] = {}
					
				rooms[room_code][websocket] = msg["username"]
				if websocket in connections:
					connections.remove(websocket)
				for sock in rooms.get(room_code, {}).keys(): #broadcasts join msg
					try:
						await sock.send_text(json.dumps({
							"type": "message",
							"username": "*system",
							"message": f"{msg['username']} joined the room.",
							"room": room_code,
							"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
							}))
					except Exception:
						pass
				break
			else:
				return
				
	except Exception:
		return

	
	# -----
	# MESSAGE MANAGING
	# -----
	try:
		while True:
			jsonMsg = await websocket.receive_text()
			msg = json.loads(jsonMsg)
			if msg["type"] == "message":
				if not str(msg["message"]).startswith("/"): #handles messages, not cmds
					corr_room = next((room for room, users in rooms.items() if websocket in users), None)
					if corr_room:
						for sock in list(rooms[corr_room].keys()):
							await sock.send_text(json.dumps({
								"type": "message",
								"message": msg["message"],
								"username": rooms[corr_room][websocket],
								"room": corr_room,
								"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
							}))
						
				else: #handles commands
			
					#FIX INDENTATION TYPE AND ALSO DO LIST BASED WITH A FUNCTION INSTEAD OF THIS

		    
					if str(msg["message"]) == "/here": #TODO
						pass
					elif str(msg["message"]) == "":
						pass
					else:
						for sock, username in rooms.get(room_code, {}).items():
							if username == msg["username"]:
								await sock.send_text(json.dumps({
									"type": "message",
									"username": "*system",
									"message": "Sorry, but we currently do NOT handle commands.",
									"room": room_code,
									"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
								}))

			else: #handles other messages
				pass
				
	except (Exception, WebSocketDisconnect):
		try:
			await websocket.send_text(json.dumps({
				"type": "message", 
				"username": "*system", 
				"message": "An error occured. We're trying to disconnect you from the server...", 
				"room": room_code,
				"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
			}))
		except:
			pass

		# remove from temp list
		if websocket in connections:
			connections.remove(websocket)

		user_disconnected = None
		socket_disconnected = None
		for room, users in rooms.items():
			for sock, username in users.items():
				if sock == websocket:
					user_disconnected = username
					room_disconnected = room
					del rooms[room_disconnected][websocket]
					break
			if user_disconnected:
				break
				
		if user_disconnected and room_disconnected:
			exit_message = {
				"type": "message",
				"username": "*system",
				"message": f"{user_disconnected} has left the room.",
				"room": room_disconnected,
				"timestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
			}

			if room_disconnected in rooms:
				for sock in rooms[room_disconnected].keys():
					try:
						await sock.send_text(json.dumps(exit_message))
					except Exception:
						pass
			if not rooms[room_disconnected]:
				del rooms[room_disconnected]

	finally:
		try:
			await websocket.close()
		except Exception:
			pass

@app.route("/keep-alive", methods=["GET", "HEAD"])
async def keep_alive(request: Request): #keep alive
	return {"status": "awake"}
	
app.mount("/", StaticFiles(directory="static", html=True), name="static") #LAST PART FOR SERVING STATIC FILES
app.mount("/", StaticFiles(directory=".", html=True), name="root_static") #Mainly for version #
