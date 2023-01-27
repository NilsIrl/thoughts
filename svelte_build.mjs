import esbuild from "esbuild";
import sveltePlugin from "esbuild-svelte";

esbuild.build({
  entryPoints: ["js/drafting.js"],
  mainFields: ["svelte", "browser", "module", "main"],
  bundle: true,
  outdir: "hackathon/static/js",
  plugins: [sveltePlugin()],
  logLevel: "info",
  minify: true,
})
  .catch(() => process.exit(1))
