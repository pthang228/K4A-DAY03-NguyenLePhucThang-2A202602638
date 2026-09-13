"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        # Prompt ở các bước sau gồm yêu cầu ban đầu và Observation do app.py đính kèm.
        user_query = prompt.split("[OBSERVATION TỪ TOOL Ở CÁC LƯỢT TRƯỚC]", 1)[0].strip()
        prompt_lower = user_query.lower()
        has_observation = "[OBSERVATION TỪ TOOL Ở CÁC LƯỢT TRƯỚC]" in prompt
        student_match = re.search(r"\bSV\d+\b", user_query, flags=re.IGNORECASE)
        student_id = student_match.group(0).upper() if student_match else "SV2026001"
        is_multi_step = all(keyword in prompt_lower for keyword in ("tra cứu", "đặt lịch", "sau đó"))
        datetime_match = re.search(r"(?:lúc|vào)\s+(.+?)(?:[.?!]|$)", user_query, flags=re.IGNORECASE)
        datetime_str = datetime_match.group(1).strip() if datetime_match else "14:00 15/09/2026"
        datetime_str = re.sub(r"^(?:vào\s+)?lúc\s+", "", datetime_str, flags=re.IGNORECASE)
        advisor_match = re.search(r"với\s+(.+?)\s+(?:lúc|vào)\b", user_query, flags=re.IGNORECASE)
        requested_advisor = advisor_match.group(1).strip() if advisor_match else "PGS.TS Nguyễn Văn A"

        if has_observation:
            if '"status": "NOT_FOUND"' in prompt:
                return {
                    "type": "text",
                    "content": f"Không tìm thấy thông tin sinh viên {student_id}; vì vậy tôi không thể tiếp tục xử lý yêu cầu.",
                    "thought": "Observation cho thấy dữ liệu không tồn tại, cần trả lời chính xác và không bịa đặt."
                }
            if is_multi_step and '"advisor"' in prompt and '"data"' in prompt and '"booking_id"' not in prompt:
                advisor_match = re.search(r'"advisor"\s*:\s*"([^"]+)"', prompt)
                advisor_name = advisor_match.group(1) if advisor_match else "PGS.TS Nguyễn Văn A"
                return {
                    "type": "tool_call",
                    "tool_name": "schedule_appointment",
                    "arguments": {
                        "student_id": student_id,
                        "datetime_str": datetime_str,
                        "advisor_name": advisor_name
                    },
                    "thought": "Đã tra cứu được cố vấn. Tôi sẽ dùng đúng tên cố vấn từ Observation để đặt lịch."
                }
            if '"booking_id"' in prompt:
                return {
                    "type": "text",
                    "content": "Đặt lịch tư vấn thành công. Thông tin đặt lịch đã được xác nhận trong kết quả từ MCP Server.",
                    "thought": "Observation đã xác nhận đặt lịch thành công, nên có thể trả lời cuối cùng."
                }
            if '"data"' in prompt:
                name_match = re.search(r'"full_name"\s*:\s*"([^"]+)"', prompt)
                gpa_match = re.search(r'"gpa"\s*:\s*([0-9.]+)', prompt)
                advisor_match = re.search(r'"advisor"\s*:\s*"([^"]+)"', prompt)
                full_name = name_match.group(1) if name_match else "sinh viên yêu cầu"
                gpa = gpa_match.group(1) if gpa_match else "không có"
                advisor_name = advisor_match.group(1) if advisor_match else "không có"
                return {
                    "type": "text",
                    "content": f"Kết quả tra cứu {student_id}: {full_name}, GPA {gpa}, cố vấn học tập {advisor_name}.",
                    "thought": "Observation đã cung cấp đủ hồ sơ sinh viên, nên có thể trả lời cuối cùng."
                }
            return {
                "type": "text",
                "content": "Tôi đã nhận được kết quả tra cứu từ MCP Server và đã tổng hợp thông tin cho bạn.",
                "thought": "Observation đã cung cấp đủ dữ liệu, không cần gọi thêm Tool."
            }

        # TC04 phải tra cứu cố vấn trước; tuyệt đối không đặt lịch ở bước đầu.
        if is_multi_step:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": student_id},
                "thought": "Cần tra cứu hồ sơ để biết chính xác cố vấn học tập trước khi đặt lịch."
            }

        # Mô phỏng nhận diện intent gọi Tool cho bài kiểm thử offline.
        if "đặt lịch" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {"student_id": student_id, "datetime_str": datetime_str, "advisor_name": requested_advisor},
                "thought": f"Người dùng yêu cầu đặt lịch hẹn tư vấn cho sinh viên {student_id}. Tôi sẽ gọi tool schedule_appointment."
            }
        elif student_match or "tra cứu" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": student_id},
                "thought": f"Người dùng muốn tra cứu thông tin học vụ của sinh viên {student_id}. Tôi sẽ gọi tool academic_query."
            }
        else:
            return {
                "type": "text",
                "content": f"[Mock Agent Response]: Xin chào! Quy chế học vụ VinUni yêu cầu sinh viên tích lũy tối thiểu 120 tín chỉ và duy trì GPA trên 2.0 để tốt nghiệp.",
                "thought": "Câu hỏi chung về quy chế học vụ, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek Provider qua endpoint tương thích OpenAI, có hỗ trợ Tool Calling."""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "deepseek-v4-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            return "[DeepSeek Error]: Chưa cấu hình DEEPSEEK_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[DeepSeek Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            print("ℹ️ [DeepSeek Provider]: Chưa tìm thấy DEEPSEEK_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"DeepSeek quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            return {
                "type": "text",
                "content": msg.content or "",
                "thought": "DeepSeek phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
            }
        except Exception as e:
            print(f"⚠️ [DeepSeek API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        if key and key != "your_deepseek_api_key_here":
            return DeepSeekProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
