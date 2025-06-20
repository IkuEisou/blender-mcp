import socket
import json
import io
import base64

class BlenderMCPClient:
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.socket = None

    def _connect(self):
        if self.socket:
            self._disconnect()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def _disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def _send_command(self, command_type, params=None):
        try:
            self._connect()
            command = {"type": command_type, "params": params or {}}
            self.socket.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive response
            buffer = b''
            while True:
                data = self.socket.recv(8192)
                if not data:
                    break
                buffer += data
                try:
                    response = json.loads(buffer.decode('utf-8'))
                    return response
                except json.JSONDecodeError:
                    # Incomplete data, wait for more
                    continue
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self._disconnect()

    # Client methods for each Blender MCP command
    def get_scene_info(self):
        return self._send_command("get_scene_info")

    def get_object_info(self, object_name):
        return self._send_command("get_object_info", {"name": object_name})
    
    def get_viewport_screenshot(self, max_size=800):
        # We need to save the screenshot to a temporary file on the Blender side
        # and then transmit it. This example simplifies by just requesting.
        # A more robust solution would involve Blender saving to a known path
        # and then the client requesting that path's content.
        # For Dify, it's about getting the *status* of screenshot.
        return self._send_command("get_viewport_screenshot", {"max_size": max_size})

    def execute_blender_code(self, code):
        return self._send_command("execute_code", {"code": code})
    
    def get_polyhaven_categories(self, asset_type):
        return self._send_command("get_polyhaven_categories", {"asset_type": asset_type})

    def search_polyhaven_assets(self, asset_type=None, categories=None):
        params = {}
        if asset_type:
            params["asset_type"] = asset_type
        if categories:
            params["categories"] = categories
        return self._send_command("search_polyhaven_assets", params)

    def download_polyhaven_asset(self, asset_id, asset_type, resolution=None, file_format=None):
        params = {
            "asset_id": asset_id,
            "asset_type": asset_type,
        }
        if resolution:
            params["resolution"] = resolution
        if file_format:
            params["file_format"] = file_format
        return self._send_command("download_polyhaven_asset", params)
    
    def set_texture(self, object_name, texture_id):
        return self._send_command("set_texture", {"object_name": object_name, "texture_id": texture_id})

    def get_polyhaven_status(self):
        return self._send_command("get_polyhaven_status")

    def get_hyper3d_status(self):
        return self._send_command("get_hyper3d_status")

    def generate_hyper3d_model_via_text(self, text_prompt, bbox_condition=None):
        params = {"text_prompt": text_prompt}
        if bbox_condition:
            params["bbox_condition"] = bbox_condition
        return self._send_command("create_rodin_job", params)

    def generate_hyper3d_model_via_images(self, input_image_paths=None, input_image_urls=None, bbox_condition=None):
        params = {}
        if input_image_paths:
            # For MAIN_SITE mode, images are sent as a list of (suffix, content)
            # This needs to be handled carefully. For now, assume client sends image content directly.
            # Convert local paths to base64 encoded strings
            converted_images = []
            for img_path in input_image_paths:
                with open(img_path, "rb") as f:
                    # Get file extension from path
                    file_ext = img_path.split('.')[-1]
                    converted_images.append((f".{file_ext}", base64.b64encode(f.read()).decode('utf-8')))
            params["images"] = converted_images
        elif input_image_urls:
            params["images"] = input_image_urls
        if bbox_condition:
            params["bbox_condition"] = bbox_condition
        return self._send_command("create_rodin_job", params)

    def poll_rodin_job_status(self, request_id=None, subscription_key=None):
        params = {}
        if request_id:
            params["request_id"] = request_id
        if subscription_key:
            params["subscription_key"] = subscription_key
        return self._send_command("poll_rodin_job_status", params)

    def import_generated_asset(self, name, request_id=None, task_uuid=None):
        params = {"name": name}
        if request_id:
            params["request_id"] = request_id
        if task_uuid:
            params["task_uuid"] = task_uuid
        return self._send_command("import_generated_asset", params)

    def get_sketchfab_status(self):
        return self._send_command("get_sketchfab_status")

    def search_sketchfab_models(self, query, categories=None, count=None, downloadable=None):
        params = {"query": query}
        if categories:
            params["categories"] = categories
        if count:
            params["count"] = count
        if downloadable is not None:
            params["downloadable"] = downloadable
        return self._send_command("search_sketchfab_models", params)

    def download_sketchfab_model(self, uid):
        return self._send_command("download_sketchfab_model", {"uid": uid})

if __name__ == "__main__":
    client = BlenderMCPClient()
    
    # Example Usage:
    # Get scene info
    # print("Getting scene info...")
    # response = client.get_scene_info()
    # print(json.dumps(response, indent=2))

    # Example: Execute Blender code
    # print("\nExecuting Blender code (creating a new cube)...")
    # response = client.execute_blender_code("bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))")
    # print(json.dumps(response, indent=2))
    
    # Example: Get object info for the newly created cube (assuming it's named 'Cube')
    # print("\nGetting object info for 'Cube'...")
    # response = client.get_object_info("Cube")
    # print(json.dumps(response, indent=2))
    
    # Example: Search Polyhaven textures
    # print("\nSearching for Polyhaven textures 'wood'...")
    # response = client.search_polyhaven_assets(asset_type="textures", categories="wood")
    # print(json.dumps(response, indent=2))

    # Example: Check Polyhaven status
    # print("\nChecking Polyhaven status...")
    # response = client.get_polyhaven_status()
    # print(json.dumps(response, indent=2))
    
    # Example: Check Hyper3D status
    # print("\nChecking Hyper3D status...")
    # response = client.get_hyper3d_status()
    # print(json.dumps(response, indent=2))

    # Example: Search Sketchfab models
    # print("\nSearching Sketchfab models 'chair'...")
    # response = client.search_sketchfab_models(query="chair", count=5)
    # print(json.dumps(response, indent=2)) 