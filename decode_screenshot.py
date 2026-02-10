import json
import base64
import os

input_path = "/Users/nbiish/.gemini/antigravity/brain/ae39688a-df39-4ec5-8cd7-9dc2345637d7/.system_generated/steps/1042/output.txt"
output_path = "/Users/nbiish/.gemini/antigravity/brain/ae39688a-df39-4ec5-8cd7-9dc2345637d7/chamfered_bolt.png"

try:
    with open(input_path, 'r') as f:
        data = json.load(f)
        # Handle the structure returned by the tool (sometimes it's wrapped in result, sometimes effectively flat if read from file)
        # The file content shown in view_file was: {"success": true, "result": {"image_base64": "..."}}
        b64_str = data['result']['image_base64']
        
    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(b64_str))
    print(f"Success: {output_path}")
except Exception as e:
    print(f"Error: {e}")
