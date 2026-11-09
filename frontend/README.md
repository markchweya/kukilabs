# Kuki web app

React 19 + TypeScript + Vite + Tailwind CSS v4. Talks only to the local Kuki API.

```bash
npm install
npm run dev      # http://localhost:5173, proxies /api to http://127.0.0.1:8765 (override with KUKI_API)
npm run build    # outputs dist/, which the backend serves at /
npx eslint .
```

## Structure

```
src/
  api/          typed client: one function per endpoint, types mirror the backend
  components/   AppShell, DropZone, sources (citations + drawer), ReviewSession, …
  pages/        Library, Document (+ doc/ tabs), Review, Progress, Courses
  lib/          data hook, formatting, SM-2 preview, misconception labels
  index.css     design tokens (light + dark), fonts, the "stitch" motif
```

## Design notes

* Palette from the whale mascot: ink navy, whale blue, belly cream for quoted
  sources, sea teal for understanding, blush for misconceptions.
* Bricolage Grotesque for headings, Atkinson Hyperlegible for reading.
* The dashed **stitch** marks content sewn to the student's own material
  (citations, quoted sources, flipped flashcards). Uncited content is never stitched.
* One ambient animation (the whale bobbing while the model works), disabled
  under `prefers-reduced-motion`.
* Keyboard: Space flips a flashcard and 1-4 rate it; Ctrl+Enter checks a quiz
  answer; Escape closes the source drawer.
