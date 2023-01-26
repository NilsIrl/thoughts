<script lang="ts">
    // TODO: we can do custom completion for usernames
    // https://codemirror.net/try/?example=Custom%20completions

    //import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
    import { minimalSetup } from "codemirror";
    import { EditorState } from "@codemirror/state";
    import { EditorView, keymap } from "@codemirror/view";
    import { defaultKeymap } from "@codemirror/commands";
    import { markdown } from "@codemirror/lang-markdown";

    let parsedImages = {}
    const imRe = /\[\[.*\]\]/g;
    const imRe2 = /\[\[(.*)\]\]/;

    const imagesDiv = document.getElementById("images");
    async function getImages() {
      setTimeout(getImages, 10000);
      console.log(parsedImages);
      for (var key in parsedImages) {
        if (!parsedImages[key]) {
          let resp = await fetch(`/api/images?prompt=${encodeURIComponent(key)}`)
          if (resp.ok) {
            let json = await resp.json();
            if (json.success)
            {
              parsedImages[key] = 1;
              json.urls.forEach((url) => {
                imagesDiv.innerHTML += `<img src="${url}" />`;
              }
             }
          }
        }
      }
    }
    getImages();
    let lastProc = Date.now()
    const initialState = EditorState.create({
        doc: '',
        extensions: [
            minimalSetup,
            markdown(),
            EditorView.updateListener.of((update) => {
                if (update.docChanged && Date.now() - lastProc > 5000) {
                    lastProc = Date.now();
                    let sel = update.state.selection.main.from;
                    let newCont = update.state.doc.toString(); // hacky
                    for (let i = sel; i < newCont.length-1; i += 2) {
                        if (newCont[i] == '[' && newCont[i+1] == '[') {
                            break;
                        }
                        if (newCont[i] == ']' && newCont[i+1] == ']') {
                            return;
                        }
                    }
                    let generations = newCont.match(imRe);
                    if (!generations) return;
                    generations.forEach(async (gen) => {
                        let genName = gen.slice(2, -2);
                        parsedImages[genName] = 0;
                        if (!(genName in parsedImages)) {
                          let resp = await fetch(`/api/images?prompt=${encodeURIComponent(genName)}`, {
                            method: 'POST',
                          })
                          if (!(resp.ok)) {
                            console.log("Error fetching image");
                          }
                        }
                    });

                }
            }),
        ]
    });

    const view = new EditorView({
        parent: document.getElementById("editor"),
        state: initialState,
        doc: '',
    });

    console.log("WTF");
</script>
<!-- <div id="editor"></div> -->
