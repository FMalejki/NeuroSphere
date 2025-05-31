"""
Handlers for files uploaded to the OpenAI API.
"""
import base64
import io
import zipfile
from typing import List, Any, Dict


def handle_image(f: Dict[str, Any], content: List[Dict[str, Any]]) -> None:
    """
    Handles image files by appending their data to the content of the request
    """
    try:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{f['info']['type']};base64,{f['data']}"}
        })
        print("Image processed successfully")
    except Exception as e:
        print(f"Error handling image: {str(e)}")


def handle_text(f: Dict[str, Any], content: List[Dict[str, Any]]) -> None:
    """
    Handles text files by decoding their data and appending it to the content of the request
    """
    try:
        file_bytes = base64.b64decode(f['data'])
        try:
            file_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            file_text = file_bytes.decode("latin-1")
        
        content[0]["text"] += f"\n\nAttached file `{f['info']['name']}` content:\n{file_text[:2000]}"
        print("Text file processed successfully")
    except Exception as e:
        print(f"Error handling text file: {str(e)}")


def handle_zip(f: Dict[str, Any], content: List[Dict[str, Any]]) -> None:
    """
    Handles ZIP files by extracting text from contained files and appending
    it to the content of the request
    """
    try:
        file_bytes = base64.b64decode(f['data'])
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            zip_text = ""
            for zip_info in z.infolist():
                if zip_info.file_size > 0 and not zip_info.is_dir():
                    if zip_info.filename.endswith(('.txt', '.md', '.py', '.json', '.csv')):
                        with z.open(zip_info) as file:
                            try:
                                file_content = file.read().decode("utf-8")
                            except UnicodeDecodeError:
                                file_content = file.read().decode("latin-1")
                            zip_text += f"\n\nFile `{zip_info.filename}`:\n{file_content[:1000]}"
            if zip_text:
                content[0]["text"] += f"\n\nExtracted ZIP `{f['info']['name']}` contents:{zip_text}"
            else:
                content[0]["text"] += f"\n\nZIP file `{f['info']['name']}` contains no readable text files."
        print("ZIP file processed successfully")
    except Exception as e:
        print(f"Error handling ZIP file: {str(e)}")


def handle_default(f: Dict[str, Any], content: List[Dict[str, Any]]) -> None:
    """
    Handle unsupported file types by appending a message to the content of the request
    """
    try:
        content[0]["text"] += f"\n\nFile attached: {f['info']['name']} ({f['info']['type']}, {f['info']['size']} bytes)"
        print("Default handler used for file")
    except Exception as e:
        print(f"Error in default handler: {str(e)}")