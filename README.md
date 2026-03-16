# VibeCheck CAPTCHA Solver

a solver to complelety fuck vibecheck



---

## How VibeCheck Works 


### The Loader

A page that uses vibecheck will have this in there code

```html
<script src="https://com.com/api/genjs/" async defer></script>
<div class="vibecheck-result"></div>
```

That `/api/genjs/` endpoint thingy is the captchas javascripts that like injects into the page 

### Token Generation

The genjs script injects a input into the `.vibecheck-result` div:
 for example this 
```javascript
window.md.innerHTML = `<input type='hidden'
  value='nct.8b6162c8ae7790fd6a1e8f8b179c15b5bb602ee000b291...'
  name='vibecheck-result-token' />`;
```

does a request to  `/api/eh/`:

```javascript
const payload = {
    "e": -6627,  // changes every few minutes on there serevr
    "ed": btoa(JSON.stringify({
        "mft": "nct.8b6162c8...",  // the token it just created
        "a": "atavoart"            // action identifier
    }))
};
```

**reversed:** The `e` value is a integer that rotates The `ed` field is just base64 JSON with the token and a static action string We extract both with regex + Node.js emluation

### Token swap method

The server responds with executable JS in the `cte` field:
 example
```json
{
  "ag": true,
  "se": true,
  "cte": "window.md.getElementsByTagName('input')[0].value='2f66db535ba2...';window.nmd=md;window.md=undefined;globalThis.window.self.window.smt('WgmTVQdYcyTQ...');"
}
```

This does 3 things:
1. **Replaces** the token in the hidden input with a new one (`2f66db...`)
2. **Keeps** the DOM reference in `window.nmd`
3. **Calls `smt(ts)`** with a challenge string `ts`

**reversed:** We regex out the new token and use Node.js to properly unescape the `ts` value (which contains base64 with `\/` JS escapes).

### smt() call

The `smt` function (defined in genjs) computes a second `e` value using ass obfuscation:

```javascript
"e": -6627 + (((
    +(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])  // "9"
    +(+!![]+[])  // + "1"
    +(+!![]+[])  // + "1"
    +(+!![]+[])  // + "1"  ... (9 more times)
) - (-1*-90000000990)
  - (-80888888888)
  + (1*8*82+332+5) - 3
) * (~[].length)) * -1 * 5
```
which retunrs -5

**Deobfuscation breakdown**

| Expression | Result | Why |
|---|---|---|
| `!+[]` | `true` | `+[]` = 0, `!0` = true |
| `!![]` | `true` | `![]` = false, `!false` = true |
| `true+true+...` (×9) | `9` | boolean addition |
| `9 + []` | `"9"` | array coerces to `""` |
| `+(+!![]+[])` | concatenates `"1"` | builds the string `"9111111111"` |
| Full numeric expression | evaluates to `0` or `-5` | carefully balanced to produce a small offset |
| `~[].length` | `-1` | bitwise NOT of 0 |

The whole thing evaluates to `base_e - 5` (e.g., `-6627 + (-5) = -6632`)

**What we reversed:** We don't bother deobfuscating manually — we extract the raw expression with regex and `eval()` it in Node.js. Works regardless of how they change the obfuscation.

### Some fingerprint thing i think

The second POST returns an `ett` field containing a fingerprint collection script

```javascript
window.mfrr = [];

window.jcr = (function(){
    try {
        return [][[]]+[] === "undefined"  // [][undefined] = undefined, + [] = "undefined"
            && !+[]+[] === "true"         // !0 + [] = "true"
    } catch(e) { return false }
})();

window.mfrr.push(ts + window.jcr);          // challenge_string + "true"

String.prototype.vc = () => '95879';         // override .vc() on ALL strings
window.mfrr.push(navigator.userAgent.vc() + ts);  // "95879" + challenge_string
window.mfrr.push(navigator.userAgent.vc() + ts);  // same thing again

postData(url, {
    'e': 95879,
    'ed': btoa(JSON.stringify({
        'mft': current_token,
        'mrd': JSON.stringify(window.mfrr)  // the "fingerprints"
    }))
});
```

**reversed:** The "fingerprint" is fake 
`navigator.userAgent.vc()` return a fixed string instead of the actual user agent. The `e` value and `vc()` return value change per-session but we extract them dynamically from the `ett` code.

### Verification

The final POST returns:

```json
{"ag": true, "passed": true}
```

The token in the hidden input is now verified Form submission with this token succeeds now


## Architecture

```
┌─────────────┐     GET /api/genjs/      ┌──────────────┐
│   solver.py  │ ──────────────────────→  │   VibeCheck   │
│              │  ← JS with token + e     │    Server     │
│              │                          │              │
│  ┌────────┐  │     POST /api/eh/        │              │
│  │Node.js │  │ ──────────────────────→  │  Step 1:     │
│  │sandbox │  │  ← cte (new token + ts)  │  Token swap  │
│  └────────┘  │                          │              │
│   ↑ eval()   │     POST /api/eh/        │              │
│   │ dynamic  │ ──────────────────────→  │  Step 2:     │
│   │ JS code  │  ← ett (challenge JS)    │  Challenge   │
│              │                          │              │
│              │     POST /api/eh/        │              │
│              │ ──────────────────────→  │  Step 3:     │
│              │  ← {passed: true}        │  Verify      │
│              │                          │              │
│              │     POST /submit/        │              │
│              │ ──────────────────────→  │  ✅ Done      │
└─────────────┘                          └──────────────┘
```

---

## Usage

### Requirements

- Python 3.7+
- `requests` (`pip install requests`)
- Node.js (for sandboxed JS eval)

### Run

```bash
python solver.py

# custom input just put a random name doesant matteer
python solver.py "https://vibecheck.petar.petrushev.u.is-my.space" "/demo/" "aaa"
```

### As a Library

```python
from solver import solve

# Solve and submit
solve(
    base_url="https://vibecheck.petar.petrushev.u.is-my.space",
    form_path="/demo/",
    name="John Doe"
)
```

---

## Patch Attempts

### Patch 1:


```javascript
(typeof CSS !== 'undefined' && CSS.supports('display', 'grid'))
    ? btoa(ts.substring(9, 12)) : 'e'


(typeof navigator !== 'undefined' && navigator.onLine === true)
    ? btoa(ts.substring(6, 9)) : 'f'


(typeof screen !== 'undefined' && screen.colorDepth > 0)
    ? btoa(ts.substring(3, 6)) : 'n'

(function(){return
'84830'})() === undefined ? 'y' : 'n'
```

The idea was that a Node.js sandbox `CSS`, `screen`, `navigator.onLine`, `document.body` etc so it would return the fallback values (`'e'`, `'f'`, `'n'`) instead of the real `btoa(...)` answers and the server would reject it

**How we fixed it:** we just added the values:

```python
"const navigator = { userAgent: '...', onLine: true, platform: 'Win32', ... };\n"
"const CSS = { supports: () => true };\n"
"const screen = { width: 1920, height: 1080, colorDepth: 24, ... };\n"
"const document = { body: true, ... };\n"
```
### Patch 2:

they added real DOM checks basically

```javascript
var inp = document.createElement('input');
inp.name = 'vc_test_' + Math.random();
document.body.appendChild(inp);
var found = document.getElementsByName(inp.name);
window.mfrr.push(found.length > 0 ? btoa(ts.substring(3, 6)) : 'err');
var d = document.createElement('div');
d.id = 'vc_' + Date.now();
document.body.appendChild(d);
window.mfrr.push(document.getElementById(d.id) ? btoa(ts.substring(6, 9)) : 'err');
var c = document.createElement('canvas');
var ctx = c.getContext('2d');
ctx.fillStyle = 'rgb(47, 79, 79)';
ctx.fillRect(0, 0, 1, 1);
var px = ctx.getImageData(0, 0, 1, 1).data;
window.mfrr.push(px[0] === 47 ? btoa(ts.substring(0, 3)) : 'err');
var span = document.createElement('span');
span.style.width = '100px';
document.body.appendChild(span);
var cs = window.getComputedStyle(span);
window.mfrr.push(cs ? btoa(ts.substring(9, 12)) : 'err');
var box = document.createElement('div');
box.style.width = '50px';
box.style.height = '25px';
document.body.appendChild(box);
var rect = box.getBoundingClientRect();
window.mfrr.push(rect.width > 0 ? 'y' : 'n');
```

Our old sandbox was just a shallow object mock (`const document = { body: true }`) so that bascially 

**How we fixed it:** Switched Libraies 

```python
"const { JSDOM } = require('jsdom');\n"
"const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');\n"
"const window = dom.window;\n"
"const document = window.document;\n"
"if (tag === 'canvas') {\n"
"    el.getContext = () => ({\n"
"      fillRect: () => {},\n"
"      getImageData: () => {\n"
"        const m = _fillStyle.match(/\\d+/g) || ['0','0','0'];\n"
"        return { data: [+m[0], +m[1], +m[2], 255] };\n"
"      }\n"
"    });\n"
"el.getBoundingClientRect = () => {\n"
"    const w = parseFloat(el.style.width) || 0;\n"
"    const h = parseFloat(el.style.height) || 0;\n"
"    return { x:0, y:0, top:0, left:0, bottom:h, right:w, width:w, height:h };\n"

"window.getComputedStyle = (el) => el.style;\n"
```
---
