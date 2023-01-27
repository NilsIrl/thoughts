<script lang="ts">
    import { minimalSetup, EditorView } from "codemirror";
    import { EditorState } from "@codemirror/state";
    import { markdown } from "@codemirror/lang-markdown";
    import { autocompletion, completeFromList } from "@codemirror/autocomplete";

    import Carousel from "./carousel.svelte";
    import { element } from "svelte/internal";

    let carousels = [];

    let parsedImages = {};
    const imRe = /\[\[(.*?)\]\]/g;

    let all_users = fetch(`/api/users`)
        .then((response) => response.json())
        .then((json_response) => json_response.map((email) => "@" + email));

    const images = document.getElementById("images");
    let button = document.getElementById("loading");
    let lastProc = Date.now();

    const initialState = EditorState.create({
        doc: "",
        extensions: [
            minimalSetup,
            markdown(),
            EditorView.lineWrapping,
            EditorView.updateListener.of((update) => {
                if (update.docChanged) {
                    lastProc = Date.now();
                    let sel = update.state.selection.main.from;
                    let newCont = update.state.doc.toString(); // hacky
                    for (let i = sel; i < newCont.length - 1; i += 2) {
                        if (newCont[i] == "[" && newCont[i + 1] == "[") {
                            break;
                        }
                        if (newCont[i] == "]" && newCont[i + 1] == "]") {
                            return;
                        }
                    }
                    let generations = newCont.match(imRe);
                    if (!generations) return;
                    carousels = generations.map((gen) => ({prompt: gen.slice(2, -2), selected_url: ''}));
                }
            }),
            autocompletion({
                override: [
                    async (context) =>
                        completeFromList(await all_users)(context),
                ],
            }),
        ],
    });

    const view = new EditorView({
        parent: document.getElementById("editor"),
        state: initialState,
        doc: "",
    });


    const timer = setInterval(() => {
            view.focus();
            if(view.hasFocus) clearInterval(timer);
        }, 200);
    let submit = document.getElementById("submit");
    submit.addEventListener("click", async () => {
        console.log(carousels);
        let doc = view.state.doc.toString();
        let generations = doc.replace(imRe, (match) => `![](${carousels.find(element => element.prompt == match.slice(2, -2)).selected_url})`);

        let resp = await fetch("/api/posts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                content: generations,
            }),
        });
        if (resp.ok) {
            window.location.href = `/`;
        }
    });
</script>

<div>
    {#each carousels as carousel}
        <Carousel bind:selected_url={carousel.selected_url} prompt={carousel.prompt} />
    {/each}
</div>

<style>
    div {
        display: flex;
        flex-direction: column;
    }
</style>