# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Lê Phúc Thắng  
> **Mã Sinh Viên / Mã Học viên:** 2A202602638  
> **Chủ đề Lựa chọn:** Trợ lý Học vụ & Tra cứu Lịch thi VinUni  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Với yêu cầu đặt lịch cùng đúng cố vấn, Agent phải tra cứu hồ sơ sinh viên, lấy tên cố vấn từ kết quả rồi mới đặt lịch. |
| **2. Tool Interaction** | 5 / 5 | Hệ thống cần gọi MCP Server để tra cứu dữ liệu học vụ và thực thi hành động đặt lịch tư vấn. |
| **3. Dynamic Decision** | 4 / 5 | Tool ở bước hai phụ thuộc vào Observation của bước một, cụ thể là tên cố vấn trả về từ `academic_query`. |
| **4. Long Horizon Goal** | 3 / 5 | Agent duy trì mục tiêu hỗ trợ sinh viên hoàn tất tra cứu hoặc đặt lịch qua nhiều bước trong cùng một phiên xử lý. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Tổng điểm lớn hơn 12/20, nên bài toán phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026001, sau đó đặt lịch tư vấn với đúng cố vấn đó vào lúc 10:30 ngày 13/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "advisor": "PGS.TS Nguyễn Văn A"
      }
    },
    "latency_ms": 1019.95
  },
  {
    "step": 2,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026001, sau đó đặt lịch tư vấn với đúng cố vấn đó vào lúc 10:30 ngày 13/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "schedule_appointment",
    "arguments": {
      "student_id": "SV2026001",
      "datetime_str": "10:30 13/09/2026",
      "advisor_name": "PGS.TS Nguyễn Văn A"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "BK-SV2026001-99",
      "advisor": "PGS.TS Nguyễn Văn A"
    },
    "latency_ms": 1479.88
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (DeepSeek).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
