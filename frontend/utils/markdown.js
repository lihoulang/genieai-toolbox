const escapeHtml = (value = '') => value
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const escapeAttribute = (value = '') => escapeHtml(value).replace(/`/g, '&#96;');

const sanitizeUrl = (url = '') => {
  const normalized = url.trim();
  if (/^(https?:\/\/|mailto:)/i.test(normalized)) return normalized;
  return '#';
};

const applyCodeSpans = (text, slots) => text.replace(/`([^`\n]+)`/g, (_, code) => {
  const key = `__CODE_SPAN_${slots.length}__`;
  slots.push(`<code style="padding:2px 6px;border-radius:6px;background:#eef2f7;color:#243042;font-family:Consolas,monospace;font-size:12px;">${escapeHtml(code)}</code>`);
  return key;
});

const restoreCodeSpans = (text, slots) => text.replace(/__CODE_SPAN_(\d+)__/g, (_, index) => slots[Number(index)] || '');

const renderInline = (input = '') => {
  const codeSlots = [];
  let text = applyCodeSpans(input, codeSlots);
  text = escapeHtml(text);
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, url) => {
    const safeUrl = escapeAttribute(sanitizeUrl(url));
    return `<a href="${safeUrl}" style="color:#4f63d8;text-decoration:none;">${label}</a>`;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  text = text.replace(/(^|[^*])\*([^*\n]+)\*([^*]|$)/g, '$1<em>$2</em>$3');
  text = text.replace(/(^|[^_])_([^_\n]+)_([^_]|$)/g, '$1<em>$2</em>$3');
  text = text.replace(/~~([^~]+)~~/g, '<del>$1</del>');
  return restoreCodeSpans(text, codeSlots);
};

const renderCodeBlock = (language, code) => {
  const safeLang = escapeHtml(language || 'text');
  const formatted = escapeHtml(code || '').replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;');
  return `<div style="background:#1f2430;border-radius:10px;margin:10px 0;overflow:hidden;">
    <div style="padding:8px 12px;background:#2d3342;color:#b7bfcd;font-size:12px;">${safeLang}</div>
    <div style="padding:12px 14px;color:#edf1f7;font-family:Consolas,monospace;font-size:13px;line-height:1.7;">${formatted}</div>
  </div>`;
};

const isTableSeparator = (line = '') => /^\s*\|?[\s:-]+(?:\|[\s:-]+)+\|?\s*$/.test(line);

const parseTableRow = (line = '') => line
  .trim()
  .replace(/^\|/, '')
  .replace(/\|$/, '')
  .split('|')
  .map((cell) => cell.trim());

const renderTable = (lines) => {
  const header = parseTableRow(lines[0]);
  const rows = lines.slice(2).map(parseTableRow);
  const headHtml = header
    .map((cell) => `<th style="border:1px solid #ebeef5;padding:8px;background:#f6f7fb;text-align:left;">${renderInline(cell)}</th>`)
    .join('');
  const bodyHtml = rows
    .map((row) => `<tr>${row.map((cell) => `<td style="border:1px solid #ebeef5;padding:8px;">${renderInline(cell)}</td>`).join('')}</tr>`)
    .join('');
  return `<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:13px;"><thead><tr>${headHtml}</tr></thead><tbody>${bodyHtml}</tbody></table>`;
};

const renderList = (lines, ordered) => {
  const tag = ordered ? 'ol' : 'ul';
  const items = lines
    .map((line) => line.replace(ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/, ''))
    .map((item) => `<li style="margin:6px 0;">${renderInline(item)}</li>`)
    .join('');
  return `<${tag} style="margin:10px 0;padding-left:22px;">${items}</${tag}>`;
};

const renderBlockquote = (lines) => {
  const content = lines
    .map((line) => line.replace(/^\s*>\s?/, ''))
    .map((line) => renderInline(line))
    .join('<br/>');
  return `<blockquote style="margin:10px 0;padding:8px 12px;border-left:3px solid #d6dceb;background:#f7f9fc;color:#536074;">${content}</blockquote>`;
};

const renderParagraph = (lines) => {
  if (!lines.length) return '';
  return `<p style="margin:10px 0;line-height:1.75;">${lines.map((line) => renderInline(line)).join('<br/>')}</p>`;
};

export const renderMarkdown = (input = '') => {
  const text = String(input)
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .trim();

  if (!text) return '';

  const lines = text.split('\n');
  const html = [];
  let paragraph = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    html.push(renderParagraph(paragraph));
    paragraph = [];
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      flushParagraph();
      continue;
    }

    const fenceMatch = line.match(/^(```|~~~)\s*([^`]*)$/);
    if (fenceMatch) {
      flushParagraph();
      const fence = fenceMatch[1];
      const language = fenceMatch[2].trim();
      const codeLines = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith(fence)) {
        codeLines.push(lines[i]);
        i += 1;
      }
      html.push(renderCodeBlock(language, codeLines.join('\n')));
      continue;
    }

    if (i + 1 < lines.length && line.includes('|') && isTableSeparator(lines[i + 1])) {
      flushParagraph();
      const tableLines = [line, lines[i + 1]];
      i += 2;
      while (i < lines.length && lines[i].includes('|') && lines[i].trim()) {
        tableLines.push(lines[i]);
        i += 1;
      }
      i -= 1;
      html.push(renderTable(tableLines));
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      const level = headingMatch[1].length;
      html.push(`<h${level} style="margin:12px 0 8px;font-size:${28 - level * 2}px;line-height:1.4;">${renderInline(headingMatch[2].trim())}</h${level}>`);
      continue;
    }

    if (/^\s*>\s?/.test(line)) {
      flushParagraph();
      const blockquoteLines = [line];
      while (i + 1 < lines.length && /^\s*>\s?/.test(lines[i + 1])) {
        blockquoteLines.push(lines[i + 1]);
        i += 1;
      }
      html.push(renderBlockquote(blockquoteLines));
      continue;
    }

    if (/^\s*[-*+]\s+/.test(line)) {
      flushParagraph();
      const listLines = [line];
      while (i + 1 < lines.length && /^\s*[-*+]\s+/.test(lines[i + 1])) {
        listLines.push(lines[i + 1]);
        i += 1;
      }
      html.push(renderList(listLines, false));
      continue;
    }

    if (/^\s*\d+[.)]\s+/.test(line)) {
      flushParagraph();
      const listLines = [line];
      while (i + 1 < lines.length && /^\s*\d+[.)]\s+/.test(lines[i + 1])) {
        listLines.push(lines[i + 1]);
        i += 1;
      }
      html.push(renderList(listLines, true));
      continue;
    }

    paragraph.push(line);
  }

  flushParagraph();
  return html.join('');
};
