import esbuild from "esbuild";
import sveltePlugin from "esbuild-svelte";

esbuild.build({
  entryPoints: ["js/app.js"],
  mainFields: ["svelte", "browser", "module", "main"],
  bundle: true,
  outdir: "hackathon/static/js",
  plugins: [sveltePlugin()],
  logLevel: "info",
})
  .catch(() => process.exit(1))