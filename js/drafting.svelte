<script lang="ts">
    //import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
    import { basicSetup } from "codemirror";
    import { EditorState } from "@codemirror/state";
    import { EditorView, keymap } from "@codemirror/view";
    import { defaultKeymap } from "@codemirror/commands";
    import { markdown } from "@codemirror/lang-markdown";

    let parsedImages = {}
    const imRe = /\[\[.*\]\]/g;
    const imRe2 = /\[\[(.*)\]\]/;

    const imagesDiv = document.getElementById("images");
    function async getImages() {
      setTimeout(getImages, 60000);
      for (var key in parsedImages) {
        if (!parsedImages[key]) {
          let resp = await fetch(`/api/images?prompt=${encodeURIComponent(key)}`)
          if (resp.ok) {
            let url = (await resp.json())[0];
            parsedImages[key] = 1;
            imagesDiv.innerHTML += `<img src="${url}" />`;
          }
        }
      }
    }
    const initialState = EditorState.create({
        doc: '',
        extensions: [
            basicSetup,
            markdown().
            EditorView.updateListener.of(async (update) => {
                if (update.docChanged) {
                    let newCont = update.state.doc.toString());
                    let generations = newCont.match(imRe);
                    generations.forEach((gen) => {
                        let genName = gen.slice(2, -2);
                        if (!(genName in parsedImages)) {
                          let resp = await fetch(`/api/images?prompt=${encodeURIComponent(genName)}`, {
                            method: 'POST',
                          })
                          parsedImages[genName] = 0;
                          if (resp.ok) {
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
    });

    console.log("WTF");
</script>