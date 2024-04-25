import json
import flask
import io
import torch, auto_gptq
import numpy as np
import base64

from transformers import AutoModel, AutoTokenizer
from auto_gptq.modeling._base import BaseGPTQForCausalLM
from PIL import Image

from torchvision.transforms.functional import InterpolationMode
from torchvision import transforms

from flask import Flask, request

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

auto_gptq.modeling._base.SUPPORTED_MODELS = ["internlm"]
torch.set_grad_enabled(False)

class InternLMXComposer2QForCausalLM(BaseGPTQForCausalLM):
    layers_block_name = "model.layers"
    outside_layer_modules = [
        'vit', 'vision_proj', 'model.tok_embeddings', 'model.norm', 'output', 
    ]
    inside_layer_modules = [
        ["attention.wqkv.linear"],
        ["attention.wo.linear"],
        ["feed_forward.w1.linear", "feed_forward.w3.linear"],
        ["feed_forward.w2.linear"],
    ]

VISUAL_PROCESSOR = transforms.Compose([
    transforms.Resize((490, 490),
                    interpolation=InterpolationMode.BICUBIC),
    transforms.ToTensor(),
    transforms.Normalize((0.48145466, 0.4578275, 0.40821073),
                        (0.26862954, 0.26130258, 0.27577711)),
])

#Location of our LLM model. For registered models, sagemaker automatically downloads artifacts here
MODEL_PATH = f"/opt/ml/model"

application = app = Flask(__name__)

representation_model = InternLMXComposer2QForCausalLM.from_quantized(
    MODEL_PATH, trust_remote_code=True, device="cuda:0").eval()
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH, trust_remote_code=True)

def main():
    print("Model path:")
    print(MODEL_PATH)
    print("CUDA Available?:")
    print(torch.cuda.is_available())
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=8080, threaded=True)

def convert_image2tensor(base64_string):
    convert_image = Image.open(io.BytesIO(base64.b64decode(base64_string))).convert('RGB')
    tensor_image = VISUAL_PROCESSOR(convert_image).unsqueeze(0).to(device)
    return tensor_image

@app.route('/invocations', methods=["POST"])
def invoke():
    try:
        llm_request = request.get_json('inputs')
        resp_body = {}

        if llm_request is not None:
            
            # Setting some defaults for model parameters
            llm_request['parameters']['max_tokens']= 1024 if llm_request['parameters']['max_tokens'] is None else llm_request['parameters']['max_tokens']
            llm_request['parameters']['top_p']= 0.8 if llm_request['parameters']['top_p'] is None else llm_request['parameters']['top_p']
            llm_request['parameters']['temperature']= 1.0 if llm_request['parameters']['temperature'] is None else llm_request['parameters']['temperature']
            llm_request['parameters']['repeat_penalty']= 1.005 if llm_request['parameters']['repeat_penalty'] is None else llm_request['parameters']['repeat_penalty']

            image_tensor = convert_image2tensor(base64_string=llm_request['inputs'][0][0]['image'])

            with torch.cuda.amp.autocast():
                response, _ = representation_model.chat(
                    tokenizer=tokenizer,
                    query=llm_request['inputs'][0][0]['content'],
                    image=image_tensor,
                    max_new_tokens=llm_request['parameters']['max_tokens'],
                    temperature=llm_request['parameters']['temperature'],
                    top_p=llm_request['parameters']['top_p'],
                    repetition_penalty=llm_request['parameters']['repeat_penalty'],
                    history=[],
                    do_sample=False
                ) 
                return flask.Response(json.dumps(response), mimetype='application/json')
        else:
            
            resp_body['error'] = "No request or missing request body required to process the request"
            return flask.Response(json.dumps(resp_body), mimetype='application/json')

    except Exception as e:
        print("Failed to process request using the LLM:")
        print(str(e))
        resp_body['error'] = f"Failed to process request using the LLM: {str(e)}"
        return flask.Response(json.dumps(resp_body), mimetype='application/json')


@app.route("/ping", methods=["GET"])
def ping():
    """Determine if the container is working and healthy"""
    health = representation_model is not None
    status = 200 if health else 404

    if status == 200:
        return flask.Response(response="True", status=status, mimetype="application/json")
    else:
        return flask.Response(response="False", status=status, mimetype="application/json")

if __name__ == '__main__':
    main()
