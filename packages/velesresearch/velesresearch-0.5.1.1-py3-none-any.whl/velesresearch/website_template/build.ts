import { build } from 'esbuild';
const { style } = require("@hyrious/esbuild-plugin-style");

async function buildMain() {
    await build({
        entryPoints: ['./src/index.tsx'],
        bundle: true,
        minify: true,
        outfile: "./build/main.js",
        plugins: [style()],
    });
    console.log("Build complete");
};

export default buildMain;

buildMain();