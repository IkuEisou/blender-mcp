from flask import Flask, request, jsonify
import sys
import os

# Ensure client_mcp.py is in the Python path or same directory
sys.path.append(os.path.dirname(__file__))
from client_mcp import BlenderMCPClient

app = Flask(__name__)
client = BlenderMCPClient()

@app.route('/get_scene_info', methods=['GET'])
def get_scene_info_api():
    response = client.get_scene_info()
    return jsonify(response)

@app.route('/get_object_info', methods=['POST'])
def get_object_info_api():
    data = request.get_json()
    object_name = data.get('object_name')
    if not object_name:
        return jsonify({"status": "error", "message": "object_name is required"}), 400
    response = client.get_object_info(object_name)
    return jsonify(response)

@app.route('/get_viewport_screenshot', methods=['POST'])
def get_viewport_screenshot_api():
    data = request.get_json()
    max_size = data.get('max_size', 800)
    response = client.get_viewport_screenshot(max_size=max_size)
    return jsonify(response)

@app.route('/execute_blender_code', methods=['POST'])
def execute_blender_code_api():
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({"status": "error", "message": "code is required"}), 400
    response = client.execute_blender_code(code)
    return jsonify(response)

@app.route('/get_polyhaven_categories', methods=['POST'])
def get_polyhaven_categories_api():
    data = request.get_json()
    asset_type = data.get('asset_type')
    if not asset_type:
        return jsonify({"status": "error", "message": "asset_type is required"}), 400
    response = client.get_polyhaven_categories(asset_type)
    return jsonify(response)

@app.route('/search_polyhaven_assets', methods=['POST'])
def search_polyhaven_assets_api():
    data = request.get_json()
    asset_type = data.get('asset_type')
    categories = data.get('categories')
    response = client.search_polyhaven_assets(asset_type=asset_type, categories=categories)
    return jsonify(response)

@app.route('/download_polyhaven_asset', methods=['POST'])
def download_polyhaven_asset_api():
    data = request.get_json()
    asset_id = data.get('asset_id')
    asset_type = data.get('asset_type')
    resolution = data.get('resolution')
    file_format = data.get('file_format')
    if not all([asset_id, asset_type]):
        return jsonify({"status": "error", "message": "asset_id and asset_type are required"}), 400
    response = client.download_polyhaven_asset(asset_id, asset_type, resolution, file_format)
    return jsonify(response)

@app.route('/set_texture', methods=['POST'])
def set_texture_api():
    data = request.get_json()
    object_name = data.get('object_name')
    texture_id = data.get('texture_id')
    if not all([object_name, texture_id]):
        return jsonify({"status": "error", "message": "object_name and texture_id are required"}), 400
    response = client.set_texture(object_name, texture_id)
    return jsonify(response)

@app.route('/get_polyhaven_status', methods=['GET'])
def get_polyhaven_status_api():
    response = client.get_polyhaven_status()
    return jsonify(response)

@app.route('/get_hyper3d_status', methods=['GET'])
def get_hyper3d_status_api():
    response = client.get_hyper3d_status()
    return jsonify(response)

@app.route('/generate_hyper3d_model_via_text', methods=['POST'])
def generate_hyper3d_model_via_text_api():
    data = request.get_json()
    text_prompt = data.get('text_prompt')
    bbox_condition = data.get('bbox_condition')
    if not text_prompt:
        return jsonify({"status": "error", "message": "text_prompt is required"}), 400
    response = client.generate_hyper3d_model_via_text(text_prompt, bbox_condition)
    return jsonify(response)

@app.route('/generate_hyper3d_model_via_images', methods=['POST'])
def generate_hyper3d_model_via_images_api():
    data = request.get_json()
    input_image_paths = data.get('input_image_paths')
    input_image_urls = data.get('input_image_urls')
    bbox_condition = data.get('bbox_condition')

    if not input_image_paths and not input_image_urls:
        return jsonify({"status": "error", "message": "Either input_image_paths or input_image_urls is required"}), 400

    response = client.generate_hyper3d_model_via_images(input_image_paths=input_image_paths, input_image_urls=input_image_urls, bbox_condition=bbox_condition)
    return jsonify(response)

@app.route('/poll_rodin_job_status', methods=['POST'])
def poll_rodin_job_status_api():
    data = request.get_json()
    request_id = data.get('request_id')
    subscription_key = data.get('subscription_key')
    if not request_id and not subscription_key:
        return jsonify({"status": "error", "message": "Either request_id or subscription_key is required"}), 400
    response = client.poll_rodin_job_status(request_id=request_id, subscription_key=subscription_key)
    return jsonify(response)

@app.route('/import_generated_asset', methods=['POST'])
def import_generated_asset_api():
    data = request.get_json()
    name = data.get('name')
    request_id = data.get('request_id')
    task_uuid = data.get('task_uuid')
    if not name:
        return jsonify({"status": "error", "message": "name is required"}), 400
    if not request_id and not task_uuid:
        return jsonify({"status": "error", "message": "Either request_id or task_uuid is required"}), 400

    response = client.import_generated_asset(name=name, request_id=request_id, task_uuid=task_uuid)
    return jsonify(response)

@app.route('/get_sketchfab_status', methods=['GET'])
def get_sketchfab_status_api():
    response = client.get_sketchfab_status()
    return jsonify(response)

@app.route('/search_sketchfab_models', methods=['POST'])
def search_sketchfab_models_api():
    data = request.get_json()
    query = data.get('query')
    categories = data.get('categories')
    count = data.get('count')
    downloadable = data.get('downloadable')
    if not query:
        return jsonify({"status": "error", "message": "query is required"}), 400
    response = client.search_sketchfab_models(query=query, categories=categories, count=count, downloadable=downloadable)
    return jsonify(response)

@app.route('/download_sketchfab_model', methods=['POST'])
def download_sketchfab_model_api():
    data = request.get_json()
    uid = data.get('uid')
    if not uid:
        return jsonify({"status": "error", "message": "uid is required"}), 400
    response = client.download_sketchfab_model(uid)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True) 