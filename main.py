"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - Main Application Entry Point
Purpose: Initializes the FastAPI server, connects all IoT, manufacturing,
entertainment modules, and Saphira Nodes (eyes/ears/hands/screens),
and serves as the central command hub for Saphira.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Union

# Import Saphira's custom modules
from saphira.iot.media_controller import MediaController
from saphira.iot.appliance_manager import ApplianceManager
from saphira.iot.lighting_controller import LightingController
from saphira.iot.smart_bed import SmartBedController
from saphira.iot.print_controller import PrintController
from saphira.entertainment.companion_hub import CompanionHub

# Saphira Nodes — OpenClaw-inspired companion device surface
from src.api.nodes_router import router as nodes_router
from src.nodes.registry import node_registry

app = FastAPI(
    title="Saphira AI Ecosystem",
    description=(
        "Autonomous multi-agent and IoT control hub with physical Nodes "
        "(code, canvas, media, mobile) — architected by Chelsea Megan Woods."
    ),
    version="1.1.0",
)

# Nodes API surface
app.include_router(nodes_router)

# Initialize controllers
media = MediaController()
appliances = ApplianceManager()
lighting = LightingController()
bed = SmartBedController()
printer = PrintController()
companion = CompanionHub()

# Seed development nodes so /nodes and invoke work out of the box
def _seed_dev_nodes():
    node_registry.register(
        name="saphira-headless",
        node_type="headless",
        platform="linux",
        host="localhost",
        auto_approve=True,
        metadata={"role": "dev-code-node", "owner": "Chelsea Megan Woods"},
    )
    node_registry.register(
        name="saphira-canvas",
        node_type="canvas",
        platform="web",
        host="localhost",
        auto_approve=True,
        metadata={"role": "dev-dashboard-node", "owner": "Chelsea Megan Woods"},
    )
    node_registry.register(
        name="saphira-media",
        node_type="media",
        platform="linux",
        host="localhost",
        auto_approve=True,
        metadata={"role": "dev-render-node", "owner": "Chelsea Megan Woods"},
    )


_seed_dev_nodes()


# Request Models
class MediaRequest(BaseModel):
    media_title: str
    device_id: Optional[str] = None


class ChannelRequest(BaseModel):
    channel: Union[str, int]
    device_id: Optional[str] = None


class VacuumRequest(BaseModel):
    action: str
    device_id: Optional[str] = None


class LightPowerRequest(BaseModel):
    state: str
    device_id: Optional[str] = None


class LightColorRequest(BaseModel):
    color: str
    device_id: Optional[str] = None


class BedPositionRequest(BaseModel):
    section: str
    angle_or_preset: Union[int, str]
    device_id: Optional[str] = None


class PrintJobRequest(BaseModel):
    file_name: str
    device_id: Optional[str] = None


class PrintActionRequest(BaseModel):
    action: str
    device_id: Optional[str] = None


class EntertainmentRequest(BaseModel):
    query: str


@app.get("/")
async def root():
    return {
        "architect": "Chelsea Megan Woods",
        "system": "Saphira AI Active",
        "status": "Online and ready to make life 1% easier.",
        "nodes": node_registry.status_summary(),
    }


# --- Media & TV Endpoints ---
@app.post("/iot/media/play")
async def play_media(req: MediaRequest):
    return await media.play_media(req.media_title, req.device_id)


@app.post("/iot/media/channel")
async def change_channel(req: ChannelRequest):
    return await media.change_channel(req.channel, req.device_id)


@app.get("/iot/media/status")
async def get_what_is_playing(device_id: Optional[str] = None):
    return await media.get_what_is_playing(device_id)


# --- Appliance & Vacuum Endpoints ---
@app.post("/iot/vacuum")
async def control_vacuum(req: VacuumRequest):
    return await appliances.control_vacuum(req.action, req.device_id)


# --- Lighting Endpoints ---
@app.post("/iot/lights/power")
async def power_light(req: LightPowerRequest):
    return await lighting.power_light(req.device_id, req.state)


@app.post("/iot/lights/color")
async def set_light_color(req: LightColorRequest):
    return await lighting.set_color(req.color, req.device_id)


# --- Smart Bed Endpoints ---
@app.post("/iot/bed/position")
async def adjust_bed(req: BedPositionRequest):
    return await bed.adjust_position(req.section, req.angle_or_preset, req.device_id)


# --- 3D Printing Endpoints ---
@app.get("/iot/printer/status")
async def get_print_status(device_id: Optional[str] = None):
    return await printer.get_print_status(device_id)


@app.post("/iot/printer/start")
async def start_print(req: PrintJobRequest):
    return await printer.start_print(req.file_name, req.device_id)


@app.post("/iot/printer/control")
async def control_print_job(req: PrintActionRequest):
    return await printer.control_print_job(req.action, req.device_id)


# --- Companion & Entertainment Endpoints ---
@app.post("/entertainment/music")
async def select_music(req: EntertainmentRequest):
    return await companion.select_music(req.query)


@app.post("/entertainment/sing")
async def sing_song(req: EntertainmentRequest):
    return await companion.sing_song(req.query)


@app.post("/entertainment/game")
async def start_game(req: EntertainmentRequest):
    return await companion.start_game(req.query)


@app.post("/entertainment/solve")
async def solve_problem(req: EntertainmentRequest):
    return await companion.solve_problem_or_homework(req.query)
