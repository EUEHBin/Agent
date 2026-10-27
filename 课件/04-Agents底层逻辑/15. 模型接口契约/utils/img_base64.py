import base64


def to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_image


def to_dataurl(image_path: str) -> str:
    # base64编码
    b64_data = to_base64(image_path)

    # 简单判断图片类型，可自行扩展
    lower_path = image_path.lower()
    if lower_path.endswith(".png"):
        mime = "image/png"
    elif lower_path.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    elif lower_path.endswith(".gif"):
        mime = "image/gif"
    elif lower_path.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "image/octet-stream"

    data_url = f"data:{mime};base64,{b64_data}"
    return data_url
