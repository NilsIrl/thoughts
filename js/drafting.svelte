<script lang="ts">
    //import { basicSetup, EditorState, EditorView } from "@codemirror/basic-setup";
    import { basicSetup } from "codemirror";
    import { EditorState } from "@codemirror/state";
    import { EditorView, keymap } from "@codemirror/view";
    import { defaultKeymap } from "@codemirror/commands";
    import { markdown } from "@codemirror/lang-markdown";

    const initialState = EditorState.create({
        doc: '',
        extensions: [
            basicSetup,
            markdown()
        ]
    });

    const view = new EditorView({
        parent: document.getElementById("editor"),
        state: initialState,
    });

    console.log("WTF");
</script>
