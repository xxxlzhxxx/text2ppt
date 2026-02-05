"""
Text2PPT Web API Server
Flask-based API for the Text2PPT application.
"""
import os
import json
import uuid
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

from llm_client import LLMClient
from image_generator import ImageGenerator
from ppt_generator import PPTGenerator
from config import OUTPUT_DIR

app = Flask(__name__, static_folder='static')
CORS(app)

# Store task status
tasks = {}


def generate_ppt_task(task_id: str, text: str, num_slides: int, language: str, style: str):
    """Background task to generate PPT."""
    try:
        print(f"\n{'='*60}", flush=True)
        print(f"[Task {task_id}] 开始生成 PPT", flush=True)
        print(f"[Task {task_id}] 页数: {num_slides}, 语言: {language}, 风格: {style}", flush=True)
        print(f"{'='*60}", flush=True)
        
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = '正在分析内容结构...'
        
        # Step 1: Generate structure with language parameter
        print(f"\n[Step 1] 调用 LLM 生成内容结构...", flush=True)
        llm = LLMClient()
        slides = llm.generate_ppt_structure(text, num_slides, language)
        print(f"[Step 1] 成功生成 {len(slides)} 页结构", flush=True)
        tasks[task_id]['progress'] = f'已生成 {len(slides)} 页内容结构'
        tasks[task_id]['slides_count'] = len(slides)
        
        # Step 2: Generate images
        print(f"\n[Step 2] 开始生成图片...", flush=True)
        tasks[task_id]['progress'] = '正在生成图片...'
        gen = ImageGenerator()
        
        image_paths = []
        for i, slide in enumerate(slides):
            print(f"\n[Step 2] 正在生成第 {i+1}/{len(slides)} 页图片...", flush=True)
            tasks[task_id]['progress'] = f'正在生成第 {i+1}/{len(slides)} 页图片...'
            slide_num = slide.get('slide_number', i + 1)
            prompt = slide.get('image_prompt', '')
            
            if prompt:
                # Add style to image prompt
                if style:
                    prompt = f"{prompt}, {style} design style"
                    
                output_filename = f"{task_id}_slide_{slide_num:02d}"
                image_path = gen.generate_image(prompt, output_filename)
                if image_path:
                    image_paths.append(image_path)
                    slide['image_path'] = image_path
                    print(f"[Step 2] 第 {i+1} 页图片生成成功", flush=True)
        
        # Step 3: Create PPT
        print(f"\n[Step 3] 正在创建 PPT 文件...", flush=True)
        tasks[task_id]['progress'] = '正在创建 PPT 文件...'
        ppt = PPTGenerator()
        output_filename = f"presentation_{task_id}"
        ppt_path = ppt.create_ppt_from_images(image_paths, output_filename, slides)
        
        # Complete
        print(f"\n{'='*60}", flush=True)
        print(f"[Task {task_id}] PPT 生成完成!", flush=True)
        print(f"[Task {task_id}] 输出文件: {ppt_path}", flush=True)
        print(f"{'='*60}\n", flush=True)
        
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = '完成！'
        tasks[task_id]['result'] = {
            'ppt_path': ppt_path,
            'ppt_filename': f"{output_filename}.pptx",
            'slides_count': len(slides),
            'slides': [{'title': s.get('title', ''), 'content': s.get('content', '')} for s in slides]
        }
        
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)


@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')


@app.route('/api/generate', methods=['POST'])
def generate():
    """Start PPT generation task."""
    data = request.json
    text = data.get('text', '')
    num_slides = data.get('num_slides', 5)
    language = data.get('language', '中文')
    style = data.get('style', '商务')
    
    if not text.strip():
        return jsonify({'error': 'Text content is required'}), 400
    
    # Create task
    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        'id': task_id,
        'status': 'pending',
        'progress': 'Starting...',
        'created_at': datetime.now().isoformat(),
        'params': {
            'text': text[:100] + '...' if len(text) > 100 else text,
            'num_slides': num_slides,
            'language': language,
            'style': style
        }
    }
    
    # Start background task
    thread = threading.Thread(
        target=generate_ppt_task,
        args=(task_id, text, num_slides, language, style)
    )
    thread.start()
    
    return jsonify({'task_id': task_id, 'status': 'pending'})


@app.route('/api/status/<task_id>')
def get_status(task_id):
    """Get task status."""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(tasks[task_id])


@app.route('/api/download/<task_id>')
def download(task_id):
    """Download generated PPT."""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({'error': 'PPT not ready yet'}), 400
    
    ppt_path = task['result']['ppt_path']
    if not os.path.exists(ppt_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        ppt_path,
        as_attachment=True,
        download_name=task['result']['ppt_filename']
    )


@app.route('/api/tasks')
def list_tasks():
    """List all tasks."""
    return jsonify(list(tasks.values()))


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
