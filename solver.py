import requests, re, json, base64, subprocess, sys


def node_eval(js, timeout=10):
    proc = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"Node.js error:\n{proc.stderr}")
    return proc.stdout.strip()


def cjson(obj):
    return json.dumps(obj, separators=(',', ':'))


def solve(base_url="https://vibecheck.petar.petrushev.u.is-my.space", form_path="/demo/", name="Alex Rivera"):
    api_eh = f"{base_url}/api/eh/"
    referer = f"{base_url}{form_path}"

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

    genjs = s.get(f"{base_url}/api/genjs/", headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Sec-Fetch-Dest": "script", "Sec-Fetch-Mode": "no-cors", "Sec-Fetch-Site": "same-origin", "Referer": referer}).text

    tok_m = re.search(r"value='([^']+)'", genjs)
    if not tok_m:
        raise RuntimeError(" error token")
    initial_token = tok_m.group(1)
    print(f"token: {initial_token[:50]}...")

    extract_js = (
        "const src = " + json.dumps(genjs) + ";\n"
        "const idx = src.indexOf('async function smt');\n"
        "const sPart = src.substring(0, idx);\n"
        "const smtPart = src.substring(idx);\n"
        "function getE(code) {\n"
        "  const m = code.match(/\"e\":\\s*([\\s\\S]+?)\\s*,\\s*(?:\\r?\\n\\s*)?\"ed\"/);\n"
        "  if (!m) throw new Error('no e match');\n"
        "  return eval(m[1]);\n"
        "}\n"
        "process.stdout.write(JSON.stringify({e1: getE(sPart), e2: getE(smtPart)}));\n"
    )
    e_vals = json.loads(node_eval(extract_js))
    first_e, smt_e = e_vals["e1"], e_vals["e2"]
    print(f"      e1={first_e}, e2={smt_e}")

    ed1 = base64.b64encode(cjson({"mft": initial_token, "a": "atavoart"}).encode()).decode()
    r1 = s.post(api_eh, data=cjson({"e": first_e, "ed": ed1}), headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Origin": base_url, "Referer": referer}).json()
    if not r1.get("ag") or not r1.get("se"):
        raise RuntimeError(f"rejected: {r1}")
    cte = r1["cte"]
    print("      OK")

    new_tok_m = re.search(r"\.value='([^']+)'", cte) or re.search(r'\.value="([^"]+)"', cte)
    if not new_tok_m:
        raise RuntimeError("cant find the cte solver is probably fucking patched")
    new_token = new_tok_m.group(1)

    ts_js = (
        "const cte = " + json.dumps(cte) + ";\n"
        "const m = cte.match(/smt\\((['\"])([\\s\\S]*?)\\1\\)/);\n"
        "if (!m) { process.stderr.write('no smt match'); process.exit(1); }\n"
        "const ts = eval(m[1] + m[2] + m[1]);\n"
        "process.stdout.write(ts);\n"
    )
    ts_value = node_eval(ts_js)
    print(f"new token: {new_token[:50]}...")
    print(f"ts: {ts_value[:50]}...")

    ed2 = base64.b64encode(cjson({"mft": new_token, "a": "gmttiweasb"}).encode()).decode()
    r2 = s.post(api_eh, data=cjson({"e": smt_e, "ed": ed2}), headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Origin": base_url, "Referer": referer}).json()
    if not r2.get("ag"):
        raise RuntimeError(f"rejected: {r2}")
    ett = r2.get("ett", "")
    print("      OK")

    sandbox_js = (
        "const btoa = (s) => Buffer.from(s).toString('base64');\n"
        "const ts = " + json.dumps(ts_value) + ";\n"
        "const currentToken = " + json.dumps(new_token) + ";\n"
        "const navigator = { userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' };\n"
        "const window = { nmd: { getElementsByTagName: () => [{ value: currentToken }] } };\n"
        "let captured = null;\n"
        "async function postData(url, data) { captured = data; return { ag: true, passed: true }; }\n"
        "try { eval(" + json.dumps(ett) + "); } catch(e) { process.stderr.write('eval error: ' + e.stack); process.exit(1); }\n"
        "setTimeout(() => {\n"
        "  if (captured) { process.stdout.write(JSON.stringify(captured)); }\n"
        "  else { process.stderr.write('postData was never called'); process.exit(1); }\n"
        "}, 300);\n"
    )
    final_payload = json.loads(node_eval(sandbox_js, timeout=15))

    r3 = s.post(api_eh, data=cjson(final_payload), headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Origin": base_url, "Referer": referer}).json()
    if not r3.get("passed"):
        raise RuntimeError(f"failed: {r3}")
    print("Solved")

    form_resp = s.post(f"{base_url}{form_path}submit/", data={"name": name, "vibecheck-result-token": new_token}, headers={"Referer": referer, "Origin": base_url})

    if "Captcha verified" in form_resp.text:
        print(f"\nsubmitted as '{name}'")
    elif "Submission Received" in form_resp.text:
        print(f"\nsubmitted as '{name}'")
    else:
        print(f"\n[-] Submitted (HTTP {form_resp.status_code})")
        status_m = re.search(r"<h1>\s*(.*?)\s*</h1>", form_resp.text)
        if status_m:
            print(f"    Server: {status_m.group(1)}")
    return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://vibecheck.petar.petrushev.u.is-my.space"
    form = sys.argv[2] if len(sys.argv) > 2 else "/demo/"
    who = sys.argv[3] if len(sys.argv) > 3 else "a"
    solve(url, form, who)
