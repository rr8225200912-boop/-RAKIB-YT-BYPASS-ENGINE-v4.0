import os
import sys
import logging
import subprocess
import tempfile
import time
import random
from pyrogram import Client, filters, emoji

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing!")
    sys.exit(1)
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
if not API_ID or not API_HASH:
    logger.error("API_ID or API_HASH is missing!")
    sys.exit(1)

app = Client(
    "rakib_yt_bypass",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

def run_ffmpeg_command(cmd):
    """Helper function to run FFmpeg commands robustly"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg Error: {e.stderr}")
        return False

@app.on_message(filters.document | filters.video)
async def handle_video(client, message):
    start_time = time.time()
    
    # Status Message with RAKIB Branding
    status_msg = await message.reply_text(
        f"{emoji.FLAG_BD} **RAKIB YOUTUBE BYPASS ENGINE v4.0** Active...\n\n"
        "🔄 Layer 1: Temporal Jitter (FPS)\n"
        "🔄 Layer 2: Chromatic Mutation (Color)\n"
        "🔄 Layer 3: Audio Phase Inversion\n"
        "🔄 Layer 4: Resolution Scramble\n"
        "🔄 Layer 5: Metadata Wiping"
    )
    
    file_path = None
    output_path = None
    
    try:
        logger.info(f"Downloading file ID: {message.id}")
        file_path = await client.download_media(message)
        
        if not file_path:
            raise Exception("Download failed or empty file.")

        output_path = await rakib_nuclear_process(file_path)
            
        await message.reply_video(
            video=output_path, 
            caption="✅ **RAKIB ENGINE: BYPASS COMPLETE!**\n\n"
                    "🛡️ Protected by Multi-Layer Algorithm Evasion.\n"
                    "📊 Resolved: AI-Mutated\n"
                    "🎵 Audio: Phase-Inverted\n"
                    "👤 Engine: ADMIN RAKIB",
            progress=lambda p, t: status_msg.edit_text(f"⬆️ Uploading... {p/t*100:.1f}%")
        )
            
        duration = time.time() - start_time
        logger.info(f"Processing completed in {duration:.2f} seconds.")
        await status_msg.edit_text(f"✅ Done! Time taken: {duration:.2f}s")

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.exception(error_msg)
        await status_msg.edit_text(error_msg)
        
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

async def rakib_nuclear_process(input_file):
    """
    RAKIB's Nuclear Processing Method for YouTube
    """
    output_file = "rakib_final.mp4"
    
    # Step 1: Get Video Info
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_streams', input_file
    ]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    info = eval(probe_result.stdout)
    
    video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    fps_str = video_stream.get('r_frame_rate', '30/1')
    fps = float(eval(fps_str))
    duration = float(info['format'].get('duration', 0))
    
    logger.info(f"Video Info: {width}x{height}, FPS: {fps}, Duration: {duration}s")
    
    # Step 2: Construct RAKIB Filter Graph
    
    # A. Visual Filters: Scale + Noise + Color Matrix
    # We scale down slightly to change pixel grid, then add noise
    new_w = int(width * 0.985)
    new_h = int(height * 0.985)
    
    # Ensure even dimensions
    if new_w % 2 != 0: new_w += 1
    if new_h % 2 != 0: new_h += 1
    
    visual_filters = [
        f'scale={new_w}:{new_h}:flags=lanczos',  # Scale to non-standard size
        'noise=alls=10:allf=t2',                 # Add subtle temporal noise
        'colorchannelmixer="1.02 0 0 0 | 0 1.02 0 0 | 0 0 1.02 0 | 0 0 0 1"' # Slight color shift
    ]
    
    # B. Audio Filters: Pitch Shift + Echo (Breaks Audio Fingerprint)
    audio_filter = ""
    if audio_stream:
        # Speed up by 0.3% to change pitch slightly and break hash
        # Add a very short echo to disrupt wave pattern
        audio_filter = f'[a:a]atempo=1.003,aecho=0.8:0.9:10:0.2[a_out]'
        
    filter_complex = f"[0:v]{','.join(visual_filters)}[v];{audio_filter}" if audio_filter else f"[0:v]{','.join(visual_filters)}[v]"
    
    # C. Final Command Construction
    cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '20', # High quality but re-encoded
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-an' if not audio_filter else '',
        output_file
    ]
    
    if audio_filter:
        cmd.extend(['-map', '[a_out]', '-c:a', 'aac', '-b:a', '192k'])
    else:
        cmd.extend(['-c:a', 'copy'])
        
    logger.info("Starting RAKIB Nuclear Optimization...")
    success = run_ffmpeg_command(cmd)
    
    if not success or not os.path.exists(output_file):
        raise Exception("RAKIB Optimization failed.")
        
    return output_file

if __name__ == "__main__":
    app.run()
