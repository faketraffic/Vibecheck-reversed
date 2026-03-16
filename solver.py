import requests, re, json, base64, subprocess, sys, time
from colorama import init, Fore, Style

init()


def node_eval(js, timeout=10):
    proc = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def cjson(obj):
    return json.dumps(obj, separators=(',', ':'))


def solve(base_url="https://vibecheck.petar.petrushev.u.is-my.space", form_path="/demo/", name=None, retries=5):
    api_eh = f"{base_url}/api/eh/"
    referer = f"{base_url}{form_path}"

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

    for attempt in range(1, retries + 1):
        try:
            start = time.time()

            genjs = s.get(f"{base_url}/api/genjs/", headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Sec-Fetch-Dest": "script", "Sec-Fetch-Mode": "no-cors", "Sec-Fetch-Site": "same-origin", "Referer": referer}).text

            tok_m = re.search(r"value='([^']+)'", genjs)
            if not tok_m:
                raise RuntimeError("token not found in genjs")
            initial_token = tok_m.group(1)

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

            ed1 = base64.b64encode(cjson({"mft": initial_token, "a": "atavoart"}).encode()).decode()
            r1 = s.post(api_eh, data=cjson({"e": first_e, "ed": ed1}), headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Origin": base_url, "Referer": referer}).json()
            if not r1.get("ag") or not r1.get("se"):
                raise RuntimeError(f"step1 rejected: {r1}")
            cte = r1["cte"]

            unwrap_js = (
                "let final = '';\n"
                "const _eval = eval;\n"
                "eval = function(x) {\n"
                "  if (typeof x === 'string' && x.includes('eval(')) { return _eval('eval = function(y){final=y}; ' + x); }\n"
                "  final = x;\n"
                "};\n"
                + cte + "\n"
                "process.stdout.write(final);\n"
            )
            unwrapped = node_eval(unwrap_js)

            new_tok_m = re.search(r"\.value='([^']+)'", unwrapped) or re.search(r'\.value="([^"]+)"', unwrapped)
            if not new_tok_m:
                new_tok_m = re.search(r"\.value='([^']+)'", cte) or re.search(r'\.value="([^"]+)"', cte)
            if not new_tok_m:
                raise RuntimeError("cte token not found (patched?)")
            new_token = new_tok_m.group(1)

            smt_m = re.search(r"smt\('([^']+)'\)", unwrapped) or re.search(r'smt\("([^"]+)"\)', unwrapped)
            if not smt_m:
                smt_m = re.search(r"smt\('([^']+)'\)", cte) or re.search(r'smt\("([^"]+)"\)', cte)
            if not smt_m:
                raise RuntimeError("smt call not found in cte")
            ts_value = smt_m.group(1)

            ed2 = base64.b64encode(cjson({"mft": new_token, "a": "gmttiweasb"}).encode()).decode()
            r2 = s.post(api_eh, data=cjson({"e": smt_e, "ed": ed2}), headers={"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9", "Content-Type": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Origin": base_url, "Referer": referer}).json()
            if not r2.get("ag"):
                raise RuntimeError(f"step2 rejected: {r2}")
            ett = r2.get("ett", "")

            sandbox_js = (
                "const { JSDOM } = require('jsdom');\n"
                "const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', { url: " + json.dumps(referer) + " });\n"
                "const window = dom.window;\n"
                "const document = window.document;\n"
                "const location = window.location;\n"
                "const history = window.history;\n"
                "const btoa = (s) => Buffer.from(s).toString('base64');\n"
                "const ts = " + json.dumps(ts_value) + ";\n"
                "const currentToken = " + json.dumps(new_token) + ";\n"
                "window.nmd = { getElementsByTagName: () => [{ value: currentToken }] };\n"
                "const navigator = { userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36', onLine: true, language: 'en-US', languages: ['en-US','en'], cookieEnabled: true, hardwareConcurrency: 8, maxTouchPoints: 0, platform: 'Win32' };\n"
                "const CSS = { supports: () => true };\n"
                "const screen = { width: 1920, height: 1080, colorDepth: 24, pixelDepth: 24, availWidth: 1920, availHeight: 1040 };\n"
                "const localStorage = {};\n"
                "const sessionStorage = {};\n"
                "const _origCreateElement = document.createElement.bind(document);\n"
                "document.createElement = function(tag) {\n"
                "  const el = _origCreateElement(tag);\n"
                "  if (tag === 'canvas') {\n"
                "    let _fillStyle = '';\n"
                "    el.getContext = () => ({\n"
                "      set fillStyle(v) { _fillStyle = v; },\n"
                "      get fillStyle() { return _fillStyle; },\n"
                "      fillRect: () => {},\n"
                "      getImageData: () => {\n"
                "        const m = _fillStyle.match(/\\d+/g) || ['0','0','0'];\n"
                "        return { data: [+m[0], +m[1], +m[2], 255] };\n"
                "      }\n"
                "    });\n"
                "  }\n"
                "  el.getBoundingClientRect = () => {\n"
                "    const w = parseFloat(el.style.width) || 0;\n"
                "    const h = parseFloat(el.style.height) || 0;\n"
                "    return { x: 0, y: 0, top: 0, left: 0, bottom: h, right: w, width: w, height: h };\n"
                "  };\n"
                "  return el;\n"
                "};\n"
                "window.getComputedStyle = (el) => el.style;\n"
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
                raise RuntimeError(f"verification failed: {r3}")

            elapsed = round(time.time() - start, 1)
            submitted = False

            if name:
                form_resp = s.post(f"{base_url}{form_path}submit/", data={"name": name, "vibecheck-result-token": new_token}, headers={"Referer": referer, "Origin": base_url})
                submitted = "Captcha verified" in form_resp.text or "Submission Received" in form_resp.text

            return {"token": new_token, "time": elapsed, "submitted": submitted}

        except RuntimeError as e:
            if attempt == retries:
                raise
            continue

    raise RuntimeError("all retries exhausted")



def menu():
    print(f"  {Fore.WHITE}{Style.BRIGHT}[{Fore.CYAN}1{Fore.WHITE}]{Style.RESET_ALL} Solve")
    print(f"  {Fore.WHITE}{Style.BRIGHT}[{Fore.CYAN}2{Fore.WHITE}]{Style.RESET_ALL} Solve Rate Test")
    print(f"  {Fore.WHITE}{Style.BRIGHT}[{Fore.CYAN}3{Fore.WHITE}]{Style.RESET_ALL} Exit")
    print()


def run_solve():
    url = input(f"  {Fore.YELLOW}URL {Fore.WHITE}{Style.DIM}(enter for default){Style.RESET_ALL}: ").strip()
    if not url:
        url = "https://vibecheck.petar.petrushev.u.is-my.space"
    path = input(f"  {Fore.YELLOW}Form path {Fore.WHITE}{Style.DIM}(enter for /demo/){Style.RESET_ALL}: ").strip()
    if not path:
        path = "/demo/"
    name = input(f"  {Fore.YELLOW}Name {Fore.WHITE}{Style.DIM}(enter to skip submission){Style.RESET_ALL}: ").strip() or None

    print()
    try:
        result = solve(url, path, name)
        tok_short = result["token"][:40] + "..."
        print(f"  {Fore.GREEN}{Style.BRIGHT}VibeCheck{Style.RESET_ALL} {Fore.WHITE}({Fore.GREEN}Solved: {result['time']}s{Fore.WHITE}) ({Fore.CYAN}Token: {tok_short}{Fore.WHITE}){Style.RESET_ALL}")
        if name and result["submitted"]:
            print(f"  {Fore.GREEN}Submitted as '{name}'{Style.RESET_ALL}")
        elif name:
            print(f"  {Fore.RED}Form submission failed{Style.RESET_ALL}")
    except Exception as e:
        print(f"  {Fore.RED}{Style.BRIGHT}Failed:{Style.RESET_ALL} {Fore.RED}{e}{Style.RESET_ALL}")
    print()

# solve rate test ig
def run_rate_test():
    url = input(f"  {Fore.YELLOW}URL {Fore.WHITE}{Style.DIM}(enter for default){Style.RESET_ALL}: ").strip()
    if not url:
        url = "https://vibecheck.petar.petrushev.u.is-my.space"
    path = input(f"  {Fore.YELLOW}Form path {Fore.WHITE}{Style.DIM}(enter for /demo/){Style.RESET_ALL}: ").strip()
    if not path:
        path = "/demo/"

    print()
    passes = 0
    fails = 0
    reasons = {}

    for i in range(1, 21):
        try:
            result = solve(url, path, retries=1)
            passes += 1
            print(f"  {Fore.WHITE}[{i:2d}/20]  {Fore.GREEN}{Style.BRIGHT}PASS{Style.RESET_ALL}  {Fore.WHITE}{Style.DIM}{result['time']}s{Style.RESET_ALL}")
        except Exception as e:
            fails += 1
            reason = str(e).split(":")[0].strip()
            reasons[reason] = reasons.get(reason, 0) + 1
            print(f"  {Fore.WHITE}[{i:2d}/20]  {Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL}  {Fore.RED}{Style.DIM}{e}{Style.RESET_ALL}")

    pct = round((passes / 20) * 100)
    color = Fore.GREEN if pct >= 80 else Fore.YELLOW if pct >= 50 else Fore.RED

    print()
    print(f"  {Fore.WHITE}{Style.BRIGHT}{'=' * 40}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}{Style.BRIGHT}Pass Rate: {color}{passes}/20 ({pct}%){Style.RESET_ALL}")
    if reasons:
        print(f"  {Fore.WHITE}{Style.BRIGHT}Failures:{Style.RESET_ALL}")
        for reason, count in reasons.items():
            print(f"    {Fore.RED}- {reason}: {count}{Style.RESET_ALL}")
    print()


if __name__ == "__main__":
    while True:
        try:
            menu()
            choice = input(f"  {Fore.CYAN}{Style.BRIGHT}>{Style.RESET_ALL} ").strip()
            if choice == "1":
                run_solve()
            elif choice == "2":
                run_rate_test()
            elif choice == "3":
                print(f"\n  {Fore.MAGENTA}bye{Style.RESET_ALL}\n")
                break
            else:
                print(f"  {Fore.RED}invalid option{Style.RESET_ALL}\n")
        except KeyboardInterrupt:
            print(f"\n\n  {Fore.MAGENTA}bye{Style.RESET_ALL}\n")
            break
