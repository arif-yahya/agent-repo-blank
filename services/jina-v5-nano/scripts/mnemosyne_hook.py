#!/usr/bin/env python3
import sys
import json
import subprocess
import os

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        print("{}")
        return

    transcript_path = input_data.get("transcriptPath")
    user_query = ""

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-20:]):
                    try:
                        record = json.loads(line)
                        if record.get("type") == "USER_INPUT" and record.get("content"):
                            user_query = record["content"].strip()
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    if not user_query or len(user_query) < 3 or user_query.startswith("/"):
        print("{}")
        return

    try:
        # Run local mnemosyne recall
        proc = subprocess.run(
            ["/home/ubuntu/.local/bin/mnemosyne", "recall", user_query, "2"],
            capture_output=True,
            text=True,
            timeout=2
        )
        output = proc.stdout.strip()
        if output and "Content:" in output:
            # Extract content lines
            memories = []
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Content:"):
                    memories.append(line.replace("Content:", "•").strip())
            
            if memories:
                msg = "🧠 [Mnemosyne Proactive Context]\n" + "\n".join(memories[:2])
                response = {
                    "injectSteps": [
                        {
                            "ephemeralMessage": msg
                        }
                    ]
                }
                print(json.dumps(response))
                return
    except Exception:
        pass

    print("{}")

if __name__ == "__main__":
    main()
