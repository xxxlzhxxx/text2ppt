"""
LLM Client Module - Handles communication with Seed 2.0 for PPT content generation.
Uses OpenAI-compatible API for Volcengine Ark.
"""
import json
from typing import List, Dict, Any
from openai import OpenAI
from config import ARK_API_KEY, ARK_BASE_URL, LLM_ENDPOINT


class LLMClient:
    """Client for interacting with Seed 2.0 language model via OpenAI-compatible API."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL
        )
        self.endpoint = LLM_ENDPOINT

    def generate_ppt_structure(self, user_input: str, num_slides: int = 5, language: str = "中文") -> List[Dict[str, Any]]:
        """
        Generate PPT structure from user input text.
        
        Args:
            user_input: The user's text input describing the PPT topic
            num_slides: Number of slides to generate (default: 5)
            language: Output language for titles and content (default: "中文")
            
        Returns:
            List of slide dictionaries with title, content, and image_prompt
        """
        # Determine language-specific instructions
        if language == "中文":
            lang_instruction = """
【重要】语言要求：
- title（标题）必须使用中文
- content（内容要点）必须使用中文
- image_prompt 保持英文（因为文生图模型用英文效果更好），但要在提示词中包含中文标题的英文翻译"""
        elif language == "English":
            lang_instruction = """
【IMPORTANT】Language Requirements:
- title must be in English
- content must be in English  
- image_prompt must be in English with the English title embedded"""
        elif language == "日本語":
            lang_instruction = """
【重要】言語要件：
- title（タイトル）は日本語で記述
- content（内容）は日本語で記述
- image_promptは英語で記述（タイトルの英訳を含める）"""
        else:
            lang_instruction = f"请使用{language}生成标题和内容。image_prompt保持英文。"

        system_prompt = f"""你是一个专业的PPT内容策划师和文生图提示词专家。
你的任务是将用户提供的文字内容转化为适合制作PPT的结构化数据。

{lang_instruction}

对于每一页PPT，你需要生成：
1. title: 简洁有力的标题（10字以内，使用指定语言）
2. content: 关键要点（使用指定语言，2-4个要点，用分号分隔）
3. image_prompt: 用于生成PPT背景图的英文提示词

【重要】关于 image_prompt 的要求：
- 必须是英文提示词
- ⚠️ 禁止包含任何文字、标题、字母、数字！只描述纯视觉背景
- 描述适合作为PPT背景的抽象图案、渐变、纹理
- 背景应该有足够的对比度，方便后续叠加深色或浅色文字
- 风格要专业、现代、有设计感
- 可以包含：渐变、几何图形、光效、科技元素、抽象图案等
- 不要包含：文字、人物、具体物体

输出格式必须是有效的JSON数组：
```json
[
    {{
        "slide_number": 1,
        "title": "标题文字（使用指定语言）",
        "content": "要点1；要点2；要点3",
        "image_prompt": "Abstract modern gradient background for presentation, blue and purple colors blending smoothly, subtle geometric shapes, soft lighting effects, professional corporate style, clean and minimal, 4K high resolution, no text no letters no words"
    }}
]
```

背景风格建议：
- 封面页：大气、有视觉冲击力的渐变或光效背景
- 内容页：简洁、不抢眼的浅色或深色背景，方便阅读
- 结尾页：温暖、专业的感谢页背景

注意事项：
1. 第一页应该是封面/标题页
2. 中间页面展示主要内容
3. 最后一页应该是总结或感谢页
4. 确保内容逻辑连贯，层次分明
5. 每个 image_prompt 末尾都要加上 "no text no letters no words" 以确保不生成文字"""

        user_prompt = f"""请根据以下内容，生成一个包含 {num_slides} 页的PPT结构：

{user_input}

请直接输出JSON数组，不要包含markdown代码块标记。"""

        completion = self.client.chat.completions.create(
            model=self.endpoint,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        # Log request ID for debugging (completion.id contains the request ID)
        request_id = completion.id
        print(f"[LLM] Request ID: {request_id}", flush=True)
        print(f"[LLM] Model: {completion.model}", flush=True)
        
        response_text = completion.choices[0].message.content.strip()
        
        # Parse JSON response
        # Remove markdown code block if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first and last lines (```json and ```)
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        try:
            slides = json.loads(response_text)
            return slides
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text}")
            # Return a default structure if parsing fails
            return self._create_default_structure(user_input, num_slides)
    
    def _create_default_structure(self, topic: str, num_slides: int) -> List[Dict[str, Any]]:
        """Create a default PPT structure if LLM parsing fails."""
        return [
            {
                "slide_number": i + 1,
                "title": f"Slide {i + 1}",
                "content": topic if i == 0 else f"Content for slide {i + 1}",
                "image_prompt": f"Professional PPT slide with title 'Slide {i + 1}' in large white font centered, modern blue gradient background, clean corporate design, business presentation style, high quality, 4K"
            }
            for i in range(num_slides)
        ]


def test_llm_client():
    """Test function for LLM client."""
    client = LLMClient()
    
    test_input = """
    人工智能在医疗健康领域的应用：
    - 疾病诊断辅助
    - 药物研发加速
    - 个性化治疗方案
    - 医疗影像分析
    - 健康监测与预警
    """
    
    slides = client.generate_ppt_structure(test_input)
    
    print("Generated PPT Structure:")
    for slide in slides:
        print(f"\n=== Slide {slide.get('slide_number', '?')} ===")
        print(f"Title: {slide.get('title', 'N/A')}")
        print(f"Content: {slide.get('content', 'N/A')}")
        print(f"Image Prompt: {slide.get('image_prompt', 'N/A')[:100]}...")
    
    return slides


if __name__ == "__main__":
    test_llm_client()
