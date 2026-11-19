import { existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ADDRESS = /\b(?:https?|wss?):\/\/[^\s"<>`]*/gi;
const LINK_VALUE = /^(\s*-?\s*\/url:\s*"?)([^?#"\s]*)[?#][^"\s]*/gm;

function withoutQuery(address) {
  const cut = address.search(/[?#]/);
  if (cut < 0) {
    return address;
  }
  const tail = address.slice(cut);
  const trailing = /[)\]']*$/.exec(tail)[0];
  let surplus = (tail.match(/[)\]]/g) ?? []).length - (tail.match(/[([]/g) ?? []).length;
  let quoteOpen = (address.match(/'/g) ?? []).length % 2 === 1;
  let keep = 0;
  for (let i = trailing.length - 1; i >= 0; i -= 1) {
    if (trailing[i] === "'" && quoteOpen) {
      quoteOpen = false;
    } else if (trailing[i] !== "'" && surplus > 0) {
      surplus -= 1;
    } else {
      break;
    }
    keep += 1;
  }
  return address.slice(0, cut) + trailing.slice(trailing.length - keep);
}

export function cutQueries(text) {
  return text.replace(ADDRESS, withoutQuery).replace(LINK_VALUE, '$1$2');
}

export function cleanCliFolder(runFolder) {
  const cliFolder = join(runFolder, '.playwright-cli');
  if (!existsSync(cliFolder)) {
    return;
  }
  for (const entry of readdirSync(cliFolder, { recursive: true, withFileTypes: true })) {
    if (!entry.isFile()) {
      continue;
    }
    const file = join(entry.parentPath, entry.name);
    if (/^console-.*\.log$/i.test(entry.name)) {
      rmSync(file, { force: true });
      continue;
    }
    if (!/\.(log|yml|yaml|md|txt|json)$/i.test(entry.name)) {
      continue;
    }
    const text = readFileSync(file, 'utf8');
    const cut = cutQueries(text);
    if (cut !== text) {
      writeFileSync(file, cut);
    }
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [runFolder] = process.argv.slice(2);
  if (!runFolder) {
    console.error('verify redact: usage: node redact.mjs <run folder>');
    process.exit(2);
  }
  cleanCliFolder(runFolder);
}
