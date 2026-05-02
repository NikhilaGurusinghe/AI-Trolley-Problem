# P5.js Template

P5.js project template with Bun, TypeScript and Biome (linter) set up.

Based on the new project created by the [p5.vscode](https://marketplace.visualstudio.com/items?itemName=samplavigne.p5-vscode) Visual Studio
Code extension.

## Setup

Copy this repository to a new folder.

```bash
bun install
```

## Developing

Start development server:

```bash
bun run watch
```

Open `index.html` with a Web server (Right click `index.html` -> "Open with Live Server" for VS Code).

The entry point is `src/index.ts`.

# Building

```bash
bun run build
```

The output will be written to `dist/index.js`. See `index.html` for how the
bundled script is loaded.
