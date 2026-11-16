import * as fs from 'node:fs';
import * as path from 'node:path';

async function main() {
  const src = path.join(import.meta.dirname || '.', 'entry.png');
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
  
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const dest = path.join(outDir, 'entry.png');
  fs.copyFileSync(src, dest);
  console.log(`Copied ${src} to ${dest}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
