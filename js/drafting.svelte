<script lang="ts">
    // TODO: we can do custom completion for usernames
    // https://codemirror.net/try/?example=Custom%20completions

    //import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
    import { minimalSetup } from "codemirror";
    import { EditorState } from "@codemirror/state";
    import { EditorView, keymap } from "@codemirror/view";
    import { defaultKeymap } from "@codemirror/commands";
    import { markdown } from "@codemirror/lang-markdown";

    let parsedImages = {"@nils@nilsand.re eating a biscuit": 0}
    const imRe = /\[\[(.*?)\]\]/g;
    const imRe2 = /\[\[(.*)\]\]/;

    const images = document.getElementById("images");
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
              let current = view.state.doc.toString().indexOf(key);
              let subDiv = document.createElement("div");
              json.urls.forEach((url) => {
                let img = document.createElement("img");
                img.src = url;
                subDiv.appendChild(img);
                img.addEventListener("click", (e) => {
                  let pos = view.state.doc.toString().indexOf(key);
                  let tr = view.state.update({
                    changes: {
                      from: pos,
                      to: pos + key.length + 2,
                      insert: `\n![${key}](${url})\n`,
                    },
                  });
                  view.dispatch(tr);
                  subDiv.children.forEach((otherImg) => {
                    if (otherImg != img) {
                        otherImg.remove();
                    }
                  })
                });
                images.appendChild(subDiv);
              })
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
                if (update.docChanged && Date.now() - lastProc > 1000) {
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
                        if (!(genName in parsedImages)) {
                          parsedImages[genName] = 0;
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


    let submit = document.getElementById("submit");
    let input = document.getElementById("post-content");
    submit.addEventListener("click", async () => {
        let cmv = view.state.doc.toString();
        let resp = await fetch("/api/posts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                content: cmv,
            }),
        });
        if (resp.ok) {
            window.location.href = `/`;
        }
    });
</script>
<!-- <div id="editor"></div> -->
