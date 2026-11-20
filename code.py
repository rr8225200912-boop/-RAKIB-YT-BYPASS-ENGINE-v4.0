import os
import sys
import logging
import subprocess
import time
import random
import uuid
from pyrogram import Client, filters, emoji
import json

# ================= CONFIGURATION SECTION =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("API_ID and API_HASH are required.")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= PYROGRAM CLIENT SETUP =================
app = Client(
    "rakib_yt_bypass_v10",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ================= HELPER FUNCTIONS =================

def run_ffmpeg_command(cmd):
    """Executes ffmpeg with robust error handling"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg Error: {e.stderr[-200:]}") # Log last 200 chars of error
        return False

def get_video_info(file_path):
    """Robust metadata extraction"""
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_streams', '-show_format', file_path
    ]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    
    if probe_result.returncode != 0:
        raise Exception(f"ffprobe failed: {probe_result.stderr}")
        
    try:
        info = json.loads(probe_result.stdout)
    except json.JSONDecodeError:
        raise Exception("Failed to parse ffprobe output.")
    
    streams = info.get('streams', [])
    video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    
    if not video_stream:
        raise Exception("No video stream found.")

    width = int(video_stream.get('width', 1920))
    height = int(video_stream.get('height', 1080))
    
    fps_str = video_stream.get('r_frame_rate', '30/1')
    try:
        fps_num, fps_den = map(int, fps_str.split('/'))
        fps = fps_num / fps_den if fps_den else 30
    except ValueError:
        fps = 30
        
    duration = float(info.get('format', {}).get('duration', 0))
    
    return {
        "width": width,
        "height": height,
        "fps": fps,
        "duration": duration,
        "has_audio": audio_stream is not None
    }

async def rakib_brute_process_v10(input_file):
    """
    RAKIB's Brute Force Processing Method v10.0
    Features:
    1. Large Scale Mutation (3-5% Randomized Scaling)
    2. Timestamp & Speed Shifting (Audio Fingerprint Disruption)
    3. Noise Injection (Visual Hash Mutation)
    4. True Metadata Sanitization (Wiping)
    """
    unique_id = str(uuid.uuid4())[:8]
    output_file = f"rakib_final_{unique_id}.mp4"
    
    logger.info(f"Starting RAKIB Engine v10.0 (Brute Force) for job {unique_id}...")
    
    # Step 1: Get Info
    try:
        info = get_video_info(input_file)
    except Exception as e:
        raise Exception(f"Info extraction failed: {e}")
        
    w, h, fps = info['width'], info['height'], info['fps']
    has_audio = info['has_audio']
    
    logger.info(f"Input: {w}x{h}, FPS: {fps}, Duration: {info['duration']}s")
    
    # Step 2: Dynamic/Stochastic Parameters
    
    # A. Visual Filters: Large Scale Mutation
    # Scale factor between 0.95 and 1.05 (Random every time)
    scale_factor = round(random.uniform(0.95, 1.05), 3)
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    
    # Ensure even dimensions
    if new_w % 2 != 0: new_w += 1
    if new_h % 2 != 0: new_h += 1
    
    # Random Color Curve Mutation (Chromatic Aberration Simulation)
    r_mul = round(random.uniform(0.95, 1.05), 2)
    g_mul = round(random.uniform(0.95, 1.05), 2)
    b_mul = round(random.uniform(0.95, 1.05), 2)
    
    visual_filters = [
        f'scale={new_w}:{new_h}:flags=lanczos',
        'noise=alls=10:allf=t2',                  # Temporal noise
        f'colorchannelmixer="{r_mul} 0 0 0 | 0 {g_mul} 0 0 | 0 0 {b_mul} 0 | 0 0 0 1"'
    ]
    
    # B. Audio Filters: Timestamp & Speed Shifting
    # Using atempo to change speed slightly (breaks fingerprinting)
    # Using asetpts to shift timestamps (breaks sync detection)
    audio_filter = ""
    if has_audio:
        # Random speed change between 0.98x and 1.02x
        speed_change = round(random.uniform(0.98, 1.02), 3)
        # Timestamp shift by small random amount
        ts_shift = round(random.uniform(-0.1, 0.1), 3)
        
        audio_filter = f'[a:a]atempo={speed_change},asetpts=PTS+{ts_shift}[T]'
        
    filter_complex = f"[0:v]{','.join(visual_filters)}[v];{audio_filter}" if audio_filter else f"[0:v]{','.join(visual_filters)}[v]"
    
    # Step 3: Build Command with True Metadata Wiping
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-c:v', 'libx264',
        '-preset', 'medium', # Balanced speed/quality
        '-crf', '22',       # High quality
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        # True Metadata Wiping: Remove ALL existing metadata
        '-map_metadata', '-1',
        # No extra metadata added, so it remains clean
    ]
    
    if audio_filter:
        cmd.extend(['-map', '[T]', '-c:a', 'aac', '-b:a', '192k'])
    else:
        cmd.extend(['-c:a', 'copy'])
        
    cmd.append(output_file)
    
    logger.info(f"Executing FFmpeg pipeline with Scale Factor: {scale_factor}")
    success = run_ffmpeg_command(cmd)
    
    if not success or not os.path.exists(output_file):
        raise Exception("RAKIB Optimization failed during FFmpeg execution.")
        
    return output_file

# ================= MAIN BOT LOGIC =================

@app.on_message(filters.document | filters.video)
async def handle_video(client, message):
    start_time = time.time()
    
    status_msg = await message.reply_text(
        f"{emoji.FLAG_BD} **RAKIB ENGINE v10.0 (BRUTE FORCE)** Active...\n\n"
        "🔄 Layer 1: Large Scale Mutation (3-5%)\n"
        "🔄 Layer 2: Audio Speed & Timestamp Shifting\n"
        "🔄 Layer 3: Chromatic Mutation\n"
        "🔄 Layer 4: Metadata Wiping (True)"
    )
    
    file_path = None
    output_path = None
    
    try:
        logger.info(f"Downloading file ID: {message.id}")
        file_path = await client.download_media(message)
        
        if not file_path or not os.path.exists(file_path):
            raise Exception("Download failed or empty file.")

        output_path = await rakib_brute_process_v10(input_file=file_path)
            
        # Improved Progress Handling
        async def progress(current, total):
            percent = (current / total) * 100
            status_msg.edit_text(f"⬆️ Uploading... {percent:.1f}%")
            
        await message.reply_video(
            video=output_path, 
            caption="✅ **RAKIB ENGINE: PROCESSING COMPLETE**\n\n"
                    "🛡️ Protected by Multi-Layer Algorithm Evasion.\n"
                    "📊 Resolved: AI-Mutated\n"
                    "🎵 Audio: Speed/Timestamp Shifted\n"
                    "👤 Engine: ADMIN RAKIB",
            progress=progress
        )
            
        duration = time.time() - start_time
        logger.info(f"Processing completed in {duration:.2f} seconds.")
        await status_msg.edit_text(f"✅ Done! Time taken: {duration:.2f}s")

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.exception(error_msg)
        await status_msg.edit_text(error_msg)
        
    finally:
        # Cleanup
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app.run()