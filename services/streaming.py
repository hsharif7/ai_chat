from database.save import save

def stream(sans, uid, logged_in):
    ans = ""
    try:
        for s in sans:
            chunk = s.choices[0].delta.content

            if chunk:
                ans += chunk
                yield chunk
    finally:
        if ans:
            if logged_in:
                save("assistant", ans, uid)
