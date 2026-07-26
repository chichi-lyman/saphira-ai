"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - Core Intent Router Module
Purpose: Serves as Saphira's central decision engine, analyzing user intent 
and routing commands to the appropriate IoT, hardware, or entertainment controller.
"""

import logging
from typing import Dict, Any, Optional

# Import Saphira's sub-controllers
from saphira.iot.media_controller import MediaController
from saphira.iot.appliance_manager import ApplianceManager
from saphira.iot.lighting_controller import LightingController
from saphira.iot.smart_bed import SmartBedController
from saphira.entertainment.companion_hub import CompanionHub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraCoreRouter")

class SaphiraRouter:
    def __init__(self):
        self.media = MediaController()
        self.appliances = ApplianceManager()
        self.lighting = LightingController()
        self.bed = SmartBedController()
        self.companion = CompanionHub()

    async def process_intent(self, user_command: str) -> Dict[str, Any]:
        """
        Parses user commands in natural language and routes them to the correct subsystem.
        """
        cmd = user_command.lower()
        logger.info(f"Processing command for Chelsea Megan Woods: '{user_command}'")

        # 1. Media & TV Routing
        if any(keyword in cmd for keyword in ["tv", "channel", "movie", "show", "playing"]):
            if "channel" in cmd:
                return await self.media.change_channel(channel="requested channel")
            elif "playing" in cmd or "what's on" in cmd:
                return await self.media.get_what_is_playing()
            else:
                return await self.media.play_media(media_title=user_command)

        # 2. Lighting Routing
        elif any(keyword in cmd for keyword in ["light", "lights", "lamp", "color", "dim", "bright"]):
            if "color" in cmd:
                return await self.lighting.set_color(color="custom mood")
            elif "off" in cmd:
                return await self.lighting.power_light(state="off")
            else:
                return await self.lighting.power_light(state="on")

        # 3. Smart Vacuums & Appliance Routing
        elif any(keyword in cmd for keyword in ["vacuum", "clean", "sweep", "appliance"]):
            if "stop" in cmd or "dock" in cmd:
                return await self.appliances.control_vacuum(action="dock")
            else:
                return await self.appliances.control_vacuum(action="start")

        # 4. Smart Bed Routing
        elif any(keyword in cmd for keyword in ["bed", "mattress", "massage", "zero gravity"]):
            if "massage" in cmd:
                return await self.bed.control_massage(state="on", intensity=3)
            else:
                return await self.bed.adjust_position(section="head", angle_or_preset="reading")

        # 5. Companion, Music & Homework Routing
        elif any(keyword in cmd for keyword in ["sing", "song", "music", "play game", "homework", "help", "solve"]):
            if "sing" in cmd:
                return await self.companion.sing_song(song_title=user_command)
            elif "game" in cmd:
                return await self.companion.start_game(game_type="trivia")
            elif any(k in cmd for k in ["homework", "solve", "problem"]):
                return await self.companion.solve_problem_or_homework(topic_or_question=user_command)
            else:
                return await self.companion.select_music(genre_or_mood=user_command)

        # Fallback General Response
        return {
            "status": "success",
            "message": f"Saphira received your command: '{user_command}'. Processing in background to keep your day stress-free, Chelsea Megan Woods."
        }
