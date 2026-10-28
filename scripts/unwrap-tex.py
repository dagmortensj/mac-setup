#!/usr/bin/env python3
"""Slår sammen hardt brukne tekstlinjer i .tex-filer til ett avsnitt per linje.

Bruk:  python3 unwrap-tex.py fil.tex [flere.tex ...]

Filene skrives om på stedet. PDF-en blir identisk: inne i et avsnitt er et
linjeskift bare et mellomrom for LaTeX. Skriptet rører ikke
  - kommentarlinjer og linjer med %-kommentar på slutten
  - linjer som slutter med \\\\ (tvunget linjeskift)
  - preamblen (alt før \\begin{document})
  - linjer som begynner med en strukturkommando (\\section, \\begin, \\label, ...)
  - linjer som slutter med \\newline, \\par, \\vspace{...} o.l.
  - matematikk-, kode-, tabell- og tikz-miljøer, \\[ ... \\] og $$ ... $$
"""
import re
import sys

SKIP_ENVS = re.compile(
    r'(equation|align|alignat|gather|multline|flalign|eqnarray|split|cases|'
    r'[pbBvV]?matrix|smallmatrix|array|tabular[x*]?|longtable|tikzpicture|axis|'
    r'verbatim|Verbatim|lstlisting|minted|python|comment|filecontents)\*?$'
)
# Kommandoer som kan stå først i en tekstlinje uten å være struktur
INLINE = re.compile(
    r'\\(emph|textbf|textit|texttt|textsc|textsf|textrm|underline|ref|eqref|autoref|'
    r'cref|Cref|pageref|cite|citep|citet|footnote|SI|si|qty|num|unit|vv|enquote|'
    r'mbox|url|href|ldots|dots|LaTeX|TeX|ie|eg|,|\(|&|%|\$|_)(?![A-Za-z])'
)

def unescaped_percent(line):
    return re.search(r'(?<!\\)%', line) is not None

def starts_structural(stripped):
    return stripped.startswith('\\') and not INLINE.match(stripped) and not stripped.startswith('\\item')

def can_continue(stripped):
    """Kan denne linjen hektes på linjen over?"""
    if not stripped or stripped.startswith('%'):
        return False
    if stripped.startswith('$$') or re.search(r'(?<!\\)&', stripped):
        return False
    if stripped.startswith('\\'):
        return INLINE.match(stripped) is not None
    return re.match(r'[0-9A-Za-zÆØÅæøåÄÖÜäöüÉé(«"\'`$\-–—.,;:!?]', stripped) is not None

def can_take_more(line):
    """Kan linjen under hektes på denne?"""
    s = line.strip()
    if not s or s.startswith('%') or unescaped_percent(line):
        return False
    if re.search(r'\\\\(\[[^\]]*\])?\s*$', line):
        return False
    if re.search(r'\\(newline|linebreak|par|newpage|pagebreak|clearpage|smallskip|medskip|bigskip|noindent|hfill|vfill)\s*$', line):
        return False
    if re.search(r'\\[vh]space\*?\{[^}]*\}\s*$', line):
        return False
    if s[0] in '{}[]&' or re.search(r'(?<!\\)&', line):
        return False
    if starts_structural(s):
        return False
    return True

def unwrap(text):
    lines = text.split('\n')
    out, skip_env, in_display = [], [], False
    joined = 0
    # Preamblen røres ikke. Filer uten \begin{document} (\input-deler) behandles i sin helhet.
    in_body = not any(re.match(r'\s*\\begin\{document\}', l) for l in lines)
    for line in lines:
        s = line.strip()
        if not in_body:
            out.append(line)
            if re.match(r'\s*\\begin\{document\}', line):
                in_body = True
            continue
        # Hold rede på miljøer der linjeskift skal stå
        for m in re.finditer(r'\\(begin|end)\{([^}]*)\}', line):
            kind, env = m.groups()
            if SKIP_ENVS.match(env):
                if kind == 'begin':
                    skip_env.append(env)
                elif skip_env:
                    skip_env.pop()
        opens = len(re.findall(r'(?<!\\)\\\[', line)) + line.count('$$')
        closes = len(re.findall(r'(?<!\\)\\\]', line))
        protected = bool(skip_env) or in_display or '\\begin{' in line or '\\end{' in line
        if '$$' in line:
            in_display = (line.count('$$') % 2 == 1) != in_display
        elif opens > closes:
            in_display = True
        elif closes > opens:
            in_display = False
            protected = True

        if (out and not protected and can_continue(s) and can_take_more(out[-1])
                and not out[-1].rstrip().endswith('$$') and not re.search(r'\\\]\s*$', out[-1])):
            out[-1] = out[-1].rstrip() + ' ' + s
            joined += 1
        else:
            out.append(line)
    return '\n'.join(out), joined

def main(paths):
    if not paths:
        print(__doc__.strip()); return 1
    for p in paths:
        with open(p, encoding='utf-8') as f:
            old = f.read()
        new, n = unwrap(old)
        if n:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new)
        print(f'OK: {p} ({n} linjer slått sammen)')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
