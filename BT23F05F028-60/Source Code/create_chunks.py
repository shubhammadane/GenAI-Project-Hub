# Speech to Text
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import whisper
import json
model = whisper.load_model("medium")
audios=os.listdir("audios/")
for audio in audios:
    number=audio.split("_")[0]
    name=audio.split("_")[1].split(".")[0]
    result = model.transcribe(audio=f"audios\\{audio}",language="hi",task="translate",word_timestamps=False)
    # print(number,name)
    chunks = []
    for segment in result["segments"]:
        chunks.append({
            "number": number,
            "title": name,
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        })
    chunks_with_metadata = {
        "chunks": chunks,
        "text": result["text"]
    }
    with open(f"jsons/{audio}.json", "w", encoding="utf-8") as f:
        json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=4)
    