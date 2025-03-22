from flask import Flask, request, jsonify, render_template
from io import BytesIO
import base64

def DalleWebAPI(client, host: str = "0.0.0.0", port: int = 5754, debug: bool = False):
    """
    Start Dalle Generator API server with all endpoints.
    
    Parameters:
    - client (Client): Dalle Generator instance
    - host (str): Host to run the server on
    - port (int): Port to run the server on
    - debug (bool): Enable Flask debug mode
    """
    try:
        app = Flask(__name__)

        def __data_url_processor(pil_image) -> str:
            """Convert PIL Image to base64 data URL."""
            try:
                img_io = BytesIO()
                pil_image.save(img_io, format='WEBP', quality=90)
                img_io.seek(0)
                img_base64 = base64.b64encode(img_io.getvalue()).decode()
                
                client.logger.info(f"Created data URL from PIL object!")
                return f"data:image/png;base64,{img_base64}"
            
            except Exception as e:
                client.logger.error(f"Error in data_url_processor: {e}")
                return None

        @app.route('/', methods=['GET'])
        def api_index():
            """Render the API documentation page"""
            return render_template('index.py')
            
        @app.route('/v1/api/image/generate', methods=['POST'])
        def image_generate_api():
            """
            Handle image generation requests via form data.
            
            Form Parameters:
            - prompt (str, required): User's positive prompt
            """
            try:
                data = {
                    'prompt': request.form.get('prompt'),
                }

                if not data['prompt']:
                    raise Exception("Missing prompt")

                result = client.image_generate(**data)
                if not result:
                    raise Exception("Generation failed")

                # Convert result to list if it's a single image
                images = result if isinstance(result, list) else [result]
                
                # Process all images, collecting successful conversions
                data_urls = []
                for image in images:
                    data_url = __data_url_processor(image)
                    if data_url:  # Only add successfully processed images
                        data_urls.append(data_url)

                return jsonify({"success": True, "results": data_urls})

            except Exception as e:
                client.logger.error(f"Error in image_generate_api: {e}")
                return jsonify({"success": False, "error": str(e)}), 400

        client.logger.info(f"Starting API server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    
    except Exception as e:
        client.logger.error(f"{str(e)}")
        raise